import os
import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from starlette.background import BackgroundTask
from pydantic import BaseModel, Field

from speech_client import create_speech, model_status
from simple_voice import DEFAULT_VOICE, SimpleVoiceUnavailable, UnknownVoice, synthesize_simple

logger = logging.getLogger(__name__)

router = APIRouter()

class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    voice_type: Literal["CLONE", "SIMPLE"] = "CLONE"
    voice_name: str = Field(default=DEFAULT_VOICE, min_length=1, max_length=128)
    pitch: int = Field(default=3, ge=-10, le=10)
    rate: int = Field(default=0, ge=-10, le=10)
    volume: int = Field(default=100, ge=0, le=100)

@router.post("/synthesize")
def synthesize(request: SpeechRequest):
    if request.voice_type == "SIMPLE":
        try:
            wav = synthesize_simple(request.text, request.voice_name, request.pitch, request.rate, request.volume)
        except SimpleVoiceUnavailable as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        except UnknownVoice as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        except Exception:
            logger.exception("SIMPLE synthesis failed")
            raise HTTPException(status_code=500, detail="SIMPLE synthesis failed")
        return Response(wav, media_type="audio/wav")

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
