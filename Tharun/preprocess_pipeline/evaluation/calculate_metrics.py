import jiwer
from evaluation.normalize_text import normalize_text


def calculate_metrics(reference_text, hypothesis_text):
    """
    Calculate WER, CER, SER between reference and hypothesis text
    """

    # Normalize both texts
    ref = normalize_text(reference_text)
    hyp = normalize_text(hypothesis_text)

    # Word Error Rate
    wer = jiwer.wer(ref, hyp)

    # Character Error Rate
    cer = jiwer.cer(ref, hyp)

    # Sentence Error Rate (0 = correct, 1 = incorrect)
    ser = 0 if ref == hyp else 1

    return wer, cer, ser
