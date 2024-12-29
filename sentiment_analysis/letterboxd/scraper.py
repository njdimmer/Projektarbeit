import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

from model import Review

def process_review(raw_review: dict) -> Review:
    username = raw_review['username'].replace('/', '')
    score = raw_review['stars'].count('★') + (0.5 if '½' in raw_review['stars'] else 0)
    date = raw_review['date']
    if date:
        date = datetime.strptime(date.strip(), '%d %b %Y').date()
    
    return Review(
        username=username,
        score=score,
        review=raw_review['comment'].strip(),
        date=date
    )

async def scrape_reviews(session, page_url: str) -> list[Review]:
    reviews = []
    async with session.get(page_url) as response:
        html_content = await response.text()
        soup = BeautifulSoup(html_content, 'html.parser')

        review_elements = soup.find_all('li', class_='film-detail')
        for element in review_elements:
            username = element.find('a', class_='avatar').get('href', '').strip()
            stars = element.find('span', class_='rating')
            stars = stars.text.strip() if stars else "No rating"
            comment = element.find('div', class_='body-text').text.strip()
            date_element = element.find('span', class_='_nobr')
            date = date_element.text.strip() if date_element else None

            raw_review = {'username': username, 'stars': stars, 'comment': comment, 'date': date}
            reviews.append(process_review(raw_review))

    return reviews

async def async_scrape_reviews(base_url, movie_name, start_page, end_page):
    all_reviews = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page in range(start_page, end_page + 1):
            page_url = f"{base_url}/{movie_name}/reviews/page/{page}/"
            tasks.append(scrape_reviews(session, page_url))
        
        results = await asyncio.gather(*tasks)
        for result in results:
            all_reviews.extend(result)
    
    return all_reviews

def save_reviews_to_csv(data: list[Review], movie_name: str):
    csv_file_path = f'db/letterboxd/{movie_name}.csv'
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    keys = data[0].__annotations__.keys() if data else []
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for review in data:
            writer.writerow({key: getattr(review, key) for key in keys})
    print(f"Data saved to {csv_file_path}")


if __name__ == "__main__":
    MOVIE_NAME = "wicked-2024"
    BASE_URL = "https://letterboxd.com/film"
    START_PAGE = 1
    END_PAGE = 256
    
    reviews = asyncio.run(async_scrape_reviews(BASE_URL, MOVIE_NAME, START_PAGE, END_PAGE))
    save_reviews_to_csv(reviews, MOVIE_NAME)
    print(f"Scraped {len(reviews)} reviews and saved to 'db/letterboxd/{MOVIE_NAME}.csv'")
