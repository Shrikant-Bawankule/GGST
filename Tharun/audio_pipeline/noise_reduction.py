import noisereduce as nr

def reduce_noise(audio, sr):
    return nr.reduce_noise(y=audio, sr=sr)
