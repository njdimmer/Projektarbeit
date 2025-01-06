# workflow/sentiment_analyzer.py
import pandas as pd
from typing import Dict, List
from ..models import get_model

class SentimentAnalyzer:
    def __init__(self, model_name: str = 'vader'):
        """Initialize with either 'vader' or 'logreg' model"""
        self.model = get_model(model_name)
        self.model_type = model_name

    def analyze_reviews(self, csv_path: str) -> Dict:
        """Analyze all reviews in a CSV file and return aggregate metrics"""
        df = pd.read_csv(csv_path)
        reviews = df['review'].tolist()
        scores = df['score'].tolist()
        
        sentiments = [self.model.analyze(review) for review in reviews]
        compounds = [s['compound'] for s in sentiments]
        normalized_compounds = [(c + 1) / 2 for c in compounds]

        comparison = {
            'review_scores': scores,
            'sentiment_scores': normalized_compounds,
            'correlation': round(pd.Series(scores).corr(pd.Series(normalized_compounds)), 3),
            'mae': round(sum(abs(s - c) for s, c in zip(scores, normalized_compounds)) / len(scores), 3),
            'rmse': round((sum((s - c) ** 2 for s, c in zip(scores, normalized_compounds)) / len(scores)) ** 0.5, 3)
        }

        results = (self._aggregate_vader_sentiments(sentiments) 
                  if self.model_type == 'vader' 
                  else self._aggregate_logreg_sentiments(sentiments))
        
        results['comparison'] = comparison
        return results

    def _aggregate_vader_sentiments(self, sentiments: List[Dict]) -> Dict:
        """Aggregate VADER sentiment scores with original thresholds"""
        total = len(sentiments)
        
        avg_pos = sum(s['pos'] for s in sentiments) / total
        avg_neg = sum(s['neg'] for s in sentiments) / total
        avg_neu = sum(s['neu'] for s in sentiments) / total
        avg_compound = sum(s['compound'] for s in sentiments) / total
        
        positive_count = sum(1 for s in sentiments if s['compound'] >= 0.05)
        negative_count = sum(1 for s in sentiments if s['compound'] <= -0.05)
        neutral_count = total - positive_count - negative_count
        
        return {
            'total_reviews': total,
            'average_scores': {
                'positive': round(avg_pos, 3),
                'negative': round(avg_neg, 3),
                'neutral': round(avg_neu, 3),
                'compound': round(avg_compound, 3)
            },
            'sentiment_distribution': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            },
            'sentiment_percentages': {
                'positive': round((positive_count / total) * 100, 2),
                'negative': round((negative_count / total) * 100, 2),
                'neutral': round((neutral_count / total) * 100, 2)
            }
        }

    def _aggregate_logreg_sentiments(self, sentiments: List[Dict]) -> Dict:
        """Aggregate Logistic Regression sentiment scores"""
        total = len(sentiments)
        
        avg_pos = sum(s['pos'] for s in sentiments) / total
        avg_neg = sum(s['neg'] for s in sentiments) / total
        avg_compound = sum(s['compound'] for s in sentiments) / total
        
        positive_count = sum(1 for s in sentiments if s['compound'] > 0)
        negative_count = total - positive_count
        
        return {
            'total_reviews': total,
            'average_scores': {
                'positive': round(avg_pos, 3),
                'negative': round(avg_neg, 3),
                'compound': round(avg_compound, 3)
            },
            'sentiment_distribution': {
                'positive': positive_count,
                'negative': negative_count
            },
            'sentiment_percentages': {
                'positive': round((positive_count / total) * 100, 2),
                'negative': round((negative_count / total) * 100, 2)
            }
        }