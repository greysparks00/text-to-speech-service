import os
import uuid

import pyttsx4

TEMP_AUDIO_PATH = "./temp_audios"

def create_speech(text: str, voice: int):
    # initialize engine
    speech_engine = pyttsx4.init()

    voices = speech_engine.getProperty("voices")

    # fallback to default voice if index is out of bounds
    if voice >= len(voices):
        voice = 0

    # Set voice
    speech_engine.setProperty("voice", voices[voice].id)

    # generate unique filename
    random_id = str(uuid.uuid4())
    os.makedirs(TEMP_AUDIO_PATH, exist_ok=True)
    full_path = os.path.join(TEMP_AUDIO_PATH, random_id + ".wav")

    # queue file creation and flush the engine loop cleanly
    speech_engine.save_to_file(text, full_path)
    speech_engine.runAndWait()

    # validate output
    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
        return os.path.abspath(full_path)
    else:
        raise FileNotFoundError(f"Failed to generate audio file at {full_path}")