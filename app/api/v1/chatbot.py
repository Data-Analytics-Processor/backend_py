"""Chatbot API endpoints for handling chat interactions.

This module shall provide endpoints for chat interactions, including regular chat,
streaming chat, message history management, and chat history clearing.
"""

import shutil
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.core.langgraph.graph import graph_app

router = APIRouter()

# --- Schemas ---
class ChatRequest(BaseModel):
    message: str
    session_id: str
    # Allow frontend to tell us which file to use
    csv_file_path: Optional[str] = None 

class ChatResponse(BaseModel):
    response: str
    history: List[Dict[str, Any]]

class UploadResponse(BaseModel):
    filename: str
    file_path: str
    message: str

# --- Endpoints ---

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Simple file upload. Returns the path so the frontend can send it back in /chat.
    """
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / file.filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return UploadResponse(
            filename=file.filename,
            file_path=str(file_path),
            message="File uploaded successfully. Pass 'file_path' to /chat endpoint."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.session_id}}
        
        # Pass the CSV path into the state if provided
        input_state = {
            "messages": [("user", request.message)],
        }
        if request.csv_file_path:
            input_state["csv_file_path"] = request.csv_file_path
        
        final_state = None
        async for event in graph_app.astream(input_state, config, stream_mode="values"):
            final_state = event
            
        last_message = final_state["messages"][-1]
        
        return ChatResponse(
            response=last_message.content,
            history=[{"role": m.type, "content": m.content} for m in final_state["messages"]]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))