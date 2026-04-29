import requests
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========================
# 🌐 SOURCES (FULL)
# =========================
GOV_SITES = [
    "https://etenders.gov.eg",
    "https://www.dgmarket.com/tenders",
    "https://www.devbusiness.com",
    "https://www.tendersinfo.com",
]

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.constructionnews.co.uk/feed/",
    "https://www.globalconstructionreview.com/feed/",
    "https://www.devex.com/feed/news",
]

ARABIC_FEEDS = [
    "https://www.youm7.com/rss",
    "https://www.masrawy.com/rss/rssfeeds",
]

# =========================
# SCRAPER (NO TABS + PDF SUPPORT)
# =========================
def scrape_site(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        results = []

        bad_words = ["menu", "home", "about", "contact", "login", "register"]

        for a in soup.select("a[href]"):
            title = a.get_text(" ", strip=True)
            href = a.get("href")

            if not title or len(title) < 15:
                continue

            if any(b in title.lower() for b in bad_words):
                continue

            full_link = urljoin(url, href)

            results.append({
                "title": title,
                "link": full_link,
                "source": url
            })

        return results

    except:
        return []


# =========================
# RSS
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
# PDF EXTRACTOR
# =========================
def extract_pdf_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    pdfs = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if ".pdf" in href.lower():
            pdfs.append(urljoin(base_url, href))

    return pdfs


# =========================
# GOV
# =========================
def get_government():
    data = []

    for s in GOV_SITES:
        data += scrape_site(s)

    return data


# =========================
# NEWS
# =========================
def get_news():
    data = []

    for f in RSS_FEEDS + ARABIC_FEEDS:
        data += get_rss(f)

    return data


# =========================
# MASTER
# =========================
def collect_all_sources():
    return get_government() + get_news()
