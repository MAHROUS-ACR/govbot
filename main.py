import hashlib
from datetime import datetime

from firebase_config import db
from sources import collect_all_sources
from parser import classify, extract_company, extract_date


# ======================
# 🇪🇬 EGYPT FILTER
# ======================
EGYPT_KEYS = ["مصر", "egypt", "القاهرة", "giza"]


def is_egypt(item):
    text = (item.get("title","") + item.get("source","")).lower()
    return any(k in text for k in EGYPT_KEYS)


# ======================
# REAL TENDER CHECK
# ======================
def is_tender(text):
    t = text.lower()
    return (
        "tender" in t or
        "مناقصة" in t or
        "bid" in t or
        "procurement" in t
    )


# ======================
# ID
# ======================
def gen_id(text):
    return hashlib.md5(text.encode()).hexdigest()


# ======================
# COLLECT
# ======================
def collect():
    print("🚀 COLLECTING ALL SOURCES...")
    data = collect_all_sources()
    print("RAW:", len(data))
    return data


# ======================
# FILTER
# ======================
def filter_data(data):
    print("\n🧠 FILTERING (EGYPT ONLY)")

    out = []

    for item in data:
        if is_egypt(item) and is_tender(item.get("title","")):
            out.append(item)
            print("✔ KEEP:", item["title"][:90])
        else:
            print("❌ SKIP:", item["title"][:90])

    return out


# ======================
# SAVE TO FIRESTORE
# ======================
def save(data):
    print("\n💾 SAVING...")

    saved = 0

    for item in data:
        title = item["title"]
        link = item.get("link","")
        source = item.get("source","")

        doc_id = gen_id(title + link)
        ref = db.collection("tenders").document(doc_id)

        if ref.get().exists:
            continue

        # ⭐ scoring system
        score = 0
        if "مناقصة" in title:
            score += 3
        if "tender" in title.lower():
            score += 2
        if "gov" in source:
            score += 2
        if extract_date(title):
            score += 2

        record = {
            "title": title,
            "link": link,
            "pdf_link": None,   # 👈 جاهز للـ upgrade لاحقاً
            "source": source,

            "company": extract_company(title),
            "type": classify(title),
            "published_date": extract_date(title),
            "deadline": None,

            "country": "Egypt",
            "score": score,

            "created_at": datetime.utcnow()
        }

        ref.set(record)
        saved += 1

        print(f"✔ SAVED (score {score}):", title[:90])

    print("\nDONE SAVED:", saved)
    return saved


# ======================
# MAIN
# ======================
if __name__ == "__main__":

    print("\n====================")
    print("🚀 PRO TENDER SYSTEM")
    print("====================")

    raw = collect()
    filtered = filter_data(raw)
    saved = save(filtered)

    print("\n====================")
    print("FINISHED")
    print("RAW:", len(raw))
    print("FILTERED:", len(filtered))
    print("SAVED:", saved)
    print("====================")
