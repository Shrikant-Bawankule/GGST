import os
import librosa
import soundfile as sf
import noisereduce as nr
import numpy as np

RAW_DIR = "data/raw_audio/Hindi"
CLEAN_DIR = "data/clean_audio/Hindi"

def preprocess_audio(audio, sr):
    # Noise reduction
    audio = nr.reduce_noise(y=audio, sr=sr)

    # Volume normalization
    audio = audio / max(abs(audio))

    return audio

def run_audio_preprocessing():
    os.makedirs(CLEAN_DIR, exist_ok=True)

    for file in sorted(os.listdir(RAW_DIR)):
        if file.lower().endswith(".mp3"):
            mp3_path = os.path.join(RAW_DIR, file)
            wav_path = os.path.join(CLEAN_DIR, file.replace(".mp3", ".wav"))

            audio, sr = librosa.load(mp3_path, sr=16000, mono=True)
            audio = preprocess_audio(audio, sr)

            sf.write(wav_path, audio, sr)
            print("Preprocessed:", file)

    print("✅ Audio preprocessing completed")
