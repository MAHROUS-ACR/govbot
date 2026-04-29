import hashlib
from datetime import datetime

from firebase_config import db
from sources import collect_all_sources
from parser import classify, extract_company, extract_date


# ======================
# 🔥 KEYWORDS (TENDERS ONLY)
# ======================
KEYWORDS = [
    "tender",
    "tenders",
    "bid",
    "bidding",
    "procurement",
    "مناقصة",
    "توريد",
    "مقاولات",
    "إنشاء",
    "صيانة",
    "مشروع"
]


# ======================
# ❌ FILTER OUT MENUS / HEADERS
# ======================
def is_not_menu(text):
    bad = [
        "home", "about", "contact", "login",
        "register", "privacy", "terms",
        "menu", "breadcrumb"
    ]
    return not any(b in text.lower() for b in bad)


# ======================
# ✅ REAL TENDER DETECTOR (IMPORTANT FIX)
# ======================
def is_real_tender(item):
    text = (item.get("title", "") + " " + item.get("source", "")).lower()

    return (
        any(k in text for k in KEYWORDS) and
        is_not_menu(text) and
        len(item.get("title", "")) > 20
    )


# ======================
# ID
# ======================
def generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()


# ======================
# COLLECT
# ======================
def collect():
    print("\n🚀 STEP 1: COLLECT ALL SOURCES")

    data = collect_all_sources()

    print("📥 RAW:", len(data))
    return data


# ======================
# FILTER (IMPORTANT FIX)
# ======================
def filter_data(data):
    print("\n🧠 STEP 2: FILTER REAL TENDERS ONLY")

    filtered = []

    for item in data:
        title = item.get("title", "")

        if is_real_tender(item):
            filtered.append(item)
            print("✔ TENDER:", title[:90])
        else:
            print("❌ SKIP:", title[:90])

    print("\n✅ FINAL:", len(filtered))
    return filtered


# ======================
# SAVE (FULL DETAILS)
# ======================
def save(data):
    print("\n💾 STEP 3: SAVE TO FIRESTORE")

    saved = 0

    for item in data:
        title = item.get("title", "")
        link = item.get("link", "")

        doc_id = generate_id(title + link)
        ref = db.collection("tenders").document(doc_id)

        if ref.get().exists:
            continue

        record = {
            "title": title,
            "link": link,
            "source": item.get("source"),

            # 🧠 AI parsing (لو عندك parser قوي)
            "company": extract_company(title),
            "type": classify(title),

            # 📅 dates
            "published_date": extract_date(title),
            "deadline": None,

            "country": "Unknown",

            "created_at": datetime.utcnow()
        }

        ref.set(record)
        saved += 1

        print("✔ SAVED:", title[:90])

    print("\n🎯 SAVED:", saved)
    return saved


# ======================
# MAIN
# ======================
if __name__ == "__main__":

    print("\n================================")
    print("🚀 PRO TENDER BOT")
    print("================================")

    raw = collect()
    filtered = filter_data(raw)
    saved = save(filtered)

    print("\n================================")
    print("🏁 DONE")
    print("RAW:", len(raw))
    print("FILTERED:", len(filtered))
    print("SAVED:", saved)
    print("================================")
