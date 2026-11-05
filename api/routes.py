import os
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel, Field

from speech_client import create_speech, model_status

logger = logging.getLogger(__name__)

router = APIRouter()

class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)

@router.post("/synthesize")
def synthesize(request: SpeechRequest):
    status = model_status()

    if status != "ready":
        raise HTTPException(
            status_code=503,
            detail=f"TTS model is {status}"
        )

    try:
        path = create_speech(request.text)

    except Exception:
        logger.exception("TTS synthesis failed")
        raise HTTPException(
            status_code=500,
            detail="TTS synthesis failed"
        )

    return FileResponse(
        path=path,
        media_type="audio/wav",
        filename="speech.wav",
        background=BackgroundTask(os.remove, path)
    )
