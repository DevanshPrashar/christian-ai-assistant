import os
import sys
from typing import Optional

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load env vars
load_dotenv()

app = FastAPI(title="Christian AI Assistant")

# Import after path is set
from src.models import ChatRequest, ChatResponse, HealthResponse
from src.chat import process_chat

@app.get("/")
async def root():
    return {"message": "Christian AI Assistant API - visit /docs for Swagger UI"}

@app.get("/health", response_model=HealthResponse)
async def health():
    from datetime import datetime
    return HealthResponse(status="healthy", timestamp=datetime.now())

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return process_chat(request)

# For Vercel serverless
handler = app