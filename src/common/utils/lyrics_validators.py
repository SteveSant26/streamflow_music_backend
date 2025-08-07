import re


def validate_lyrics(lyrics: str) -> bool:
    """Valida que el contenido parezca ser letras reales"""
    if not lyrics or len(lyrics.strip()) < 50:
        return False
    words = lyrics.split()
    if len(words) < 10:
        return False
    special_char_ratio = len(re.findall(r'[^\w\s\n\r\'".,!?()-]', lyrics)) / max(
        len(lyrics), 1
    )
    if special_char_ratio > 0.3:
        return False
    return True
