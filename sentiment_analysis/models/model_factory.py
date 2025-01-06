# models/model_factory.py
from sentiment_analysis.models import VaderModel, LogRegModel
from sentiment_analysis.models.base import SentimentModel

def get_model(model_name: str) -> SentimentModel:
    models = {
        'vader': VaderModel,
        'logreg': LogRegModel
    }
    return models[model_name]()