from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api.routes import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YouTube Clipper - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="")


@app.get("/")
async def root():
    return {"status": "online"}
