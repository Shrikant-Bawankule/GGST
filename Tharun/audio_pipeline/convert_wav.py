import librosa
import soundfile as sf

def convert_wav(mp3_path, wav_path):
    audio, sr = librosa.load(mp3_path, sr=16000, mono=True)
    sf.write(wav_path, audio, sr)
