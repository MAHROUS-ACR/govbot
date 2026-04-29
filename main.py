import hashlib
from datetime import datetime

from firebase_config import db
from sources import collect_all_sources
from parser import classify, extract_company, extract_date


# ======================
# KEYWORDS (فلترة إضافية احتياطية)
# ======================
KEYWORDS = [
    "مقاولات",
    "توريدات",
    "إنشاء",
    "بناء",
    "صيانة",
    "معدات",
    "خامات",
    "tender",
    "project",
    "procurement",
    "bid"
]


# ======================
# VALIDATION
# ======================
def is_valid(text):
    if not text:
        return False
    text_lower = text.lower()
    return any(k.lower() in text_lower for k in KEYWORDS)


# ======================
# ID GENERATOR
# ======================
def generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()


# ======================
# COLLECT DATA
# ======================
def collect():
    print("\n🚀 STEP 1: COLLECTING DATA")
    print("=" * 40)

    all_data = collect_all_sources()

    print("\n📥 TOTAL COLLECTED:", len(all_data))
    print("=" * 40)

    return all_data


# ======================
# FILTER DATA
# ======================
def filter_data(data):
    print("\n🧠 STEP 2: FILTERING DATA")
    print("=" * 40)

    filtered = []

    for item in data:
        title = item.get("title", "")

        if is_valid(title):
            filtered.append(item)
            print("✔ KEEP:", title[:80])
        else:
            print("❌ SKIP:", title[:80])

    print("\n✅ FILTERED TOTAL:", len(filtered))
    print("=" * 40)

    return filtered


# ======================
# SAVE TO FIRESTORE
# ======================
def save(data):
    print("\n💾 STEP 3: SAVING TO FIRESTORE")
    print("=" * 40)

    saved = 0

    for item in data:
        title = item.get("title", "")

        doc_id = generate_id(title)
        ref = db.collection("tenders").document(doc_id)

        # منع التكرار
        if ref.get().exists:
            print("🔁 DUPLICATE:", title[:70])
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

        print("✔ SAVED:", title[:80])

    print("\n🎯 TOTAL SAVED:", saved)
    print("=" * 40)

    return saved


# ======================
# MAIN
# ======================
if __name__ == "__main__":

    print("\n================================")
    print("🚀 TENDER BOT STARTED")
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
