"""
Pydantic models for API request/response schemas.
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    """A single message in the conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request body for /chat endpoint."""
    message: str
    conversation_id: Optional[str] = None
    denomination: Optional[str] = "Protestant"  # Default, can be changed by user


class VerseReference(BaseModel):
    """A Bible verse reference."""
    book: str
    chapter: int
    verse: int
    text: str
    reference: str  # e.g., "John 3:16"


class ChatResponse(BaseModel):
    """Response body for /chat endpoint."""
    response: str
    verses: list[VerseReference] = []  # Bible verses used in response
    conversation_id: str
    flagged: bool = False
    denial_message: Optional[str] = None


class ImageGenerationRequest(BaseModel):
    """Request body for /generate-image endpoint."""
    prompt: str
    conversation_id: Optional[str] = None


class ImageGenerationResponse(BaseModel):
    """Response body for /generate-image endpoint."""
    image_url: Optional[str] = None
    prompt: str
    success: bool
    error: Optional[str] = None
    blocked: Optional[bool] = None


class HealthResponse(BaseModel):
    """Response body for /health endpoint."""
    status: str
    timestamp: datetime
