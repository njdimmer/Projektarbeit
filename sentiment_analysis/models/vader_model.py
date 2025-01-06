# models/vader_model.py
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .base import SentimentModel

class VaderModel(SentimentModel):
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> dict:
        return self.analyzer.polarity_scores(text)
    
if __name__ == '__main__':
    text = 'I love the weather today'
    model = VaderModel()
    print(model.analyze(text))