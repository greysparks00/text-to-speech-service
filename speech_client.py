import uuid
import traceback
import threading
from pathlib import Path

import soundfile as sf

BASE_DIR = Path(__file__).resolve().parent
VOICE_PATH = BASE_DIR / "voices" / "tom_pearl.wav"
TEMP_PATH = BASE_DIR / "temp_audios"

model = None
load_error = None
generation_lock = threading.Lock()


def load_model():
    global model, load_error

    print("[TTS] Loading KittenTTS...", flush=True)

    try:
        from kittenml import KittenTTS

        loaded = KittenTTS("KittenML/kitten-tts-2")
        model = loaded

        print("[TTS] Model loaded successfully!", flush=True)

    except Exception as exc:
        load_error = str(exc)
        traceback.print_exc()


def model_status():
    if load_error is not None:
        return "failed"

    if model is None:
        return "loading"

    return "ready"


def create_speech(text: str):
    if model is None:
        raise RuntimeError("TTS model is not ready")

    TEMP_PATH.mkdir(exist_ok=True)
    output_path = TEMP_PATH / f"{uuid.uuid4()}.wav"

    with generation_lock:
        audio = model.generate(
            text,
            reference=str(VOICE_PATH)
        )

        sf.write(str(output_path), audio, model.sample_rate)

    return str(output_path)