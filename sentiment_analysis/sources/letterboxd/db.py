import csv
import os

from model import Review

def load_reviews(movie_name: str) -> list[Review]:
    csv_file_path = f'db/letterboxd/raw/{movie_name}.csv'
    if not os.path.exists(csv_file_path):
        return []

    reviews = []
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            review = Review(
                username=row['username'],
                score=float(row['score']),
                review=row['review'],
                date=row['date']
            )
            reviews.append(review)
    return reviews

def save_reviews(data: list[Review], movie_name: str):
    csv_file_path = f'db/letterboxd/raw/{movie_name}.csv'
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    keys = data[0].__annotations__.keys() if data else []
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for review in data:
            writer.writerow({key: getattr(review, key) for key in keys})
    print(f"Data saved to {csv_file_path}")