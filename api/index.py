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
from fastapi.responses import JSONResponse

app = FastAPI(title="Christian AI Assistant")

# Import src modules after path is set
from src.models import ChatRequest, ChatResponse, HealthResponse
from src.chat import process_chat

@app.get("/")
async def root():
    return {"message": "Christian AI Assistant API"}

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

# For Vercel serverless
handler = app