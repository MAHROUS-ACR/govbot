import re


# 🎯 تحديد النوع
def classify(text):
    text = text.lower()

    if "توريد" in text or "توريدات" in text:
        return "توريدات"

    if "مقاولة" in text or "إنشاء" in text or "بناء" in text:
        return "مقاولات"

    return "أخرى"


# 🏢 استخراج جهة (تقريبي)
def extract_company(text):
    words = text.split()
    return " ".join(words[:4])


# 📅 استخراج تاريخ
def extract_date(text):
    match = re.search(r"\d{1,2}/\d{1,2}/\d{4}", text)
    return match.group() if match else ""
