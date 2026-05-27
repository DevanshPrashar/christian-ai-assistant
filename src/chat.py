"""
Chat module with RAG pipeline for scripture-grounded responses.
Integrates with MiniMax API for LLM responses.
"""
import os
import uuid
import re
from typing import Optional

from dotenv import load_dotenv

from src.moderation import check_input, check_output, ModerationResult
from src.retrieval import retrieve_relevant_verses, format_verse_for_context
from src.minimax_client import get_minimax_client
from src.models import ChatRequest, ChatResponse, VerseReference
from src.verse_validator import validate_response_verses, get_fake_verses, format_verse_warning
from src.tricky_scenarios import detect_adversarial_prompt, handle_weaponized_scripture_request, handle_adversarial_prompt
from prompts.system_prompts import get_system_prompt

load_dotenv()

# In-memory conversation storage
# {conversation_id: [{"role": "user"/"assistant", "content": str}]}
_conversations: dict[str, list[dict]] = {}


def is_valid_response(text: str) -> bool:
    """
    Check if response is valid and not corrupted.
    Returns False if:
    - Contains excessive repeated characters
    - Contains gibberish/encoding artifacts
    - Is too short (likely empty)
    - Contains excessive non-ASCII characters without proper context
    """
    if not text or len(text.strip()) < 20:
        return False

    # Check for repeated character patterns (encoding corruption)
    # Pattern: same character repeated 10+ times
    repeated_pattern = re.compile(r'(.)\1{9,}')
    if repeated_pattern.search(text):
        return False

    # Check for excessive Chinese characters (common encoding corruption)
    chinese_chars = re.compile(r'[一-鿿]')
    chinese_count = len(chinese_chars.findall(text))
    # If more than 5 Chinese characters AND it's > 10% of text, it's likely corrupted
    if chinese_count > 5 and chinese_count > len(text) * 0.1:
        return False

    # Check for excessive special characters (gibberish indicator)
    special_chars = re.compile(r'[^\w\s.,!?;:\'\"\-()#*]+')
    special_count = len(special_chars.findall(text))
    if special_count > len(text) * 0.3:
        return False

    # Check for gibberish patterns (consecutive random chars)
    gibberish = re.compile(r'[a-zA-Z]{30,}')
    if gibberish.search(text):
        # Check if it looks like actual words or gibberish
        words = text.split()
        if all(len(w) > 25 for w in words[:5]):
            return False

    return True


def clean_corrupted_response(response: str, max_retries: int = 3) -> tuple[str, bool]:
    """
    Attempt to clean a corrupted response or return original if not salvageable.
    Returns (cleaned_text, was_cleaned).
    """
    # If not corrupted, return as-is
    if is_valid_response(response):
        return response, False

    # Try to extract valid portion
    lines = response.split('\n')
    valid_lines = []
    corrupted_chars = ['迟迟', '呆呆', '哈哈', '啊啊', '噢噢']

    for line in lines:
        # Skip lines that are mostly corrupted
        if any(char * 10 in line for char in corrupted_chars):
            continue
        # Skip lines with excessive repeated chars
        if re.search(r'(.)\1{15,}', line):
            continue
        valid_lines.append(line)

    if valid_lines:
        cleaned = '\n'.join(valid_lines)
        if is_valid_response(cleaned):
            return cleaned, True

    # If we have retries left, return original for retry
    return response, False


def create_conversation() -> str:
    """Create a new conversation and return its ID."""
    conversation_id = str(uuid.uuid4())
    _conversations[conversation_id] = []
    return conversation_id


def get_conversation(conversation_id: str) -> list[dict]:
    """Get conversation history, or empty list if not found."""
    return _conversations.get(conversation_id, [])


def add_to_conversation(conversation_id: str, role: str, content: str):
    """Add a message to conversation history."""
    if conversation_id not in _conversations:
        _conversations[conversation_id] = []
    _conversations[conversation_id].append({
        "role": role,
        "content": content
    })


def build_context_for_query(query: str) -> str:
    """
    Build scripture context for a query.
    Returns formatted string of relevant verses.
    """
    verses = retrieve_relevant_verses(query, limit=5)

    if not verses:
        return ""

    context_parts = ["Here are relevant Bible verses that may help answer this question:"]
    for verse in verses:
        context_parts.append(format_verse_for_context(verse))

    return "\n\n".join(context_parts)


def build_minimax_messages(conversation_history: list[dict], new_message: str,
                            scripture_context: str) -> list[dict]:
    """
    Build the messages array for MiniMax API.
    Includes conversation history and new context.
    """
    messages = []

    # Add conversation history
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Check if message is off-topic (not about Christianity/Bible/faith)
    off_topic_patterns = ["llm", "what are large language", "who is", "what is the capital",
                          "science", "history", "geography", "math", "physics", "ai ", "artificial intelligence"]
    is_off_topic = any(pattern in new_message.lower() for pattern in off_topic_patterns)

    # Add the new user message with scripture context
    if scripture_context:
        enhanced_message = f"{new_message}\n\n[SCRIPTURE CONTEXT]\n{scripture_context}\n[/SCRIPTURE CONTEXT]"
    else:
        enhanced_message = new_message

    # Add explicit instruction if off-topic
    if is_off_topic:
        enhanced_message += ("\n\n[IMPORTANT: If your question is NOT about Christianity, "
                              "the Bible, faith, or spiritual matters, you MUST politely decline "
                              "and offer to help with Christian topics instead.]")

    messages.append({
        "role": "user",
        "content": enhanced_message
    })

    return messages


def extract_verse_references(text: str) -> list[VerseReference]:
    """
    Extract verse references from response text.
    Looks for patterns like "John 3:16", "Genesis 1:1", etc.
    """
    import re

    references = []
    # Pattern for book name and chapter:verse
    verse_pattern = r'([A-Za-z]+)\s+(\d+):(\d+)'
    matches = re.findall(verse_pattern, text)

    from src.bible_db import verse_exists, get_verse

    for book, chapter, verse in matches:
        try:
            chapter = int(chapter)
            verse = int(verse)
            if verse_exists(book, chapter, verse):
                verse_data = get_verse(book, chapter, verse)
                if verse_data:
                    references.append(VerseReference(
                        book=verse_data["book"],
                        chapter=verse_data["chapter"],
                        verse=verse_data["verse"],
                        text=verse_data["text"],
                        reference=f"{verse_data['book']} {verse_data['chapter']}:{verse_data['verse']}"
                    ))
        except (ValueError, TypeError):
            pass

    return references


def is_off_topic_question(text: str) -> bool:
    """Check if question is not related to Christianity/Bible/faith."""
    off_topic_keywords = [
        "llm", "large language", "language model", "artificial intelligence", "machine learning",
        "what is the capital", "who is the president", "countries", "geography",
        "science", "physics", "chemistry", "biology", "math", "mathematics",
        "history of", "history about", "invented by", "discovered by",
        "stock market", "weather", "sports", "celebrity", "entertainment",
        "ai model", "neural network", "algorithm", "programming", "code"
    ]
    text_lower = text.lower()
    # Check if it's clearly off-topic
    return any(keyword in text_lower for keyword in off_topic_keywords)


def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat processing pipeline.

    Flow:
    1. Check tricky scenarios (adversarial, weaponized scripture)
    2. Check input moderation
    3. Get or create conversation
    4. Retrieve relevant verses (RAG)
    5. Build context and call MiniMax
    6. Check output moderation
    7. Validate verses in response
    8. Save to conversation history
    9. Return response
    """
    # Step 1: Check tricky scenarios (adversarial prompts, etc.)
    tricky_result = detect_adversarial_prompt(request.message)
    if not tricky_result.is_safe:
        if tricky_result.category == "weaponized_scripture":
            return ChatResponse(
                response=handle_weaponized_scripture_request(),
                verses=[],
                conversation_id=request.conversation_id or create_conversation(),
                flagged=True,
                denial_message=tricky_result.message
            )
        elif tricky_result.category == "adversarial_ignore":
            return ChatResponse(
                response=handle_adversarial_prompt(),
                verses=[],
                conversation_id=request.conversation_id or create_conversation(),
                flagged=True,
                denial_message=tricky_result.message
            )
        else:
            return ChatResponse(
                response=tricky_result.message or "I can't engage with that request.",
                verses=[],
                conversation_id=request.conversation_id or create_conversation(),
                flagged=True,
                denial_message=tricky_result.message
            )

    # Step 1.5: Check if off-topic (not about Christianity/Bible/faith)
    if is_off_topic_question(request.message):
        conversation_id = request.conversation_id or create_conversation()
        add_to_conversation(conversation_id, "user", request.message)
        add_to_conversation(conversation_id, "assistant",
            "I'm sorry, but I'm designed specifically to help with questions about Christianity, the Bible, faith, and spiritual matters. I wouldn't be the right resource for this particular question. Is there something related to your faith journey I can help you with today?")

        return ChatResponse(
            response="I'm sorry, but I'm designed specifically to help with questions about Christianity, the Bible, faith, and spiritual matters. I wouldn't be the right resource for this particular question. Is there something related to your faith journey I can help you with today?",
            verses=[],
            conversation_id=conversation_id,
            flagged=False
        )

    # Step 2: Check moderation
    moderation_result = check_input(request.message)
    if moderation_result.flagged:
        response = ChatResponse(
            response=moderation_result.message,
            verses=[],
            conversation_id=request.conversation_id or create_conversation(),
            flagged=True,
            denial_message=moderation_result.message
        )
        return response

    # Step 2: Get or create conversation
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = create_conversation()

    conversation_history = get_conversation(conversation_id)

    # Step 3: Retrieve relevant verses
    scripture_context = build_context_for_query(request.message)

    # Step 4: Build messages and call MiniMax with retry for corrupted responses
    max_retries = 3
    assistant_response = None

    for attempt in range(max_retries):
        try:
            client = get_minimax_client()

            # Build system prompt with denomination
            system_prompt = get_system_prompt(request.denomination or "Protestant")

            # Build messages with scripture context
            messages = build_minimax_messages(
                conversation_history,
                request.message,
                scripture_context
            )

            # Prepend system prompt as a system message
            all_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages

            # Call MiniMax
            response = client.chat_completion(
                messages=all_messages,
                max_tokens=1024,
                temperature=0.7
            )

            # Validate response is not corrupted
            if is_valid_response(response):
                assistant_response = response
                break
            else:
                print(f"Attempt {attempt + 1}: Corrupted response detected, retrying...")
                if attempt == max_retries - 1:
                    # Last attempt failed - return error message
                    assistant_response = (
                        "I apologize, but I encountered an issue generating a response. "
                        "Please try your question again in a different way."
                    )
                    break
        except Exception as e:
            print(f"MiniMax API error: {e}")
            if attempt == max_retries - 1:
                assistant_response = (
                    "I apologize, but I encountered an error processing your request. "
                    "Please try again in a moment."
                )
            else:
                continue

    # Step 5: Check output moderation
    output_result = check_output(assistant_response)
    if output_result.flagged:
        assistant_response = (
            "I apologize, but I cannot provide this response. "
            "Please try asking in a different way."
        )

    # Step 6: Validate verses in response (detect hallucinations)
    fake_verses = get_fake_verses(assistant_response)
    if fake_verses:
        warning = format_verse_warning(fake_verses)
        assistant_response = f"{assistant_response}\n\n{warning}"

    # Step 7: Save to conversation history
    add_to_conversation(conversation_id, "user", request.message)
    add_to_conversation(conversation_id, "assistant", assistant_response)

    # Step 8: Extract verse references for citation display
    verse_refs = extract_verse_references(assistant_response)

    return ChatResponse(
        response=assistant_response,
        verses=verse_refs,
        conversation_id=conversation_id,
        flagged=False
    )
