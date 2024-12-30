from dataclasses import dataclass
from datetime import date

@dataclass
class Review:
    username: str
    score: float
    review: str
    date: date
