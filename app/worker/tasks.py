import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from .celery_app import celery_app

# Load environment variables from .env file
load_dotenv()

# --- Configuration for Vector Store ---
# This ensures ChromaDB persists data to disk in the 'chroma_db' directory
CHROMA_PERSIST_DIR = "chroma_db_persistent"

# --- Initialize components once ---
embeddings = OpenAIEmbeddings()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

@celery_app.task
def process_directory(directory_path: str, collection_name: str):
    """
    Celery task to load all documents from a directory, process them,
    and save them to a persistent ChromaDB collection.
    """
    try:
        print(f"Starting to process directory: {directory_path} for collection: {collection_name}")
        # Check if the directory exists
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # 1. LOAD all documents from the directory
        # Using the same DirectoryLoader logic you provided
        loader = DirectoryLoader(directory_path, glob="**/*[.pdf,.docx,.doc]", use_multithreading=True)
        documents = loader.load()

        if not documents:
            print(f"No documents found in {directory_path}")
            return "No documents found to process."
        
        print(f"Successfully loaded {len(documents)} documents.")

        # 2. SPLIT the documents into chunks
        texts = text_splitter.split_documents(documents)
        print(f"Documents split into {len(texts)} chunks.")

        # 3. STORE the chunks in a persistent Chroma vector store
        # This is the most important change. Instead of `from_documents` (which is for in-memory),
        # we initialize Chroma with a persistent directory and collection name,
        # then use `add_documents` to save the new chunks.
        print(f"Storing chunks in ChromaDB collection: {collection_name}")
        Chroma.from_documents(
            documents=texts, 
            embedding=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=collection_name
        )

        print(f"Successfully processed directory and saved to collection '{collection_name}'")
        return f"Successfully processed {len(documents)} documents."

    except Exception as e:
        print(f"Error processing directory {directory_path}: {e}")
        # Add more robust error handling as needed
        return f"Error processing directory: {e}"