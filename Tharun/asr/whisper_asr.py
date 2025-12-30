from faster_whisper import WhisperModel

def transcribe_whisper(audio_path):
    model = WhisperModel("base", device="cpu")
    segments, _ = model.transcribe(audio_path)
    return " ".join(seg.text.strip() for seg in segments)
