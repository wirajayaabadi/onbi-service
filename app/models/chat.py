from pydantic import BaseModel

class Chat(BaseModel):
  message: str
  collection_name: str
  