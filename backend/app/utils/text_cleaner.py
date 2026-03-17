import unicodedata

def clean_vietnamese_text(text: str) -> str:
    if not text: return text
    return unicodedata.normalize('NFC', str(text)).strip()