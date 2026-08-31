from fastapi import APIRouter, HTTPException
from app.schemas import ClipRequest
from app.services.clipper import parse_timestamp
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/clip")
async def create_clip(req: ClipRequest):
    """Validate request and return a stub response for now."""
    # URL and timestamp validations are handled by Pydantic
    try:
        start_seconds = parse_timestamp(req.start)
        end_seconds = parse_timestamp(req.end)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if start_seconds >= end_seconds:
        raise HTTPException(status_code=400, detail="start must be less than end")

    # TODO: enqueue or run yt-dlp + ffmpeg to produce clip
    logger.info("Received clip request: %s to %s", req.start, req.end)

    return {"status": "accepted", "start_sec": start_seconds, "end_sec": end_seconds}
