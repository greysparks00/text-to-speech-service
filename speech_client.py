import soundfile as sf

from kittenml import KittenTTS

import os
import uuid

m = KittenTTS("KittenML/kitten-tts-2")

VOICE_REFERENCE_PATH = "./voices/tom_pearl.wav"
TEMP_AUDIO_PATH = "./temp_audios"

def create_speech(text: str):
    # generate voice
    audio = m.generate(text, reference=VOICE_REFERENCE_PATH)

    # generate unique filename
    random_id = str(uuid.uuid4())
    os.makedirs(TEMP_AUDIO_PATH, exist_ok=True)
    full_path = os.path.join(TEMP_AUDIO_PATH, random_id + ".wav")

    # save to file
    sf.write(full_path, audio, m.sample_rate)

    # validate output
    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
        return os.path.abspath(full_path)
    else:
        raise FileNotFoundError(f"Failed to generate audio file at {full_path}")