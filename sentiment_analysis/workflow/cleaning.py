import re

def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

def preprocess_reviews(reviews):
    cleaned_reviews = []
    for review in reviews:
        cleaned_review = clean_text(review)
        cleaned_reviews.append(cleaned_review)
    return cleaned_reviews
