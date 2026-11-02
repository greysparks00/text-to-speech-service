import os

from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel, Field

from speech_client import create_speech

router = APIRouter()

class SpeechRequest(BaseModel):
	text: str = Field(min_length=1, max_length=2000)
	voice: int = Field(default=0, ge=0, le=1)
	
@router.post("/synthesize")
def synthesize(request: SpeechRequest):
	path = create_speech(
		request.text,
		request.voice
	)

	return FileResponse(
		path=path,
		media_type="audio/wav",
		background=BackgroundTask(os.remove, path)
	)