import requests
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========================
# 🌐 GOVERNMENT + TENDER SOURCES
# =========================
GOV_SITES = [
    "https://etenders.gov.eg",
    "https://www.dgmarket.com/tenders",
    "https://www.devbusiness.com",
    "https://www.tendersinfo.com",
]

# =========================
# 📰 RSS SOURCES (NEWS + CONSTRUCTION)
# =========================
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.constructionnews.co.uk/feed/",
    "https://www.globalconstructionreview.com/feed/",
]


# =========================
# 🔥 CLEAN SCRAPER (IMPORTANT FIX)
# =========================
def scrape_site(url):
    try:
        print(f"🌐 SCRAPING: {url}")

        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        results = []

        # ❌ تجاهل menus / nav / footer
        bad_keywords = ["menu", "home", "about", "contact", "login", "register"]

        for a in soup.select("a[href]"):
            title = a.get_text(" ", strip=True)
            href = a.get("href")

            if not title or len(title) < 15:
                continue

            if any(b in title.lower() for b in bad_keywords):
                continue

            full_link = urljoin(url, href)

            results.append({
                "title": title,
                "link": full_link,
                "source": url
            })

        print(f"📥 FOUND: {len(results)} items")
        return results

    except Exception as e:
        print(f"❌ ERROR {url}: {e}")
        return []


# =========================
# 📡 RSS
# =========================
def get_rss(url):
    try:
        print(f"📡 RSS: {url}")

        feed = feedparser.parse(url)

        return [
            {
                "title": e.title,
                "link": e.link,
                "source": url
            }
            for e in feed.entries
            if hasattr(e, "title")
        ]

    except Exception as e:
        print(f"❌ RSS ERROR: {e}")
        return []


# =========================
# 🏛️ GOV TENDERS (ALL)
# =========================
def get_government_tenders():
    print("🏛️ COLLECTING GOV TENDERS...")
    all_data = []

    for site in GOV_SITES:
        all_data.extend(scrape_site(site))

    return all_data


# =========================
# 📰 NEWS
# =========================
def get_news():
    print("📰 COLLECTING NEWS...")
    all_data = []

    for feed in RSS_FEEDS:
        all_data.extend(get_rss(feed))

    return all_data


# =========================
# 🚀 MASTER COLLECTOR
# =========================
def collect_all_sources():
    print("🚀 MASTER COLLECTOR START")

    gov = get_government_tenders()
    news = get_news()

    return gov + news
