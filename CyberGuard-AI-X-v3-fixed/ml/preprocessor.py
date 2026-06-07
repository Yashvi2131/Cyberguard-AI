"""
CyberGuard AI X - Text Preprocessor
Handles text cleaning, tokenization, and feature extraction
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
def download_nltk_data():
    resources = ['stopwords', 'punkt', 'punkt_tab']
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass

download_nltk_data()


class TextPreprocessor:
    def __init__(self):
        self.stop_words = set()
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            pass

    def preprocess(self, text: str) -> str:
        """
        Full preprocessing pipeline:
        1. Lowercase
        2. Remove punctuation
        3. Remove numbers (optional)
        4. Tokenize
        5. Remove stopwords
        6. Rejoin
        """
        if not text or not isinstance(text, str):
            return ""

        # 1. Lowercase
        text = text.lower()

        # 2. Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # 3. Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # 4. Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # 5. Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # 6. Tokenize
        try:
            tokens = word_tokenize(text)
        except Exception:
            tokens = text.split()

        # 7. Remove stopwords and short tokens
        tokens = [t for t in tokens if t not in self.stop_words and len(t) > 2]

        # 8. Rejoin
        return ' '.join(tokens)

    def extract_keywords(self, text: str, top_n: int = 5) -> list:
        """Extract top keywords from text (simple frequency-based)"""
        processed = self.preprocess(text)
        tokens = processed.split()
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_tokens[:top_n]]
