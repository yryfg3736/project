import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
import multiprocessing
import nest_asyncio
from database.db_connection import get_collection

nest_asyncio.apply()

def selenium_scraper(url, result_queue):
    firefox_options = Options()
    firefox_options.add_argument("--headless")

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
    try:
        driver.get(url)
        time.sleep(5)  # Allow time for the page to load

        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        tweets = soup.find_all('article', {'role': 'article'})

        tweet_data = []
        for tweet in tweets:
            user_name = tweet.find('span', {'class': 'css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3'})
            user_name = user_name.text if user_name else 'N/A'

            user_photo = tweet.find('img', {'class': 'css-9pa8cd'})
            user_photo = user_photo['src'] if user_photo else 'N/A'
            
            tweet_date = tweet.find('time')
            tweet_date = tweet_date['datetime'] if tweet_date else 'N/A'

            # Updated tweet text extraction
            tweet_text_container = tweet.find('div', {'data-testid': 'tweetText'})
            if tweet_text_container:
                tweet_text_parts = tweet_text_container.find_all(text=True, recursive=True)
                tweet_text = ' '.join(tweet_text_parts).strip()
            else:
                tweet_text = 'N/A'

            tweet_media_find = tweet.find_all('div', {'class': 'css-175oi2r r-9aw3ui r-1s2bzr4'})
            media = []

            for media_item in tweet_media_find:
                media_items = media_item.find_all('img')
                media.extend([item['src'] for item in media_items])

            tweet_statistic_find = tweet.find('div', {'class': 'css-175oi2r r-1kbdv8c r-18u37iz r-1wtj0ep r-1ye8kvj r-1s2bzr4'})
            tweet_statistic = tweet_statistic_find['aria-label'] if tweet_statistic_find else 'N/A'

            tweet_data.append({
                "avatar": user_photo,
                "user": user_name,
                "date": tweet_date,
                "tweet": tweet_text,
                "media": media,
                "statistic": tweet_statistic,
            })

        result_queue.put(tweet_data)
    except (TimeoutException, NoSuchElementException) as e:
        driver.quit()
        print(f"Error scraping {url}: {e}")

async def fetch_with_selenium(urls):
    manager = multiprocessing.Manager()
    result_queue = manager.Queue()

    processes = []
    for url in urls:
        process = multiprocessing.Process(target=selenium_scraper, args=(url, result_queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = []
    while not result_queue.empty():
        results.extend(result_queue.get())

    # Store results in MongoDB
    collection = get_collection('tweets')
    if results:
        for tweet in results:
            collection.update_one(
                {"user": tweet['user'], "date": tweet['date'], "tweet": tweet['tweet']},  # Unique constraint for update
                {"$set": tweet},
                upsert=True
            )

    return results
