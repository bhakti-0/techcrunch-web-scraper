"""
TechCrunch Web Scraper
Scrapes article details using Selenium + BeautifulSoup
"""

import csv
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


# ---------------- CONFIG ---------------- #

URL = "https://techcrunch.com/"
OUTPUT_FILE = "techcrunch_articles.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- DRIVER SETUP ---------------- #

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver


# ---------------- SCRAPER ---------------- #

def scrape_articles(driver, scrolls=2):
    logging.info("Opening TechCrunch website")
    driver.get(URL)

    # Wait longer for real content
    time.sleep(12)

    # Scroll to load more articles
    for i in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # --- BETTER SELECTORS FOR TECHCRUNCH ---
    articles = soup.select("div.wp-block-tc23-post-picker article")

    data = []

    for article in articles:
        try:
            # Title
            title_tag = article.find("h2")
            title = title_tag.text.strip() if title_tag else "N/A"

            # Link
            link = (
                title_tag.find("a")["href"]
                if title_tag and title_tag.find("a")
                else "N/A"
            )

            # Author
            author_tag = article.select_one("a.river-byline__authors")
            author = author_tag.text.strip() if author_tag else "N/A"

            # Date
            date_tag = article.find("time")
            date = date_tag["datetime"] if date_tag else "N/A"

            # Short description
            desc_tag = article.find("p")
            description = desc_tag.text.strip() if desc_tag else "N/A"

            data.append([title, author, date, link, description])

        except Exception as e:
            logging.error(f"Error parsing article: {e}")

    logging.info(f"Scraped {len(data)} articles")
    return data


# ---------------- STORAGE ---------------- #

def save_to_csv(data):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Author", "Date", "URL", "Description"])
        writer.writerows(data)

    logging.info(f"Data saved to {OUTPUT_FILE}")

# ---------------- MAIN ---------------- #

def main():
    driver = setup_driver()
    try:
        articles = scrape_articles(driver)
        if not articles:
            logging.warning("No articles scraped, creating empty CSV")
        save_to_csv(articles)
    except Exception as e:
        logging.error(f"Script failed: {e}")
        save_to_csv([])   # forces CSV creation
    finally:
        driver.quit()
if __name__ == "__main__":
    main()