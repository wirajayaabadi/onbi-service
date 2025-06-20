import os
from dotenv import load_dotenv
from fastapi import HTTPException
from app.helpers.langchain import langchain_directory
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from app.models.chat import Chat

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# --- Configuration - MUST MATCH THE WORKER ---
CHROMA_PERSIST_DIR = "chroma_db_persistent"
# We'll use a default collection name for this example
DEFAULT_COLLECTION_NAME = "default_collection"

def run_conversation(request: Chat):
  # --- Initialize models once to be reused across requests ---
  embeddings = OpenAIEmbeddings()

  llm = ChatOpenAI(
    model_name="gpt-4.1-mini",
    temperature=0.7,
    openai_api_key=api_key
  )
  # response = langchain_directory(message)
  
  """
    Endpoint for the chat functionality. It connects to the persistent
    vector store and uses a QA chain to answer questions.
  """
  try:
      # 1. CONNECT to the existing persistent vector store
      vectorstore = Chroma(
          persist_directory=CHROMA_PERSIST_DIR,
          embedding_function=embeddings,
          collection_name=request.collection_name
      )

      # 2. CREATE the retriever and QA chain
      # This part is from your original script
      retriever = vectorstore.as_retriever()
      qa_chain = RetrievalQA.from_chain_type(
          llm=llm,
          chain_type="stuff",
          retriever=retriever
      )

      # 3. RUN the query
      response = qa_chain.run(request.message)

      return response
  
  except Exception as e:
      # This can happen if the collection doesn't exist yet
      raise HTTPException(status_code=500, detail=f"An error occurred: {e}. Has the directory been processed?")