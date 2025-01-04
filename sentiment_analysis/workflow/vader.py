from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def vader_sentiment_analysis(text):
    analyzer = SentimentIntensityAnalyzer()
    
    new_words = {
        "garbage": -3.0,
        "absolute garbage": -4.0
    }
    analyzer.lexicon.update(new_words)

    sentiment = analyzer.polarity_scores(text)
    return sentiment

def analyze_reviews(reviews):
    sentiments = []
    for review in reviews:
        sentiment = vader_sentiment_analysis(review)
        sentiments.append(sentiment)
    return sentiments

def aggregate_sentiments(sentiments):
    total_sentiment = {
        'pos': 0,
        'neu': 0,
        'neg': 0,
        'compound': 0
    }
    for sentiment in sentiments:
        total_sentiment['pos'] += sentiment['pos']
        total_sentiment['neu'] += sentiment['neu']
        total_sentiment['neg'] += sentiment['neg']
        total_sentiment['compound'] += sentiment['compound']
    
    count = len(sentiments)
    if count > 0:
        total_sentiment = {k: v / count for k, v in total_sentiment.items()}
    
    return total_sentiment