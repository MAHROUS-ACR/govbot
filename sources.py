import requests
import feedparser
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========================
# 🏛️ Government Tender Sites
# =========================
GOV_SITES = [
    "https://etenders.gov.eg",
    "https://www.fbo.gov",
    "https://www.tendersinfo.com",
    "https://www.devbusiness.com",
    "https://www.dgmarket.com/tenders",
]

# =========================
# 📰 RSS News Sources (Construction + Economy)
# =========================
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.constructionnews.co.uk/feed/",
    "https://www.globalconstructionreview.com/feed/",
    "https://www.devex.com/feed/news",
    "https://www.worldbank.org/en/news/all?format=rss",
]

# =========================
# 🌍 Arabic + Local News
# =========================
ARABIC_FEEDS = [
    "https://www.albawaba.com/rss.xml",
    "https://www.masrawy.com/rss/rssfeeds",
    "https://www.youm7.com/rss",
]

# =========================
# 📌 Scraper for HTML sites
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

            if title and len(title) > 10:
                results.append({
                    "title": title,
                    "link": link,
                    "source": url
                })

        print(f"📥 FOUND: {len(results)} from {url}")
        return results

    except Exception as e:
        print(f"❌ ERROR scraping {url}: {e}")
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
                "title": e.title,
                "link": e.link,
                "source": url
            })

        print(f"📥 RSS ITEMS: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ RSS ERROR {url}: {e}")
        return []

# =========================
# 🏛️ Government Tenders Collector
# =========================
def get_government_tenders():
    print("🏛️ COLLECTING GOVERNMENT TENDERS...")
    all_data = []

    for site in GOV_SITES:
        all_data.extend(scrape_site(site))

    return all_data

# =========================
# 📰 News Collector
# =========================
def get_news():
    print("📰 COLLECTING NEWS FEEDS...")
    all_data = []

    for feed in RSS_FEEDS + ARABIC_FEEDS:
        all_data.extend(get_rss(feed))

    return all_data

# =========================
# 🧠 Main Collector
# =========================
def collect_all_sources():
    print("🚀 START COLLECTING ALL SOURCES")

    gov = get_government_tenders()
    news = get_news()

    all_results = gov + news

    print("=" * 40)
    print(f"📊 GOV: {len(gov)}")
    print(f"📰 NEWS: {len(news)}")
    print(f"📦 TOTAL: {len(all_results)}")
    print("=" * 40)

    return all_results
