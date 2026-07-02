import re

from app.core.config import get_settings

settings = get_settings()

SECTION_PATTERN = re.compile(r"(?m)^\s*(\d+(?:\.\d+)*\.?)\s+\S")


def split_into_chunks(text: str) -> list[dict]:
    """Разбивает текст на чанки с сохранением пометки о разделе, если она есть."""
    text = re.sub(r"\r\n", "\n", text).strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[dict] = []
    current = ""
    current_section = ""

    def flush():
        if current.strip():
            chunks.append({"content": current.strip(), "section_label": current_section})

    for para in paragraphs:
        match = SECTION_PATTERN.match(para)
        section_label = match.group(1) if match else current_section

        if len(current) + len(para) + 2 > settings.chunk_size_chars and current:
            flush()
            overlap = current[-settings.chunk_overlap_chars :] if settings.chunk_overlap_chars else ""
            current = overlap
        current = f"{current}\n\n{para}".strip() if current else para
        current_section = section_label

    flush()
    return chunks
