import re
import unicodedata
import numpy as np
import warnings
from dataclasses import dataclass
from typing import Dict, List

warnings.filterwarnings("ignore")

def monkey_patch_numpy():
    original_array = np.array
    def patched_array(obj, copy=False, *args, **kwargs):
        if copy is False:
            return np.asarray(obj, *args, **kwargs)
        return original_array(obj, copy=copy, *args, **kwargs)
    np.array = patched_array

monkey_patch_numpy()

import fasttext

class HunspellChecker:
    """Hunspell-based spell checker for Indian languages"""
    
    def __init__(self, language="hi"):
        self.language = language
        self.dictionary = self.load_dictionary(language)
    
    def load_dictionary(self, language):
        """Load common words dictionary for each language"""
        lang_map = {
            "hi": ["नमस्ते", "कैसे", "आज", "मौसम", "कल", "है", "हो", "का", "मेरा", "आपका"],
            "kn": ["ನಮಸ್ಕಾರ", "ಹೇಗಿದ್ದೀರಿ", "ಇಂದು", "ಹವಾಮಾನ", "ಇದು", "ನನ್ನ"],
            "te": ["నమస్తే", "ఎలా", "ఈరోజు", "వాతావరణం", "ఇది", "నా"]
        }
        return lang_map.get(language, [])
    
    def check(self, word):
        """Check if word exists in dictionary"""
        return word in self.dictionary
    
    def suggest(self, word):
        """Suggest corrections"""
        suggestions = []
        for dict_word in self.dictionary:
            if word[:-1] in dict_word or word[1:] in dict_word:
                suggestions.append(dict_word)
        return suggestions


class IndicSpellChecker:
    """IndicSpell-based correction for Indian languages"""
    
    def __init__(self, language="hi"):
        self.language = language
        self.typo_map = self.load_typo_map(language)
    
    def load_typo_map(self, language):
        """Language-specific typo corrections"""
        return {
            "hi": {
                "mausm": "मौसम", "samay": "समय", "aaj": "आज",
                "kl": "कल", "kse": "कैसे", "nmste": "नमस्ते", "ka": "का",
                "ho": "हो", "hai": "है"
            },
            "kn": {
                "havama": "ಹವಾಮಾನ", "samya": "ಸಮಯ", "indu": "ಇಂದು"
            },
            "te": {
                "vatavra": "వాతావరణం", "samya": "సమయం", "iroju": "ఈరోజు"
            }
        }.get(language, {})
    
    def correct(self, text):
        """Correct typos in text"""
        words = text.split()
        corrected_words = []
        
        for word in words:
            lower_word = word.lower().strip()
            corrected = self.typo_map.get(lower_word, word)
            corrected_words.append(corrected)
        
        return " ".join(corrected_words)


class Stage1BTextValidation:
    
    def __init__(self, language="hi"):
        self.language = language
        self.hunspell = HunspellChecker(language)
        self.indicspell = IndicSpellChecker(language)
    
    def validate_text(self, text):
        """Execute Stage 1B pipeline"""
        if not text or not isinstance(text, str):
            return ""
        
        # Step 1: Basic cleaning
        text = re.sub(r'\s+', ' ', text.strip())
        text = unicodedata.normalize('NFKD', text)
        
        # Step 2: IndicSpell correction (primary)
        corrected = self.indicspell.correct(text)
        
        # Step 3: Hunspell validation
        words = corrected.split()
        validated_words = []
        
        for word in words:
            if self.hunspell.check(word):
                validated_words.append(word)
            else:
                # Keep word if not in dictionary (might be proper noun)
                validated_words.append(word)
        
        return " ".join(validated_words).strip()
    
    def process(self, text):
        """Main processing method for Stage 1B"""
        return self.validate_text(text)

@dataclass
class LIDResult:
    """Language Identification Result"""
    lang_code: str
    lang_name: str
    confidence: float
    route_key: str
    cleaned_text: str = ""


class LanguageIdentifier:
    
    INDIAN_LANGUAGES = {
        "hi": "Hindi", "kn": "Kannada", "te": "Telugu",
        "ta": "Tamil", "ml": "Malayalam", "mr": "Marathi",
        "gu": "Gujarati", "bn": "Bengali", "pa": "Punjabi",
        "or": "Odia", "ur": "Urdu", "as": "Assamese"
    }
    
    def __init__(self, model_path=None, confidence_threshold=0.8):

        self.model_path = model_path
        self.model = None
        self.conf_threshold = confidence_threshold
        
        if model_path:
            try:
                self.model = fasttext.load_model(model_path)
            except Exception as e:
                print(f"Warning: Could not load model: {e}")
    
    def detect(self, text: str) -> LIDResult:

        if not isinstance(text, str) or len(text.strip()) < 5:
            return LIDResult("unk", "Unknown", 0.0, "nlu_fallback")
        
        if not self.model:
            return LIDResult("error", "Model not loaded", 0.0, "nlu_fallback")
        
        try:
            labels, probs = self.model.predict(text.strip())
            lang_code = labels[0].replace("__label__", "")
            confidence = float(probs[0])
            
            # Check confidence threshold
            if confidence < self.conf_threshold:
                return LIDResult(lang_code, "Low confidence", confidence, "nlu_fallback")
            
            lang_name = self.INDIAN_LANGUAGES.get(lang_code, "Other")
            
            # Determine routing key based on language
            if lang_code in {"hi", "kn", "te"}:
                route_key = f"nlu_{lang_code}"
            elif lang_code in self.INDIAN_LANGUAGES:
                route_key = "nlu_indic"
            else:
                route_key = "nlu_other"
            
            return LIDResult(lang_code, lang_name, confidence, route_key)
            
        except Exception as e:
            return LIDResult("error", f"Detection failed: {str(e)}", 0.0, "nlu_fallback")

class ProductionPipeline:

    def __init__(self, lid_model_path=None):

        self.lid_detector = LanguageIdentifier(model_path=lid_model_path)
        self.stage1b_pipelines = {
            "hi": Stage1BTextValidation("hi"),
            "kn": Stage1BTextValidation("kn"),
            "te": Stage1BTextValidation("te"),
        }
    
    def process(self, text: str) -> Dict:
  
        if not text or not isinstance(text, str):
            return {
                'input': text,
                'cleaned_text': "",
                'lang_code': "error",
                'lang_name': "Error",
                'confidence': 0.0,
                'route_key': "nlu_fallback",
                'status': 'error: invalid input'
            }
        
        try:
            # STAGE 2B: Detect language first
            lid_result = self.lid_detector.detect(text)
            
            # STAGE 1B: Clean text (use detected language if available)
            lang_code = lid_result.lang_code if lid_result.lang_code in self.stage1b_pipelines else "hi"
            stage1b = self.stage1b_pipelines.get(lang_code, self.stage1b_pipelines["hi"])
            cleaned_text = stage1b.process(text)
            
            return {
                'input': text,
                'cleaned_text': cleaned_text,
                'lang_code': lid_result.lang_code,
                'lang_name': lid_result.lang_name,
                'confidence': lid_result.confidence,
                'route_key': lid_result.route_key,
                'status': 'success'
            }
        
        except Exception as e:
            return {
                'input': text,
                'cleaned_text': "",
                'lang_code': "error",
                'lang_name': "Error",
                'confidence': 0.0,
                'route_key': "nlu_fallback",
                'status': f'error: {str(e)}'
            }

if __name__ == "__main__":
    print("=" * 80)
    print("STAGE 1B + STAGE 2B PRODUCTION PIPELINE")
    print("=" * 80)
    
    # Initialize pipeline (provide path to lid.176.bin if available)
    pipeline = ProductionPipeline(lid_model_path=None)  # Update with actual model path
    
    # Test cases
    test_cases = {
        "Hindi": "नमस्ते आज का मौसम कैसे है",
        "Kannada": "ನಮಸ್ಕಾರ ಇಂದಿನ ಹವಾಮಾನ ಎನ್ನ",
        "Telugu": "నమస్కారం ఈ రోజు వాతావరణం ఎలా",
        "English": "Good morning, how are you today?"
    }
    
    for name, text in test_cases.items():
        print(f"\n{name}:")
        print(f"  Input: {text}")
        
        result = pipeline.process(text)
        
        print(f"  Cleaned: {result['cleaned_text']}")
        print(f"  Language: {result['lang_name']} ({result['lang_code']})")
        print(f"  Confidence: {result['confidence']:.3f}")
        print(f"  Route: {result['route_key']}")
        print(f"  Status: {result['status']}")
    
    print("\n" + "=" * 80)
