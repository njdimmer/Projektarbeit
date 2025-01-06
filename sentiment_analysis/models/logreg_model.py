# models/logreg_model.py
import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

from .base import SentimentModel

class LogRegModel(SentimentModel):
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_model()
    
    def load_model(self):
        """Load and verify model and vectorizer"""
        try:
            model_path = 'assets/models/sentiment_model.joblib'
            vectorizer_path = 'assets/models/tfidf_vectorizer.joblib'
            
            if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
                raise FileNotFoundError("Model or vectorizer file not found")
            
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            
            if not isinstance(self.model, LogisticRegression):
                raise TypeError("Loaded model is not a LogisticRegression model")
            if not isinstance(self.vectorizer, TfidfVectorizer):
                raise TypeError("Loaded vectorizer is not a TfidfVectorizer")
                
        except Exception as e:
            raise RuntimeError(f"Error loading model: {str(e)}")
    
    def analyze(self, text: str) -> dict:
        """
        Analyze text and return vaderSentiment-like sentiment scores
        Returns: {'neg': float, 'pos': float, 'compound': float}
        """
        if not self.model or not self.vectorizer:
            raise RuntimeError("Model not properly initialized")
            
        text_vector = self.vectorizer.transform([text])
        
        proba = self.model.predict_proba(text_vector)[0]
        neg = proba[0]
        pos = proba[1]
        
        compound = pos - neg

        return {
            'neg': round(neg, 3),
            'pos': round(pos, 3),
            'compound': round(compound, 3)
        }

if __name__ == '__main__':
    try:
        model = LogRegModel()
        text = 'I love the weather today'
        result = model.analyze(text)
        print(result)
    except Exception as e:
        print(f"Error: {e}")