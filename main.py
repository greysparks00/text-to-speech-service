from contextlib import asynccontextmanager
from threading import Thread

from fastapi import FastAPI, HTTPException
from api.routes import router
from speech_client import load_model, model_status

@asynccontextmanager
async def lifespan(app: FastAPI):
    Thread(
        target=load_model,
        daemon=True,
        name="kitten-loader"
    ).start()

    yield

app = FastAPI(
    title="Junction Service",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health", include_in_schema=False)
def health():
    status = model_status()

    if status == "failed":
        raise HTTPException(503, "Model failed to load")

    return {
        "status": "healthy",
        "model": status
    }

@app.get("/ready")
def ready():
    status = model_status()

    if status != "ready":
        raise HTTPException(503, f"Model is {status}")

    return {"status": "ready"}

app.include_router(router)