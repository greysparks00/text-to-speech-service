import os

from fastapi import HTTPException, APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel, Field

from speech_client import create_speech, model_status

router = APIRouter()

class SpeechRequest(BaseModel):
	text: str = Field(min_length=1, max_length=2000)
	
@router.post("/synthesize")
def synthesize(request: SpeechRequest):
    if model_status() != "ready":
        raise HTTPException(
            status_code=503,
            detail=f"TTS model is {model_status()}"
        )

    path = create_speech(request.text)

    return FileResponse(
        path=path,
        media_type="audio/wav",
        background=BackgroundTask(os.remove, path)
    )