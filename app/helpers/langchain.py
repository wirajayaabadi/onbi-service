import os
import asyncio
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

load_dotenv()

def langchain_directory(query: str):
  directory_path = "./public/data/"
  
  # Check if the directory exists
  if not os.path.exists(directory_path):
      print(f"Directory not found: {directory_path}")
  else:
      print(f"Loading documents from: {directory_path}")
    
  # Use a glob pattern to load specific file types
  # This pattern says "look in the directory for any file that ends with .pdf, .docx, or .doc"
  loader = DirectoryLoader(directory_path, glob="**/*[.pdf,.docx,.doc]", use_multithreading=True)
  
  # Load the documents  
  try:
      documents = loader.load()

      # Print a summary of what was loaded
      print(f"Successfully loaded {len(documents)} documents.")
      text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
      texts = text_splitter.split_documents(documents)
    
      embeddings = OpenAIEmbeddings() # Requires an OpenAI API key
      
      api_key = os.getenv("OPENAI_API_KEY")
      
      llm = ChatOpenAI(
        model_name="gpt-4.1-mini",
        temperature=0.7,
        openai_api_key=api_key
      )
      
      # Create a Chroma vector store from the text chunks and embeddings
      vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings)

      # Create a retriever from the vector store
      retriever = vectorstore.as_retriever()
      qa_chain = RetrievalQA.from_chain_type(
          llm=llm,
          chain_type="stuff",
          retriever=retriever
      )
      
      response = qa_chain.run(query)
      return response
  except Exception as e:
      print(f"An error occurred during loading: {e}")    
  # loader_map = {
  #   ".pdf": PyPDFLoader,
  #   ".docx": UnstructuredFileLoader,
  #   ".doc": UnstructuredFileLoader,
  # }
  
  # loader = DirectoryLoader("public/data/", loader_cls=loader_map)
  # documents = loader.load()
  # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
  # texts = text_splitter.split_documents(documents)
  # embeddings = OpenAIEmbeddings() # Requires an OpenAI API key
  
  # api_key = os.getenv("OPENAI_API_KEY")
  
  # llm = ChatOpenAI(
  #   model_name="gpt-4.1-mini",
  #   temperature=0.7,
  #   openai_api_key=api_key
  # )
  
  # # Create a Chroma vector store from the text chunks and embeddings
  # vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings)

  # # Create a retriever from the vector store
  # retriever = vectorstore.as_retriever()
  # qa_chain = RetrievalQA.from_chain_type(
  #     llm=llm,
  #     chain_type="stuff",
  #     retriever=retriever
  # )
  
  # response = qa_chain.run(query)
  # return response
  
async def chat_response_generator(response:str):
    words = response.split()
      
    for word in words:
        yield word + " "
        await asyncio.sleep(0.02)
