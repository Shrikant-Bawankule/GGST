# Stage 1B Production Module
# Complete text validation pipeline

import re
import unicodedata

class Stage1BTextValidation:
    def __init__(self, language="hi"):
        self.language = language
        self.typo_map = self._get_typo_map(language)
    
    def _get_typo_map(self, language):
        maps = {
            "hi": {"mausm": "मौसम", "samay": "समय", "aaj": "आज", "kse": "कैसे", "nmste": "नमस्ते", "ka": "का"},
            "kn": {"havama": "ಹವಾಮಾನ", "samya": "ಸಮಯ"},
            "te": {"vatavra": "వాతావరణం", "samya": "సమయం"}
        }
        return maps.get(language, {})
    
    def process(self, text):
        if not isinstance(text, str):
            return ""
        try:
            text = re.sub(r"\s+", " ", text.strip())
            text = unicodedata.normalize("NFKD", text)
            words = text.split()
            corrected_words = []
            for word in words:
                lower_word = word.lower()
                corrected = self.typo_map.get(lower_word, word)
                corrected_words.append(corrected)
            return " ".join(corrected_words).strip()
        except:
            return re.sub(r"\s+", " ", text.strip())

def process_text(text, language="hi"):
    return Stage1BTextValidation(language).process(text)
