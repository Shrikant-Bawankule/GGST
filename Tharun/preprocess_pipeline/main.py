"""
PHASE 1: ASR Hypothesis Generation

What this file does:
1. (Optional) Run audio preprocessing
2. Run ASR on clean WAV files
3. Store transcribed (hypothesis) text to disk

NOTE:
- No reference loading
- No normalization
- No WER / CER / SER calculation
"""

import os

from audio_pipeline.audio_pipeline import run_audio_preprocessing
from asr.transcribe import transcribe_audio


# =======================
# CONFIGURATION (EDIT ONLY THIS)
# =======================

LANGUAGE = "Hindi"

CLEAN_AUDIO_DIR = f"data/clean_audio/{LANGUAGE}"
HYPOTHESIS_DIR = f"data/hypothesis/{LANGUAGE}"

MAX_FILES = 10            # change for testing (1, 5, 10, 100)
RUN_PREPROCESSING = False   # True only if new raw audio added

# =======================


def main():
    print("🚀 PHASE 1: Hypothesis Generation Started")

    # STEP 1: Audio preprocessing (optional)
    if RUN_PREPROCESSING:
        print("🔊 Running audio preprocessing...")
        run_audio_preprocessing()
    else:
        print("⏭️ Skipping audio preprocessing (already done)")

    os.makedirs(HYPOTHESIS_DIR, exist_ok=True)

    processed = 0

    wav_files = sorted([
        f for f in os.listdir(CLEAN_AUDIO_DIR)
        if f.lower().endswith(".wav")
    ])

    for wav_file in wav_files:
        if processed >= MAX_FILES:
            break

        wav_path = os.path.join(CLEAN_AUDIO_DIR, wav_file)
        hyp_txt_path = os.path.join(
            HYPOTHESIS_DIR,
            wav_file.replace(".wav", ".txt")
        )

        print(f"\n▶️ Transcribing: {wav_file}")

        # Skip ASR if hypothesis already exists
        if os.path.exists(hyp_txt_path):
            print("📄 Hypothesis already exists, skipping")
            processed += 1
            continue

        hypothesis_text = transcribe_audio(wav_path)

        with open(hyp_txt_path, "w", encoding="utf-8") as f:
            f.write(hypothesis_text.strip())

        print("📝 Hypothesis saved:", hyp_txt_path)
        processed += 1

    print("\n✅ PHASE 1 completed")
    print("Files processed:", processed)


if __name__ == "__main__":
    main()
