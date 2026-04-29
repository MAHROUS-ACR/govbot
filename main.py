import hashlib
import re
from datetime import datetime, timedelta

from firebase_config import db
from sources import collect_all_sources
from parser import classify, extract_company


# ======================
# 🇪🇬 FILTER EGYPT ONLY
# ======================
EGYPT_KEYWORDS = [
    "مصر",
    "egypt",
    "القاهرة",
    "alexandria",
    "etenders",
    "وزارة",
    "هيئة",
    "حكومي"
]


def is_egypt_related(text, source=""):
    text = (text or "").lower()
    source = (source or "").lower()

    return any(k in text for k in EGYPT_KEYWORDS) or "eg" in source or "egypt" in source


# ======================
# BUSINESS KEYWORDS
# ======================
KEYWORDS = [
    "مقاولات",
    "توريدات",
    "إنشاء",
    "بناء",
    "صيانة",
    "معدات",
    "خامات",
    "مناقصة",
    "tender"
]


def is_valid(text):
    text = (text or "").lower()
    return any(k.lower() in text for k in KEYWORDS)


# ======================
# ID GENERATOR
# ======================
def generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()


# ======================
# DATE EXTRACTION
# ======================
def extract_dates(text):
    text = (text or "").lower()

    # محاولة استخراج مدة مثل "10 days"
    days_match = re.search(r"(\d+)\s*(يوم|days|day)", text)

    if days_match:
        days = int(days_match.group(1))
        deadline = datetime.utcnow() + timedelta(days=days)
    else:
        deadline = None

    return {
        "published_at": datetime.utcnow(),
        "deadline": deadline.isoformat() if deadline else None
    }


# ======================
# COLLECT DATA
# ======================
def collect():
    print("\n🚀 STEP 1: COLLECTING DATA")
    print("=" * 50)

    data = collect_all_sources()

    print(f"\n📥 TOTAL COLLECTED: {len(data)}")
    print("=" * 50)

    return data


# ======================
# FILTER DATA
# ======================
def filter_data(data):
    print("\n🧠 STEP 2: FILTERING DATA (EGYPT ONLY)")
    print("=" * 50)

    filtered = []

    for item in data:
        title = item.get("title", "")
        source = item.get("source", "")

        if is_egypt_related(title, source) and is_valid(title):
            filtered.append(item)
            print("✔ KEEP:", title[:90])
        else:
            print("❌ SKIP:", title[:90])

    print(f"\n✅ FILTERED TOTAL: {len(filtered)}")
    print("=" * 50)

    return filtered


# ======================
# SAVE TO FIRESTORE
# ======================
def save(data):
    print("\n💾 STEP 3: SAVING TO FIRESTORE")
    print("=" * 50)

    saved = 0

    for item in data:
        title = item.get("title", "")
        link = item.get("link", "")
        source = item.get("source", "")

        doc_id = generate_id(title + str(link))
        ref = db.collection("tenders").document(doc_id)

        if ref.get().exists:
            print("🔁 DUPLICATE:", title[:70])
            continue

        dates = extract_dates(title)

        record = {
            "title": title,
            "link": link,
            "source": source,

            # 📅 dates
            "published_at": dates["published_at"],
            "deadline": dates["deadline"],

            # 🧠 extracted info
            "company": extract_company(title),
            "type": classify(title),

            # 🇪🇬 metadata
            "country": "Egypt",
            "is_egypt": True,

            "created_at": datetime.utcnow()
        }

        ref.set(record)
        saved += 1

        print("✔ SAVED:", title[:90])
        print("📅 DEADLINE:", record["deadline"])

    print("\n🎯 TOTAL SAVED:", saved)
    print("=" * 50)

    return saved


# ======================
# MAIN
# ======================
if __name__ == "__main__":

    print("\n================================")
    print("🚀 TENDER BOT STARTED (EGYPT MODE)")
    print("================================")

    raw = collect()
    filtered = filter_data(raw)
    saved = save(filtered)

    print("\n================================")
    print("🏁 FINISHED RUN")
    print("📥 RAW:", len(raw))
    print("🧠 FILTERED:", len(filtered))
    print("💾 SAVED:", saved)
    print("================================\n")
