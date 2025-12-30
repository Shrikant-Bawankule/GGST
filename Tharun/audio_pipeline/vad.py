import torch
import numpy as np
from silero_vad import get_speech_timestamps

model, utils = torch.hub.load(
    'snakers4/silero-vad',
    'silero_vad',
    force_reload=False
)

(get_speech_timestamps, _, _, _, _) = utils

def apply_vad(audio, sr):
    # Defensive check
    if audio is None or len(audio) == 0:
        return audio

    audio = np.array(audio)

    timestamps = get_speech_timestamps(
        audio,
        model,
        sampling_rate=sr,
        threshold=0.3,           # LESS aggressive
        min_speech_duration_ms=250,
        min_silence_duration_ms=100
    )

    # 🔑 Fallback: if VAD removes everything, return original audio
    if not timestamps:
        print("  ⚠ VAD found no speech, returning original audio")
        return audio

    speech = []
    for t in timestamps:
        speech.extend(audio[t['start']:t['end']])

    return np.array(speech)

def energy_vad(audio, threshold=0.01):
    return audio if np.mean(np.abs(audio)) > threshold else audio
