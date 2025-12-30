import numpy as np

def normalize_audio(audio):
    return audio / max(abs(audio))
