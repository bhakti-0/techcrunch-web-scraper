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


def save_raw_html(driver, filename="techcrunch_page.html"):
    html = driver.page_source

    # Normalize before saving
    html = unicodedata.normalize("NFKC", html)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    logging.info(f"Raw HTML saved to {filename} in UTF-8")
import unicodedata

def clean_text(text):
    """
    Normalize and clean scraped text to avoid encoding issues.
    Converts smart quotes, special dashes, and weird unicode characters
    into safe, standard equivalents.
    """
    if not text:
        return ""

    # Normalize unicode characters to standard form
    text = unicodedata.normalize("NFKC", text)

    # Replace common problematic characters
    replacements = {
        "’": "'",
        "“": '"',
        "”": '"',
        "—": "-",
        "–": "-",
        "…": "...",
        " ": " ",   # non-breaking space
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text.strip()


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

    time.sleep(12)

    for _ in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

    # Save what Selenium actually received
    save_raw_html(driver)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    articles = soup.find_all("article")

    data = []

    for article in articles:
        try:
            title_tag = article.find(["h1", "h2"])
            title = title_tag.text.strip() if title_tag else "N/A"

            link = (
                title_tag.find("a")["href"]
                if title_tag and title_tag.find("a")
                else "N/A"
            )

            date_tag = article.find("time")
            date = date_tag["datetime"] if date_tag else "N/A"

            desc_tag = article.find("p")
            description = desc_tag.text.strip() if desc_tag else "N/A"

            if title and link != "N/A":
                data.append([
    clean_text(title),
   
    clean_text(date),
    clean_text(link),
    clean_text(description)
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

        for row in data:
            # Ensure every value is UTF-8 safe before writing
            safe_row = [clean_text(cell) for cell in row]
            writer.writerow(safe_row)

    logging.info(f"Data saved to {OUTPUT_FILE} in UTF-8")


# ---------------- MAIN ---------------- #

def main():
    driver = setup_driver()
    try:
        articles = scrape_articles(driver)
        if not articles:
            logging.warning("No articles scraped — writing empty CSV")
        save_to_csv(articles)
    except Exception as e:
        logging.error(f"Script failed: {e}")
        save_to_csv([])   # ensures file exists
    finally:
        driver.quit()

if __name__ == "__main__":
    main()