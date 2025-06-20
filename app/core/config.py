import os 
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
  raise RuntimeError("OPENAI_API_KEY not set in .env")

openai_client = OpenAI(api_key=API_KEY)
