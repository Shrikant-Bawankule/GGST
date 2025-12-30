"""
PHASE 2: ASR Evaluation

- Uses stored hypothesis files
- Uses a SINGLE reference file (line-wise)
- Calculates WER / CER / SER
"""

import os

from evaluation.load_reference import load_reference_from_single_file
from evaluation.calculate_metrics import calculate_metrics


# =======================
# CONFIGURATION
# =======================

LANGUAGE = "Hindi"

HYPOTHESIS_DIR = f"data/hypothesis/{LANGUAGE}"
REFERENCE_FILE = f"data/transcripts/{LANGUAGE}/reference.txt"

MAX_FILES = 10   # change to 1, 5, 50, 100

# =======================


def main():
    print("📊 PHASE 2: Evaluation Started")
    print("📄 Reference file:", REFERENCE_FILE)

    total_wer = 0.0
    total_cer = 0.0
    total_ser = 0
    processed = 0

    hyp_files = sorted([
        f for f in os.listdir(HYPOTHESIS_DIR)
        if f.endswith(".txt")
    ])

    for hyp_file in hyp_files:
        if processed >= MAX_FILES:
            break

        hyp_path = os.path.join(HYPOTHESIS_DIR, hyp_file)

        print(f"\n▶️ Evaluating: {hyp_file}")

        # Load hypothesis
        with open(hyp_path, "r", encoding="utf-8") as f:
            hypothesis = f.read().strip()

        # Load corresponding reference line
        reference = load_reference_from_single_file(
            REFERENCE_FILE,
            hyp_file.replace(".txt", ".wav")
        )

        wer, cer, ser = calculate_metrics(reference, hypothesis)

        print("Reference :", reference)
        print("Hypothesis:", hypothesis)
        print(f"WER: {wer:.2f} | CER: {cer:.2f} | SER: {ser}")

        total_wer += wer
        total_cer += cer
        total_ser += ser
        processed += 1

    print("\n📈 FINAL AVERAGE METRICS")
    print("Files evaluated:", processed)

    if processed > 0:
        print(f"Average WER: {total_wer / processed:.2f}")
        print(f"Average CER: {total_cer / processed:.2f}")
        print(f"Average SER: {total_ser / processed:.2f}")
    else:
        print("❌ No files evaluated")


if __name__ == "__main__":
    main()
