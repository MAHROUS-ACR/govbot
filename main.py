import hashlib
from datetime import datetime

from firebase_config import db
from sources import scrape_site, search_google, etenders
from parser import classify, extract_company, extract_date


# ======================
# KEYWORDS
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
# COLLECT
# ======================
def collect():
    print("🚀 STEP 1: Collecting data...")

    all_data = []

    et = etenders()
    print(f"🏛️ Government data: {len(et)}")
    all_data += et

    gg = search_google()
    print(f"🌐 Google data: {len(gg)}")
    all_data += gg

    print(f"📥 TOTAL collected: {len(all_data)}")
    return all_data


# ======================
# FILTER
# ======================
def filter_data(data):
    print("🧠 STEP 2: Filtering data...")

    filtered = []

    for item in data:
        title = item.get("title", "")

        if is_valid(title):
            filtered.append(item)
        else:
            print(f"❌ Skipped: {title[:50]}")

    print(f"✅ Filtered result: {len(filtered)}")
    return filtered


# ======================
# SAVE
# ======================
def save(data):
    print("💾 STEP 3: Saving to Firestore...")

    saved = 0

    for item in data:
        title = item.get("title", "")

        doc_id = generate_id(title)
        ref = db.collection("tenders").document(doc_id)

        if ref.get().exists:
            print(f"🔁 Duplicate skipped: {title[:40]}")
            continue

        record = {
            "title": title,
            "company": extract_company(title),
            "type": classify(title),
            "deadline": extract_date(title),
            "link": item.get("link"),
            "source": item.get("source"),
            "created_at": datetime.utcnow()
        }

        ref.set(record)
        saved += 1

        print(f"✔ Saved: {title[:60]}")

    print(f"🎯 TOTAL saved: {saved}")
    return saved


# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print("===================================")
    print("🚀 TENDER BOT STARTED")
    print("===================================")

    raw = collect()
    filtered = filter_data(raw)
    saved = save(filtered)

    print("===================================")
    print("🏁 FINISHED RUN")
    print(f"📥 Raw: {len(raw)}")
    print(f"🧠 Filtered: {len(filtered)}")
    print(f"💾 Saved: {saved}")
    print("===================================")
