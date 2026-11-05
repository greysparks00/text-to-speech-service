import io
import sys
import wave
from xml.sax.saxutils import escape


DEFAULT_VOICE = "Microsoft Zira Desktop"


class UnknownVoice(ValueError):
    pass


class SimpleVoiceUnavailable(RuntimeError):
    pass


def _voice(name):
    from win32com.client import Dispatch

    speaker = Dispatch("SAPI.SpVoice")
    for token in speaker.GetVoices():
        if token.GetAttribute("Name").casefold() == name.casefold():
            speaker.Voice = token
            return speaker
    raise UnknownVoice("Requested Windows speech voice is not installed")


def synthesize_simple(text, name, pitch, rate, volume):
    if sys.platform != "win32":
        raise SimpleVoiceUnavailable("SIMPLE requires a Windows SAPI voice")
    import pythoncom
    from win32com.client import Dispatch

    # FastAPI may use different worker threads. Each owns its own COM objects.
    pythoncom.CoInitialize()
    try:
        speaker = _voice(name)
        stream = Dispatch("SAPI.SpMemoryStream")
        stream.Format.Type = 22  # SAFT22kHz16BitMono
        speaker.AudioOutputStream = stream
        speaker.Rate = rate
        speaker.Volume = volume
        speaker.Speak(f'<pitch absmiddle="{pitch}">{escape(text)}</pitch>', 8)  # SVSFIsXML
        pcm = bytes(stream.GetData())
    finally:
        speaker = stream = None
        pythoncom.CoUninitialize()

    if not pcm:
        raise RuntimeError("Windows speech returned no samples")
    audio = io.BytesIO()
    with wave.open(audio, "wb") as wav:
        wav.setparams((1, 2, 22050, 0, "NONE", "not compressed"))
        wav.writeframes(pcm)
    return audio.getvalue()


def simple_available():
    if sys.platform != "win32":
        return False
    import pythoncom

    pythoncom.CoInitialize()
    try:
        _voice(DEFAULT_VOICE)
        return True
    except (UnknownVoice, pythoncom.com_error):
        return False
    finally:
        pythoncom.CoUninitialize()
