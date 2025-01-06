# models/base.py
from abc import ABC, abstractmethod

class SentimentModel(ABC):
    @abstractmethod
    def analyze(self, text: str) -> dict:
        pass