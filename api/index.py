import os
import sys

# Determine project root (api/ is one level deep)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add project root to Python path
sys.path.insert(0, project_root)

# Change working directory to project root so relative paths work
os.chdir(project_root)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, FileResponse

app = FastAPI(title="Christian AI Assistant")

# Import src modules after path is set
from src.models import ChatRequest, ChatResponse, HealthResponse, ImageGenerationRequest, ImageGenerationResponse
from src.chat import process_chat
from src.image_gen import generate_christian_image

@app.get("/")
async def root():
    # Serve the static frontend
    return FileResponse(os.path.join(project_root, "static", "index.html"))

@app.get("/health", response_model=HealthResponse)
async def health():
    from datetime import datetime
    return HealthResponse(status="healthy", timestamp=datetime.now())

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        return process_chat(request)
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@app.get("/favicon.ico")
async def favicon():
    return Response(content=b"", status_code=204)

@app.post("/generate-image", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
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

# For Vercel serverless
handler = app