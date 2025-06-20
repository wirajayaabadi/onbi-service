# /app/services/chat_service.py (or similar file)

import os
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from app.models.chat import Chat

# --- Assume you have a Pydantic model like this ---
# from pydantic import BaseModel
# class Chat(BaseModel):
#     message: str
#     collection_name: str = "default_collection"

# --- 1. Load Environment Variables ---
load_dotenv()

# --- 2. Configuration (Global Constants) ---
# This ensures ChromaDB persists data to disk in the 'chroma_db_persistent' directory
CHROMA_PERSIST_DIR = "chroma_db_persistent"
DEFAULT_COLLECTION_NAME = "default_collection"

# --- 3. Initialize Expensive Objects ONCE at Startup ---
# These models will be created only when the application boots up
# and will be reused for every request, which is much more efficient.
try:
    embeddings_model = OpenAIEmbeddings()
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)
    print("LLM and Embeddings models initialized successfully.")
except Exception as e:
    # If models fail to load (e.g., missing API key), the app shouldn't start.
    print(f"FATAL: Could not initialize models: {e}")
    llm = None
    embeddings_model = None

# --- 4. Define the Core Logic Function ---
# The function now uses the globally initialized models.
def run_conversation(request: Chat): # Assuming request_body is a dict like {"message": "...", "collection_name": "..."}
  """
  Handles the chat logic by connecting to the persistent vector store
  and using a QA chain to answer questions.
  """
  if not llm or not embeddings_model:
      raise HTTPException(
          status_code=503, # Service Unavailable
          detail="Models are not available. Please check server logs."
      )
  
  query = request.message
  collection_name = request.collection_name

  if not query:
      raise HTTPException(status_code=400, detail="The 'message' field is required.")

  try:
      # 1. CONNECT to the existing persistent vector store
      vectorstore = Chroma(
          persist_directory=CHROMA_PERSIST_DIR,
          embedding_function=embeddings_model,
          collection_name=collection_name
      )

      # 2. CREATE the retriever and QA chain
      retriever = vectorstore.as_retriever()
      qa_chain = RetrievalQA.from_chain_type(
          llm=llm,
          chain_type="stuff",
          retriever=retriever,
          return_source_documents=True # Optional: useful for debugging
      )

      # 3. RUN the query using the modern .invoke() method
      # .invoke() is more flexible and part of the standard LCEL interface
      result = qa_chain.invoke({"query": query})

      # The result is a dictionary, e.g., {"query": "...", "result": "...", "source_documents": [...]}
      return result["result"]
  
  except Exception as e:
      # This can happen if the collection doesn't exist or other runtime errors.
      # It's good practice to log the actual error for debugging.
      print(f"An error occurred during conversation: {e}")
      raise HTTPException(status_code=500, detail=f"An error occurred while processing your request. It's possible the data source '{collection_name}' has not been processed yet.")