import aiohttp
import asyncio
from typing import List
from bs4 import BeautifulSoup

BASE_URL = "https://letterboxd.com/film/wicked-2024/reviews/page/{}/"

async def fetch(url: str, session: aiohttp.ClientSession) -> str:
    async with session.get(url) as response:
        return await response.text()

def has_reviews(html: str) -> bool:
    """Check if the page contains reviews"""
    soup = BeautifulSoup(html, 'html.parser')
    review_elements = soup.find_all('div', class_='film-detail-content')
    return len(review_elements) > 0

async def find_last_page_with_reviews(base_url: str) -> int:
    """Use binary search to find the last page with reviews."""
    # Initial upper bound guess (change based on your observations)
    upper_bound = 1000
    lower_bound = 1
    last_page_with_reviews = 0

    async with aiohttp.ClientSession() as session:
        while lower_bound <= upper_bound:
            mid_point = (lower_bound + upper_bound) // 2
            url = base_url.format(mid_point)

            # Fetch the page and check if it has reviews
            html = await fetch(url, session)
            if has_reviews(html):
                # If the page has reviews, search higher pages
                last_page_with_reviews = mid_point
                lower_bound = mid_point + 1
            else:
                # If no reviews, search lower pages
                upper_bound = mid_point - 1

    return last_page_with_reviews

async def main():
    last_page_with_reviews = await find_last_page_with_reviews(BASE_URL)
    print(f"The last page with reviews is page {last_page_with_reviews}")

if __name__ == '__main__':
    asyncio.run(main())
