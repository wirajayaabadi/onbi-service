from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat import router as chat_router

app = FastAPI(title="ONBI API")

origins = [
  "http://localhost:8000"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(chat_router)
