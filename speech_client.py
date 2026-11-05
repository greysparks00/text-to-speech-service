import uuid
import logging
import threading
from pathlib import Path

import soundfile as sf

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
VOICE_PATH = BASE_DIR / "voices" / "tom_pearl.wav"
TEMP_PATH = BASE_DIR / "temp_audios"

MODEL_NAME = "english_2026-10"

model = None
voice_state = None
load_error = None

generation_lock = threading.Lock()


def load_model():
    global model, voice_state, load_error

    load_error = None
    logger.warning("[TTS] Loading Pocket TTS...")

    try:
        from pocket_tts import TTSModel

        if not VOICE_PATH.is_file():
            raise FileNotFoundError(
                f"Reference voice not found: {VOICE_PATH}"
            )

        loaded_model = TTSModel.load_model(
            language=MODEL_NAME
        )

        logger.warning("[TTS] Loading cloned voice...")

        loaded_voice = loaded_model.get_state_for_audio_prompt(
            str(VOICE_PATH)
        )

        model = loaded_model
        voice_state = loaded_voice

        logger.warning("[TTS] Model and voice ready!")

    except Exception as exc:
        load_error = str(exc)
        logger.exception("[TTS] Model loading failed")


def model_status():
    if load_error is not None:
        return "failed"

    if model is None or voice_state is None:
        return "loading"

    return "ready"


def create_speech(text: str):
    if model_status() != "ready":
        raise RuntimeError("TTS model is not ready")

    TEMP_PATH.mkdir(parents=True, exist_ok=True)

    output_path = TEMP_PATH / f"{uuid.uuid4()}.wav"

    try:
        # Pocket TTS generation is not thread-safe.
        with generation_lock:
            audio = model.generate_audio(
                voice_state,
                text
            )

            samples = audio.detach().cpu().numpy().squeeze()

            sf.write(
                str(output_path),
                samples,
                model.sample_rate
            )

        if output_path.stat().st_size == 0:
            raise RuntimeError("Generated WAV file is empty")

        return str(output_path)

    except Exception:
        output_path.unlink(missing_ok=True)
        logger.exception("[TTS] Audio generation failed")
        raise