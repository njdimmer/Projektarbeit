from .cleaning import preprocess_reviews
from .vader import analyze_reviews

def process_reviews(reviews):
    cleaned_reviews = preprocess_reviews(reviews)
    sentiments = analyze_reviews(cleaned_reviews)
    return sentiments