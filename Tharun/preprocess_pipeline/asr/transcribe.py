from faster_whisper import WhisperModel

# load model once
model = WhisperModel("small", device="cpu")

def transcribe_audio(wav_path):
    segments, _ = model.transcribe(wav_path)
    text = " ".join([segment.text for segment in segments])
    return text.strip()
