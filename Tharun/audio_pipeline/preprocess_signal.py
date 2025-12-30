from .noise_reduction import reduce_noise
from .normalize_audio import normalize_audio

def preprocess_signal(audio, sr):
    audio = reduce_noise(audio, sr)
    audio = normalize_audio(audio)
    return audio
