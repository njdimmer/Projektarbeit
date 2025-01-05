import pickle
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import emoji
import pandas as pd

class SentimentModel:
    def __init__(self):
        self.tfidf = None
        self.model = None
    
    def load_model(self, model_path='assets/models/sentiment_model.joblib', vectorizer_path='assets/models/tfidf_vectorizer.joblib'):
        """Load the trained model and vectorizer"""
        self.model = joblib.load(model_path)
        self.tfidf = joblib.load(vectorizer_path)
        print("Model and vectorizer loaded successfully")

    def predict(self, text):
        """Predict sentiment for a given text"""
        if self.model is None or self.tfidf is None:
            raise ValueError("Model and vectorizer must be loaded before prediction")
        
        # Transform the text using the loaded vectorizer
        text_vector = self.tfidf.transform([text])
        
        # Make prediction
        prediction = self.model.predict(text_vector)[0]
        probability = self.model.predict_proba(text_vector)[0]
        
        return {
            'text': text,
            'sentiment': 'Positive' if prediction == 1 else 'Negative',
            'confidence': float(max(probability)),
            'prediction': int(prediction)
        }
    
    def aggregate_sentiment(self, csv_path):
        try:
            data = pd.read_csv(csv_path)
            
            if 'review' not in data.columns or 'score' not in data.columns:
                raise ValueError("CSV file must contain 'review' and 'score' columns.")
            
            total_reviews = len(data)
            positive_count = 0
            total_confidence = 0.0
            star_positive_count = 0

            for _, row in data.iterrows():
                review = row['review']
                star_rating = row['score']

                result = self.predict(review)
                if result['sentiment'] == 'Positive':
                    positive_count += 1
                total_confidence += result['confidence']

                if star_rating >= 0.35:
                    star_positive_count += 1

            positive_percentage = (positive_count / total_reviews) * 100
            average_confidence = total_confidence / total_reviews
            star_positive_percentage = (star_positive_count / total_reviews) * 100

            comparison = {
                'positive_sentiment_percentage': positive_percentage,
                'star_positive_percentage': star_positive_percentage,
                'difference_percentage': positive_percentage - star_positive_percentage
            }

            return {
                'total_reviews': total_reviews,
                'positive_reviews': positive_count,
                'positive_percentage': positive_percentage,
                'average_confidence': average_confidence,
                'star_positive_percentage': star_positive_percentage,
                'comparison': comparison
            }
        except FileNotFoundError:
            print(f"Error: File '{csv_path}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

# Example usage:
if __name__ == "__main__":
    sentiment_model = SentimentModel()
    
    try:
        sentiment_model.load_model()
        
        csv_file = "db/letterboxd/clean/wicked-2024.csv"
        aggregate_results = sentiment_model.aggregate_sentiment(csv_file)
        
        print("\nAggregate Sentiment Results:")
        print(f"Total Reviews: {aggregate_results['total_reviews']}")
        print(f"Positive Reviews (Sentiment): {aggregate_results['positive_reviews']}")
        print(f"Positive Sentiment Percentage: {aggregate_results['positive_percentage']:.2f}%")
        print(f"Average Confidence: {aggregate_results['average_confidence']:.2f}")
        print(f"Star Positive Percentage: {aggregate_results['star_positive_percentage']:.2f}%")
        print(f"Sentiment vs Star Rating Difference: {aggregate_results['comparison']['difference_percentage']:.2f}%")
        
    except FileNotFoundError:
        print("Model files not found. Please ensure the model and vectorizer are saved in the correct paths.")
