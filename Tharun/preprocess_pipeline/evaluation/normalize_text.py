import re

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    # Hindi-specific normalizations
    text = text.replace("क लिए", "के लिए")
    text = text.replace("लए", "लिए")

    return " ".join(text.split())
