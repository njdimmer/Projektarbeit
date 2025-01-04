import pickle
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import emoji
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Download required NLTK data
nltk.download('stopwords')
nltk.download('wordnet')

class SentimentModel:
    def __init__(self):
        self.tfidf = None
        self.model = None
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english'))
    
    def extract_emojis(self, text):
        """Extract emojis and return them with descriptions"""
        emoji_list = []
        for char in text:
            if char in emoji.EMOJI_DATA:
                emoji_name = emoji.EMOJI_DATA[char]['en'].replace(':', '').replace('_', ' ')
                emoji_list.append(f"{char} {emoji_name}")
        return ' '.join(emoji_list) if emoji_list else ''

    def clean_text(self, text):
        """Clean text while preserving emojis"""
        # Extract emojis and their descriptions
        emoji_content = self.extract_emojis(text)
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        # Remove non-letters and non-digits, but keep emojis
        text = ''.join([char for char in text if char.isalnum() or char.isspace() or char in emoji.EMOJI_DATA])
        
        # Combine cleaned text with emoji descriptions
        return f"{text.lower()} {emoji_content}".strip()

    def remove_stopwords(self, text):
        """Remove stopwords but keep emoji descriptions"""
        words = text.split()
        filtered = [word for word in words if word not in self.stopwords or 
                   any(char in emoji.EMOJI_DATA for char in word)]
        return " ".join(filtered)

    def lemmatize_text(self, text):
        """Lemmatize while preserving emoji content"""
        words = text.split()
        lemmatized = [self.lemmatizer.lemmatize(word) 
                     if not any(char in emoji.EMOJI_DATA for char in word) 
                     else word for word in words]
        return ' '.join(lemmatized)

    def preprocess_text(self, text):
        """Apply all preprocessing steps"""
        text = self.clean_text(text)
        text = self.remove_stopwords(text)
        text = self.lemmatize_text(text)
        return text

    def save_model(self, model_path='sentiment_model.joblib', vectorizer_path='tfidf_vectorizer.joblib'):
        """Save the trained model and vectorizer"""
        if self.model is None or self.tfidf is None:
            raise ValueError("Model and vectorizer must be trained before saving")
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.tfidf, vectorizer_path)
        print(f"Model saved to {model_path}")
        print(f"Vectorizer saved to {vectorizer_path}")

    def load_model(self, model_path='sentiment_model.joblib', vectorizer_path='tfidf_vectorizer.joblib'):
        """Load the trained model and vectorizer"""
        self.model = joblib.load(model_path)
        self.tfidf = joblib.load(vectorizer_path)
        print("Model and vectorizer loaded successfully")

    def predict(self, text):
        """Predict sentiment for a given text"""
        if self.model is None or self.tfidf is None:
            raise ValueError("Model and vectorizer must be loaded before prediction")
        
        # Preprocess the text
        processed_text = self.preprocess_text(text)
        
        # Transform the text
        text_vector = self.tfidf.transform([processed_text])
        
        # Make prediction
        prediction = self.model.predict(text_vector)[0]
        probability = self.model.predict_proba(text_vector)[0]
        
        return {
            'text': text,
            'processed_text': processed_text,
            'sentiment': 'Positive' if prediction == 1 else 'Negative',
            'confidence': float(max(probability)),
            'prediction': int(prediction)
        }

# Example usage:
if __name__ == "__main__":
    # Example of how to use the saved model
    sentiment_model = SentimentModel()
    
    try:
        # Load the saved model
        sentiment_model.load_model()
        
        # Test the model
        test_text = "This movie was amazing! 😊 Loved every minute of it! 🎬 ❤️"
        result = sentiment_model.predict(test_text)
        
        print("\nPrediction Results:")
        print(f"Original Text: {result['text']}")
        print(f"Processed Text: {result['processed_text']}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['confidence']:.2f}")
        
    except FileNotFoundError:
        print