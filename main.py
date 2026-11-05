from contextlib import asynccontextmanager
from threading import Thread

from fastapi import FastAPI, HTTPException

from api.routes import router
from speech_client import load_model, model_status
from simple_voice import simple_available


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load Pocket TTS once in a background thread.
    # FastAPI can start accepting health checks immediately.
    loader = Thread(
        target=load_model,
        daemon=True,
        name="pocket-tts-loader"
    )
    loader.start()

    yield


app = FastAPI(
    title="Junction Text-to-Speech Service",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health", include_in_schema=False)
def health():
    status = model_status()

    if status == "failed" and not simple_available():
        raise HTTPException(
            status_code=503,
            detail="TTS model failed to load"
        )

    return {
        "status": "healthy",
        "model": status
    }


@app.get("/ready")
def ready():
    status = model_status()

    if status != "ready":
        raise HTTPException(
            status_code=503,
            detail=f"Model is {status}"
        )

    return {
        "status": "ready"
    }


app.include_router(router)
