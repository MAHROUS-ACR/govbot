import re

def extract_company(text):
    return text.split()[0] if text else None


def extract_date(text):
    patterns = [
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}/\d{2}/\d{4}"
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group()

    return None


def classify(text):
    t = text.lower()

    if "tender" in t or "مناقصة" in t:
        return "tender"

    if "contract" in t:
        return "contract"

    return "unknown"
