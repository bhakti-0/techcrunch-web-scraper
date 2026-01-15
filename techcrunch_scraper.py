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
    return webdriver.Chrome(options=options)

# ---------------- SCRAPER ---------------- #

def scrape_articles(driver, scrolls=3):
    logging.info("Opening TechCrunch website")
    driver.get(URL)
    time.sleep(5)

    for i in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    articles = soup.select("article")

    data = []

    for article in articles:
        try:
            title = article.find("h2")
            title_text = title.text.strip() if title else "N/A"

            link = title.find("a")["href"] if title and title.find("a") else "N/A"

            author = article.find("a", class_="river-byline__authors")
            author_text = author.text.strip() if author else "N/A"

            date = article.find("time")
            date_text = date["datetime"] if date else "N/A"

            description = article.find("p")
            desc_text = description.text.strip() if description else "N/A"

            data.append([
                title_text,
                author_text,
                date_text,
                link,
                desc_text
            ])

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
        save_to_csv(articles)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
