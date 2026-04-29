import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========================
# 🏛️ GOVERNMENT / TENDER SITES
# =========================
GOV_SITES = [
    "https://www.tendersinfo.com/global-egypt-tenders.php",
    "https://www.dgmarket.com/tenders",
    "https://www.devbusiness.com",
]

# =========================
# 📰 RSS NEWS
# =========================
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.constructionnews.co.uk/feed/",
    "https://www.globalconstructionreview.com/feed/",
]

# =========================
# 🌍 ARABIC SOURCES
# =========================
ARABIC_FEEDS = [
    "https://www.youm7.com/rss",
    "https://www.albawaba.com/rss.xml",
]


BASE_URL = "https://www.tendersinfo.com"


# =========================
# 🔧 FIX URL
# =========================
def fix_url(href, base):
    if not href:
        return None
    return urljoin(base, href)


# =========================
# 📌 SCRAPE LISTING PAGE
# =========================
def scrape_listing_page(url):
    try:
        print(f"\n🌐 LISTING: {url}")

        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        links = []

        for a in soup.find_all("a"):
            href = fix_url(a.get("href"), url)
            text = a.get_text(strip=True)

            if not href:
                continue

            # نفلتر بس لينكات المناقصات
            if any(x in href.lower() for x in ["tender", "procurement", "bid"]):
                links.append(href)

        print(f"📌 LISTINGS FOUND: {len(links)}")
        return list(set(links))

    except Exception as e:
        print(f"❌ LISTING ERROR: {e}")
        return []


# =========================
# 📄 SCRAPE DETAIL PAGE
# =========================
def scrape_detail(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.find("h1")
        title = title.get_text(strip=True) if title else ""

        return {
            "title": title,
            "link": url,
            "source": "tender_site",
            "full_text": soup.get_text(" ", strip=True)
        }

    except:
        return None


# =========================
# 🏛️ GOVERNMENT TENDERS
# =========================
def get_government_tenders():
    print("\n🏛️ GOVERNMENT TENDERS")

    all_tenders = []

    for site in GOV_SITES:
        listing_links = scrape_listing_page(site)

        for link in listing_links:
            data = scrape_detail(link)

            if data and data["title"]:
                all_tenders.append(data)
                print(f"✔ TENDER: {data['title'][:80]}")

    return all_tenders


# =========================
# 📡 RSS
# =========================
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


# =========================
# 📰 NEWS
# =========================
def get_news():
    print("\n📰 NEWS SOURCES")

    all_data = []

    for feed in RSS_FEEDS + ARABIC_FEEDS:
        all_data += get_rss(feed)

    return all_data


# =========================
# 🚀 MAIN COLLECTOR
# =========================
def collect_all_sources():
    print("\n🚀 START FULL COLLECTION")

    gov = get_government_tenders()
    news = get_news()

    all_data = gov + news

    print("\n========================")
    print(f"🏛️ GOV: {len(gov)}")
    print(f"📰 NEWS: {len(news)}")
    print(f"📦 TOTAL: {len(all_data)}")
    print("========================")

    return all_data
