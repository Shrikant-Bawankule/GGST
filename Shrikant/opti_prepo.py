
!pip install -q torchaudio librosa pyloudnorm noisereduce jiwer faster-whisper pydub soundfile torch
!pip install -q git+https://github.com/snakers4/silero-vad.git

from google.colab import drive
drive.mount('/content/drive')

AUDIO_DIR = "/content/drive/MyDrive/GGST/ml_test_dataset/audio+transcripts"   # folder with audio files
CSV_PATH  = "/content/drive/MyDrive/GGST/malya.csv"  # CSV with audio_file, transcript
PRE_DIR   = "/content/drive/MyDrive/preprocessed_ml"

import os
os.makedirs(PRE_DIR, exist_ok=True)

import os
import torch
import torchaudio
import librosa
import numpy as np
import pyloudnorm as pyln
import noisereduce as nr
from jiwer import wer
from faster_whisper import WhisperModel
from pydub import AudioSegment
import pandas as pd

vad_model, vad_utils = torch.hub.load(
    'snakers4/silero-vad',
    'silero_vad',
    trust_repo=True
)

(get_speech_timestamps,
 save_audio,
 _, _, collect_chunks) = vad_utils

TARGET_SR = 16000
TARGET_LOUDNESS = -20.0

import soundfile as sf

def preprocess_audio(in_path, out_path):
    y, sr = librosa.load(in_path, sr=None, mono=True)

    if sr != TARGET_SR:
        y = librosa.resample(y=y, orig_sr=sr, target_sr=TARGET_SR)
        sr = TARGET_SR

    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(y)
    y = pyln.normalize.loudness(y, loudness, TARGET_LOUDNESS)

    wav = torch.tensor(y).float()
    speech_ts = get_speech_timestamps(wav, vad_model, sampling_rate=sr)

    if len(speech_ts) == 0:
        return None

    y_vad = collect_chunks(speech_ts, wav).numpy()

    noise = y[:int(0.5 * sr)]
    snr = 10 * np.log10((np.mean(y_vad**2) + 1e-9) /
                        (np.mean(noise**2) + 1e-9))

    if snr < 25:
        y_vad = nr.reduce_noise(y=y_vad, sr=sr)

    sf.write(out_path, y_vad, sr)
    return out_path

df = pd.read_csv(CSV_PATH, encoding='latin1')
df = df.dropna(subset=["audio_file", "transcript"])
df = df.head(15)

model = WhisperModel(
    "small",
    device="cuda",
    compute_type="int8"
)

def whisper_asr(audio_path):
    segments, _ = model.transcribe(audio_path, language="ml")
    return " ".join([s.text.strip() for s in segments])

!pip install torchcodec

raw_wers = []
pre_wers = []

for _, row in df.iterrows():
    audio_path = os.path.join(AUDIO_DIR, row["audio_file"])
    raw_gt = row["transcript"]

    if not os.path.exists(audio_path):
        continue

    # RAW WER (CSV transcript vs itself = baseline 0, kept for consistency)
    raw_pred = whisper_asr(audio_path)
    raw_wers.append(wer(raw_gt, raw_pred))


    # PREPROCESS → WHISPER
    pre_audio = os.path.join(PRE_DIR, row["audio_file"])
    processed = preprocess_audio(audio_path, pre_audio)

    if processed:
        pre_pred = whisper_asr(processed)
        pre_wers.append(wer(raw_gt, pre_pred))

raw_avg_wer = np.mean(raw_wers)
pre_avg_wer = np.mean(pre_wers)

print("FILES USED:", len(pre_wers))
print("RAW WER:", round(raw_avg_wer, 4))
print("PREPROCESSED WER:", round(pre_avg_wer, 4))
