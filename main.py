import hashlib
from datetime import datetime

from firebase_config import db
from sources import scrape_site, get_rss, search_google, etenders
from parser import classify, extract_company, extract_date


# ======================
# KEYWORDS FILTER
# ======================
KEYWORDS = [
    "مقاولات",
    "توريدات",
    "إنشاء",
    "بناء",
    "صيانة",
    "معدات",
    "خامات"
]


def is_valid(text):
    return any(k in text for k in KEYWORDS)


def generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()


# ======================
# COLLECT DATA
# ======================
def collect():
    all_data = []

    # حكومي
    all_data += etenders()

    # Google
    all_data += search_google()

    # مواقع إضافية (تقدر تزود)
    sites = [
        "https://example.com",
        "https://another-site.com"
    ]

    for site in sites:
        all_data += scrape_site(site)

    # RSS (اختياري)
    rss_links = [
        # "https://site.com/rss"
    ]

    for rss in rss_links:
        all_data += get_rss(rss)

    return all_data


# ======================
# FILTER
# ======================
def filter_data(data):
    return [d for d in data if is_valid(d.get("title", ""))]


# ======================
# SAVE TO FIRESTORE
# ======================
def save(data):
    new_items = 0

    for item in data:
        title = item.get("title", "")

        if not title:
            continue

        doc_id = generate_id(title)
        ref = db.collection("tenders").document(doc_id)

        if ref.get().exists:
            continue

        ref.set({
            "title": title,
            "company": extract_company(title),
            "type": classify(title),
            "deadline": extract_date(title),
            "link": item.get("link"),
            "source": item.get("source"),
            "created_at": datetime.utcnow()
        })

        new_items += 1

    return new_items


# ======================
# RUN BOT
# ======================
if __name__ == "__main__":
    print("🚀 BOT STARTED")

    raw = collect()
    print("📥 Collected:", len(raw))

    filtered = filter_data(raw)
    print("🧠 Filtered:", len(filtered))

    saved = save(filtered)
    print("💾 New saved:", saved)

    print("✅ DONE")
