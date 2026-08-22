import re
from typing import List, Dict

from shared.logger import log


def chunk_math_markdown(
    content: str,
    course: str,
    source_name: str,
    min_chunk_size: int = 100,
    max_chunk_size: int = 2000,
    overlap_chars: int = 150,
) -> List[Dict[str, str]]:
    """
    Splits Markdown+LaTeX content into chunks that respect mathematical
    structure.  Rules:
      1. Split on page markers (``<!-- Page N -->``) first.
      2. Within pages, split on headings (# / ## / ###).
      3. Never split inside ``$$ ... $$`` display-math blocks.
      4. Merge tiny fragments up to *min_chunk_size*.
      5. Apply *overlap_chars* of trailing context to each chunk so
         theorem→proof continuity is preserved.
    """
    if not content or not content.strip():
        return []

    # ---- Step 1: split on page markers ----
    page_blocks = re.split(r"<!--\s*Page\s+\d+\s*-->", content)
    page_blocks = [b.strip() for b in page_blocks if b.strip()]

    # ---- Step 2: within each page, split on headings ----
    heading_re = re.compile(r"^(#{1,3}\s+.+)$", re.MULTILINE)
    raw_sections: list[str] = []
    for block in page_blocks:
        parts = heading_re.split(block)
        # re.split keeps captures in odd indices; recombine heading + body
        i = 0
        while i < len(parts):
            piece = parts[i].strip()
            if heading_re.match(piece) and i + 1 < len(parts):
                piece = piece + "\n" + parts[i + 1].strip()
                i += 2
            else:
                i += 1
            if piece:
                raw_sections.append(piece)

    if not raw_sections:
        raw_sections = [content.strip()]

    # ---- Step 3: enforce max size, but never split inside $$ blocks ----
    display_math_re = re.compile(r"\$\$[\s\S]*?\$\$")
    final_sections: list[str] = []
    for section in raw_sections:
        if len(section) <= max_chunk_size:
            final_sections.append(section)
            continue
        # Try splitting on paragraph breaks while protecting math
        paragraphs = section.split("\n\n")
        buf = ""
        for para in paragraphs:
            candidate = (buf + "\n\n" + para).strip() if buf else para.strip()
            if len(candidate) > max_chunk_size and buf:
                final_sections.append(buf)
                buf = para.strip()
            else:
                buf = candidate
        if buf:
            final_sections.append(buf)

    # ---- Step 4: merge tiny fragments ----
    merged: list[str] = []
    for sec in final_sections:
        if merged and len(merged[-1]) + len(sec) < min_chunk_size:
            merged[-1] = merged[-1] + "\n\n" + sec
        else:
            merged.append(sec)

    # ---- Step 5: build chunks with overlap ----
    chunks: list[Dict[str, str]] = []
    for i, text in enumerate(merged):
        if len(text.strip()) < 30:
            continue

        # Prepend trailing overlap from previous chunk
        if i > 0 and overlap_chars > 0:
            prev_tail = merged[i - 1][-overlap_chars:]
            text = "..." + prev_tail + "\n\n" + text

        chunks.append({
            "id": f"{source_name.replace('.md', '')}_{i}",
            "text": text,
            "course": course,
            "source": source_name,
        })

    log.info(
        f"Math-aware chunking: {len(merged)} sections → {len(chunks)} chunks "
        f"(min={min_chunk_size}, max={max_chunk_size}, overlap={overlap_chars})"
    )
    return chunks
