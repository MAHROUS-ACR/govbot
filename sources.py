import requests
import feedparser
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========================
# 🏛️ Government Tender Sites
# =========================
GOV_SITES = [
    "https://etenders.gov.eg",
    "https://www.tendersinfo.com",
    "https://www.dgmarket.com/tenders",
    "https://www.devbusiness.com",
    "https://www.globaltenders.com",
]

# =========================
# 📰 RSS News (Construction + Economy)
# =========================
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.constructionnews.co.uk/feed/",
    "https://www.globalconstructionreview.com/feed/",
    "https://www.devex.com/feed/news",
]

# =========================
# 🌍 Arabic News
# =========================
ARABIC_FEEDS = [
    "https://www.youm7.com/rss",
    "https://www.masrawy.com/rss/rssfeeds",
]

# =========================
# 📰 Extra News Sites (HTML)
# =========================
NEWS_SITES = [
    "https://www.albawaba.com/rss.xml",
    "https://www.thenationalnews.com/arc/outboundfeeds/rss/",
    "https://www.arabnews.com/rss.xml",
]

# =========================
# 💬 Forums
# =========================
FORUM_SITES = [
    "https://www.skyscrapercity.com/forums/construction.123/",
    "https://www.eng-tips.com/threadminder.cfm",
]

# =========================
# 📱 Social Media Searches
# =========================
SOCIAL_SITES = [
    "https://twitter.com/search?q=construction%20tender",
    "https://twitter.com/search?q=مناقصات%20مقاولات",
    "https://www.linkedin.com/jobs/search/?keywords=construction%20tender",
]

# =========================
# 🔧 HTTP Scraper
# =========================
def scrape_site(url):
    try:
        print(f"🌐 SCRAPING: {url}")

        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        results = []

        for a in soup.find_all("a"):
            title = a.get_text(strip=True)
            link = a.get("href")

            if title and len(title) > 8:
                results.append({
                    "title": title,
                    "link": link,
                    "source": url
                })

        print(f"📥 FOUND: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ SCRAPE ERROR {url}: {e}")
        return []

# =========================
# 📡 RSS Reader
# =========================
def get_rss(url):
    try:
        print(f"📡 RSS: {url}")

        feed = feedparser.parse(url)

        results = []

        for e in feed.entries:
            results.append({
                "title": getattr(e, "title", ""),
                "link": getattr(e, "link", ""),
                "source": url
            })

        print(f"📥 RSS ITEMS: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ RSS ERROR {url}: {e}")
        return []

# =========================
# 🧠 BASIC FILTER
# =========================
KEYWORDS = [
    "مقاولات", "توريد", "إنشاء", "بناء",
    "construction", "tender", "project",
    "bid", "procurement"
]

def is_valid(title):
    if not title:
        return False
    return any(k.lower() in title.lower() for k in KEYWORDS)

# =========================
# 🏛️ GOVERNMENT
# =========================
def etenders():
    print("🏛️ COLLECTING GOVERNMENT TENDERS...")
    data = []

    for site in GOV_SITES:
        data += scrape_site(site)

    return data

# =========================
# 🔍 GOOGLE (simple fallback)
# =========================
def search_google():
    try:
        print("🔍 GOOGLE SEARCH...")

        url = "https://www.google.com/search?q=construction+tenders+projects"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        results = []

        for a in soup.find_all("a"):
            text = a.get_text()

            if text and is_valid(text):
                results.append({
                    "title": text,
                    "source": "google"
                })

        print(f"📥 GOOGLE RESULTS: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ GOOGLE ERROR: {e}")
        return []

# =========================
# 🚀 FULL COLLECTOR
# =========================
def collect_all_sources():
    print("🚀 START COLLECTING ALL SOURCES")

    data = []

    # 🏛️ Government
    for site in GOV_SITES:
        data += scrape_site(site)

    # 📰 RSS
    for feed in RSS_FEEDS + ARABIC_FEEDS:
        data += get_rss(feed)

    # 📰 News sites
    for site in NEWS_SITES:
        data += scrape_site(site)

    # 💬 Forums
    for site in FORUM_SITES:
        data += scrape_site(site)

    # 📱 Social
    for site in SOCIAL_SITES:
        data += scrape_site(site)

    print(f"📦 TOTAL COLLECTED: {len(data)}")

    # optional filter
    filtered = [d for d in data if is_valid(d.get("title", ""))]

    print(f"🧠 AFTER FILTER: {len(filtered)}")

    return filtered
