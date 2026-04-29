import feedparser
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}


# ======================
# RSS SOURCE (أساسي)
# ======================
def get_rss(url):
    try:
        feed = feedparser.parse(url)

        return [
            {
                "title": entry.title,
                "link": entry.link,
                "source": url
            }
            for entry in feed.entries
        ]
    except:
        return []


# ======================
# GOVERNMENT / E-TENDERS (RSS بدل scraping)
# ======================
def etenders():
    print("🏛️ Fetching government tenders (RSS)...")

    rss_feeds = [
        # هنحط مصادر حقيقية لاحقًا (أو بوابات تدعم RSS)
        "https://feeds.feedburner.com/ExampleConstructionRSS"
    ]

    data = []

    for rss in rss_feeds:
        print("📡 RSS:", rss)
        data += get_rss(rss)

    return data


# ======================
# CONSTRUCTION NEWS SOURCES
# ======================
def search_google():
    print("🌐 Fetching construction news feeds...")

    rss_feeds = [
        "https://feeds.bbci.co.uk/news/rss.xml",  # مثال عام
        "https://www.constructionnews.co.uk/feed/"
    ]

    data = []

    for rss in rss_feeds:
        print("📡 RSS:", rss)
        data += get_rss(rss)

    return data


# ======================
# SCRAPER (احتياطي فقط)
# ======================
def scrape_site(url):
    try:
        print("🔍 Scraping:", url)

        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        results = []

        for tag in soup.find_all(["a", "h1", "h2", "h3", "p"]):
            text = tag.get_text(strip=True)

            if len(text) > 20:
                results.append({
                    "title": text,
                    "link": tag.get("href"),
                    "source": url
                })

        return results

    except Exception as e:
        print("❌ scrape error:", e)
        return []
