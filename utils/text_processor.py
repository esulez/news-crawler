"""Text processing utilities for article deduplication and clustering."""

import re
import string
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class TextProcessor:
    """Process text for similarity comparison."""
    
    def __init__(self, min_df: int = 1, max_df: float = 1.0, ngram_range: tuple = (1, 2)):
        """Initialize the text processor."""
        self.min_df = min_df
        self.max_df = max_df
        self.ngram_range = ngram_range
        self.vectorizer = TfidfVectorizer(
            min_df=min_df,
            max_df=max_df,
            ngram_range=ngram_range,
            stop_words='english',
            lowercase=True,
        )
        self._is_fitted = False
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for similarity comparison."""
        if not text:
            return ''
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters but keep numbers in version strings
        text = re.sub(r'[^\w\s.]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Use scikit-learn's stop words
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        stop_words = set(ENGLISH_STOP_WORDS)
        words = text.split()
        # Keep words that are not stop words and have length > 2
        words = [w for w in words if w.lower() not in stop_words and len(w) > 2]
        
        return ' '.join(words)
    
    def fit(self, texts: List[str]):
        """Fit the vectorizer on a list of texts."""
        processed_texts = [self.preprocess_text(t) for t in texts]
        self.vectorizer.fit(processed_texts)
        self._is_fitted = True
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform texts to TF-IDF vectors."""
        processed_texts = [self.preprocess_text(t) for t in texts]
        return self.vectorizer.transform(processed_texts)
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """Fit and transform texts."""
        processed_texts = [self.preprocess_text(t) for t in texts]
        return self.vectorizer.fit_transform(processed_texts)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        if not self._is_fitted:
            # Fit on both texts if not fitted
            self.fit([text1, text2])
        
        vectors = self.transform([text1, text2])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])
        return similarity[0][0]
    
    def calculate_batch_similarity(self, texts: List[str]) -> np.ndarray:
        """Calculate pairwise similarity matrix for a list of texts."""
        vectors = self.fit_transform(texts)
        return cosine_similarity(vectors)
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extract top keywords from text."""
        if not text:
            return []
        
        processed = self.preprocess_text(text)
        if not processed:
            return []
        
        # Simple keyword extraction based on word frequency
        words = processed.split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
    
    def get_topic_from_text(self, text: str, max_length: int = 100) -> str:
        """Generate a topic string from text."""
        if not text:
            return ""
        
        # Extract keywords
        keywords = self.extract_keywords(text, top_n=10)
        
        # Find the most meaningful sentence
        sentences = re.split(r'[.!?]', text)
        best_sentence = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > len(best_sentence) and len(sentence) <= max_length:
                # Check if sentence contains keywords
                if any(keyword.lower() in sentence.lower() for keyword in keywords):
                    best_sentence = sentence
        
        if best_sentence:
            return best_sentence[:max_length]
        
        # Fallback to keywords
        return ' '.join(keywords)[:max_length]
