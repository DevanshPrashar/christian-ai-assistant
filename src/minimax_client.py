"""
MiniMax API client for chat completions.
Handles API calls to MiniMax's LLM.
"""
import os
import json
from typing import Optional
import httpx
from dotenv import load_dotenv

load_dotenv()


class MiniMaxClient:
    """Client for MiniMax API."""

    BASE_URL = "https://api.minimaxi.chat/v1"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.group_id = os.getenv("MINIMAX_GROUP_ID")

        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY not found in environment")

    def chat_completion(
        self,
        messages: list[dict],
        model: str = "MiniMax-M2.7",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """
        Send a chat completion request to MiniMax API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default MiniMax-Text-01)
            max_tokens: Max response tokens
            temperature: Sampling temperature

        Returns:
            The assistant's response text
        """
        url = f"{self.BASE_URL}/text/chatcompletion_v2"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # Add group_id for MiniMax
        if self.group_id:
            payload["group_id"] = self.group_id

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                # Check for API errors
                if "base_resp" in data:
                    status_code = data["base_resp"].get("status_code", 0)
                    if status_code != 0:
                        raise Exception(f"MiniMax API error: {data['base_resp'].get('status_msg', 'Unknown error')}")

                # MiniMax-M2.7 response structure:
                # {"choices": [{"message": {"content": "...", "reasoning_content": "..."}}]}
                choices = data.get("choices", [])
                if choices and len(choices) > 0:
                    message = choices[0].get("message", {})
                    # Prefer normal content, fallback to reasoning_content
                    content = message.get("content", "") or message.get("reasoning_content", "")
                    if content:
                        return content

                return "I'm having trouble generating a response."

        except httpx.HTTPStatusError as e:
            print(f"MiniMax API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"MiniMax API error: {e.response.status_code}")

        except Exception as e:
            print(f"MiniMax API error: {e}")
            raise Exception(f"MiniMax API error: {str(e)}")


def get_minimax_client() -> MiniMaxClient:
    """Get or create MiniMax client."""
    return MiniMaxClient()
