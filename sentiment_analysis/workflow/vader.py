from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def vader_sentiment_analysis(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    return sentiment

def analyze_reviews(reviews):
    sentiments = []
    for review in reviews:
        sentiment = vader_sentiment_analysis(review)
        sentiments.append(sentiment)
    return sentiments