import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Tuple
import time

from .model import Review
from .db import load_reviews, save_reviews

BASE_URL = "https://letterboxd.com/film"

async def scrape_single_page(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> Tuple[List[Review], bool]:
    """Scrape a single page of reviews"""
    async with semaphore:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return [], False
                    
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                reviews = []
                review_elements = soup.find_all('li', class_='film-detail')
                
                if not review_elements:
                    return [], False
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return [], False
        
        for element in review_elements:
            try:
                avatar_element = element.find('a', class_='avatar')
                username = avatar_element.get('href', '').strip() if avatar_element else "Unknown"
                stars = element.find('span', class_='rating')
                stars = stars.text.strip() if stars else "No rating"
                comment = element.find('div', class_='body-text').text.strip()
                date_element = element.find('span', class_='_nobr')
                date = date_element.text.strip() if date_element else None

                raw_review = {
                    'username': username,
                    'stars': stars,
                    'comment': comment,
                    'date': date
                }
                reviews.append(process_review(raw_review))
            except Exception as e:
                print(f"Error processing review: {e}")
                continue
        return reviews, True

def process_review(raw_review: dict) -> Review:
    """Process raw review data into a Review object"""
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

async def async_scrape_reviews(base_url: str, movie_name: str, max_concurrent: int = 5):
    """Scrape all reviews for a movie asynchronously"""
    REVIEWS_PER_PAGE = 12
    existing_reviews = load_reviews(movie_name)
    existing_reviews_count = len(existing_reviews)
    
    complete_pages = existing_reviews_count // REVIEWS_PER_PAGE
    reviews_on_last_page = existing_reviews_count % REVIEWS_PER_PAGE
    start_page = complete_pages + 1
    
    all_reviews = existing_reviews[:]
    
    print(f"Starting from page {start_page} (found {len(all_reviews)} existing reviews)")
    
    semaphore = asyncio.Semaphore(max_concurrent)
    timeout = aiohttp.ClientTimeout(total=10)
    connector = aiohttp.TCPConnector(limit=max_concurrent)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers) as session:
        first_page_url = f"{base_url}/{movie_name}/reviews/page/{start_page}/"
        first_page_reviews, has_next = await scrape_single_page(session, first_page_url, semaphore)
        
        if first_page_reviews:
            all_reviews.extend(first_page_reviews[reviews_on_last_page:])
        
        if not has_next:
            return all_reviews

        tasks = []
        for page in range(start_page + 1, start_page + max_concurrent + 1):
            page_url = f"{base_url}/{movie_name}/reviews/page/{page}/"
            task = asyncio.create_task(scrape_single_page(session, page_url, semaphore))
            tasks.append((page, task))
        
        while tasks:
            new_tasks = []
            for page_num, task in tasks:
                try:
                    reviews, has_more = await task
                    if reviews:
                        all_reviews.extend(reviews)
                    
                    if has_more:
                        next_page = page_num + max_concurrent
                        page_url = f"{base_url}/{movie_name}/reviews/page/{next_page}/"
                        new_task = asyncio.create_task(scrape_single_page(session, page_url, semaphore))
                        new_tasks.append((next_page, new_task))
                except Exception as e:
                    print(f"Error processing page {page_num}: {e}")
            
            tasks = new_tasks
            if not tasks:
                break
    
    return all_reviews

if __name__ == "__main__":
    MOVIE_NAME = "wicked-2024"
    
    start_time = time.time()
    reviews = asyncio.run(async_scrape_reviews(BASE_URL, MOVIE_NAME))
    save_reviews(reviews, MOVIE_NAME)
    end_time = time.time()
    
    print(f"Scraped {len(reviews)} reviews in {end_time - start_time:.2f} seconds")
    print(f"Saved to 'db/letterboxd/raw/{MOVIE_NAME}.csv'")