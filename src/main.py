"""
Christian AI Assistant - FastAPI Server.
Main entry point for the API.
"""
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from src.models import ChatRequest, ChatResponse, HealthResponse, ImageGenerationRequest, ImageGenerationResponse
from src.chat import process_chat
from src.image_gen import generate_christian_image

load_dotenv()

app = FastAPI(
    title="Christian AI Assistant",
    description="A faithful AI companion for Christians — answering questions, generating content, and staying grounded in Biblical truth.",
    version="1.0.0"
)


@app.get("/", include_in_schema=False)
async def root():
    """Serve the static chat UI."""
    return FileResponse("static/index.html")


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now()
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat endpoint - send a message and receive a scripture-grounded response.

    - Checks input for safety
    - Retrieves relevant Bible verses
    - Grounds response in scripture
    - Returns response with verse citations
    """
    return process_chat(request)


@app.post("/generate-image", response_model=ImageGenerationResponse, tags=["Image"])
async def generate_image(request: ImageGenerationRequest):
    """
    Generate a Christian-themed image.
    Uses MiniMax API with DALL-E fallback.
    Includes prompt moderation for safety.
    """
    result = generate_christian_image(request.prompt)

    if result.get("blocked"):
        return ImageGenerationResponse(
            image_url=None,
            prompt=request.prompt,
            success=False,
            error=result.get("error", "Content blocked for safety"),
            blocked=True
        )
    elif result.get("image_url"):
        return ImageGenerationResponse(
            image_url=result["image_url"],
            prompt=request.prompt,
            success=True
        )
    else:
        return ImageGenerationResponse(
            image_url=None,
            prompt=request.prompt,
            success=False,
            error=result.get("error", "Image generation failed")
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
