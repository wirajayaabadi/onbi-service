import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import Chat
from app.services.chat import run_conversation, stream_conversation_generator
from fastapi.responses import JSONResponse
from app.models.directory import Directory
from app.helpers.langchain import chat_response_generator

# Import the celery task we defined
from app.worker.tasks import process_directory

# --- Configuration - MUST MATCH THE WORKER ---
CHROMA_PERSIST_DIR = "chroma_db_persistent"
# We'll use a default collection name for this example
DEFAULT_COLLECTION_NAME = "default_collection"

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/process-directory")
async def trigger_directory_processing(request: Directory):
    """
    Endpoint to trigger the asynchronous processing of a directory.
    """
    directory_path = request.path
    if not os.path.isdir(directory_path):
        raise HTTPException(status_code=404, detail=f"Directory not found: {directory_path}")

    # Dispatch the background task to Celery
    dir = process_directory.delay(directory_path, DEFAULT_COLLECTION_NAME)
    return JSONResponse(
        status_code=202, # Accepted
        content={
            "message": "Directory processing started in the background.",
            "directory_path": directory_path,
            "collection_name": DEFAULT_COLLECTION_NAME
        }
    )

@router.post("/send")
async def chat(request: Chat):
    # response = langchain_directory(request.message)
    response = run_conversation(request)

    return StreamingResponse(stream_conversation_generator(request), media_type="text/event-stream")
    
    # return StreamingResponse(chat_response_generator(response), media_type="text/plain")
    # return JSONResponse(
    #     status_code=202,
    #     content={
    #         "message": response
    #     }
    # )