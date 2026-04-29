import requests
from bs4 import BeautifulSoup
import feedparser

HEADERS = {"User-Agent": "Mozilla/5.0"}


# 🟢 مواقع عامة
def scrape_site(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        results = []

        for a in soup.find_all("a"):
            text = a.get_text(strip=True)

            if text:
                results.append({
                    "title": text,
                    "link": a.get("href"),
                    "source": url
                })

        return results

    except:
        return []


# 🟣 RSS
def get_rss(url):
    try:
        feed = feedparser.parse(url)

        return [
            {
                "title": e.title,
                "link": e.link,
                "source": url
            }
            for e in feed.entries
        ]

    except:
        return []


# 🔵 Google بسيط
def search_google():
    try:
        url = "https://www.google.com/search?q=مناقصات+مقاولات+توريدات"
        res = requests.get(url, headers=HEADERS)

        soup = BeautifulSoup(res.text, "html.parser")

        results = []

        for a in soup.find_all("a"):
            text = a.get_text()

            if "مناقصة" in text:
                results.append({
                    "title": text,
                    "source": "google"
                })

        return results

    except:
        return []


# 🏛️ مصدر حكومي
def etenders():
    return scrape_site("https://etenders.gov.eg")
