def clean_ocr_text(text: str) -> str:
    """Return ``text`` stripped and condensed to single spaces."""
    return text.strip().replace("\n", " ").replace("  ", " ")
