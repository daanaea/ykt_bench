#!/usr/bin/env python3
"""Extract text from the Sakha textbook PDFs into one .txt per book.

The PDFs already carry a Sakha-aware text layer (with ҕ ҥ ө һ ү), which is far
more accurate than any local OCR engine for Sakha. This script pulls that layer
out page by page, cleans a few systematic artifacts, and fills pages that have
no text layer from hand-checked vision transcriptions in ocr/manual/.

Usage:
    python3 scripts/extract_text.py [pdf_dir] [out_dir]

Output: <out_dir>/<book>.txt with "===== page N =====" markers (N = 1-based PDF
page index), plus <out_dir>/manifest.json with per-book stats.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

from sakha_text import CorpusStats, repair

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "ykt_textbooks" / "ykt_language"
OUT_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "ocr" / PDF_DIR.name
MANUAL_DIR = ROOT / "ocr" / "manual"
EMPTY_PAGE_CHARS = 20  # below this, a page counts as having no text layer

CYR = "а-яёА-ЯЁҕҥөһүҔҤӨҺҮ"
CYR_RE = re.compile(f"[{CYR}]")
LAT_RE = re.compile(r"[a-zA-Z]")

# Latin letters that typesetters/extractors substitute for Cyrillic look-alikes.
LAT2CYR = str.maketrans({
    "a": "а", "c": "с", "e": "е", "o": "о", "p": "р", "x": "х", "y": "у",
    "h": "һ", "k": "к", "u": "и", "n": "п", "m": "т",
    "A": "А", "B": "В", "C": "С", "E": "Е", "H": "Н", "K": "К", "M": "М",
    "O": "О", "P": "Р", "T": "Т", "X": "Х", "Y": "У",
})
CYR2LAT = str.maketrans({
    "а": "a", "с": "c", "е": "e", "о": "o", "р": "p", "х": "x", "у": "y",
    "А": "A", "В": "B", "С": "C", "Е": "E", "Н": "H", "К": "K", "М": "M",
    "О": "O", "Р": "P", "Т": "T", "Х": "X",
})

# Bullet glyphs come out of the text layer as "y"/"yy" glued to the next word.
BULLET_LINE_START = re.compile(rf"(?m)^y{{1,2}} ?(?=[{CYR}0-9«(])")
BULLET_INLINE = re.compile(rf"(?<=\s)yy ?(?=[{CYR}])")


def _is_latin(ch: str) -> bool:
    return ch.isalpha() and unicodedata.name(ch, "").startswith("LATIN")


def fix_mixed_word(m: re.Match) -> str:
    """Unify a word that mixes Cyrillic and Latin look-alike letters."""
    w = m.group(0)
    cyr = [c for c in w if CYR_RE.match(c)]
    lat = [c for c in w if _is_latin(c)]
    if not cyr or not lat:
        return w
    # "Strong" letters have no look-alike in the other script and decide it.
    strong_cyr = any(ord(c) not in CYR2LAT for c in cyr)
    strong_lat = any(ord(c) not in LAT2CYR for c in lat)
    if strong_cyr and not strong_lat:
        return w.translate(LAT2CYR)
    if strong_lat and not strong_cyr:
        return w.translate(CYR2LAT)
    if strong_cyr and strong_lat:
        return w  # genuinely mixed (e.g. linguistic transcription) — leave it
    return w.translate(LAT2CYR) if len(cyr) >= len(lat) else w.translate(CYR2LAT)


def clean(text: str) -> str:
    text = text.replace("­", "")  # soft hyphens
    text = BULLET_LINE_START.sub("• ", text)
    text = BULLET_INLINE.sub("• ", text)
    text = re.sub(r"\w+", fix_mixed_word, text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest, books = {}, {}
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        book = pdf.stem
        doc = pymupdf.open(pdf)
        pages, empty, manual_used = [], [], []
        for i, page in enumerate(doc, start=1):
            text = page.get_text()
            source = "text_layer"
            if len(text.strip()) < EMPTY_PAGE_CHARS:
                mfile = MANUAL_DIR / book / f"p{i:03d}.txt"
                if mfile.exists():
                    text, source = mfile.read_text(encoding="utf-8"), "vision"
                    manual_used.append(i)
                else:
                    empty.append(i)
            pages.append((i, source, clean(text)))
        books[book] = pages
        manifest[book] = {
            "pdf": str(pdf.relative_to(ROOT)),
            "pages": len(doc),
            "vision_pages": manual_used,
            "empty_pages": empty,
        }
        print(f"{book:28s} pages={len(doc):4d} vision={len(manual_used):3d} empty={empty}")

    # Second pass: word-level repairs that need statistics from all books.
    stats = CorpusStats(body for pages in books.values() for _, _, body in pages)
    for book, pages in books.items():
        parts = []
        for i, source, body in pages:
            tag = "" if source == "text_layer" else f" [{source}]"
            parts.append(f"===== page {i}{tag} =====\n{repair(body, stats)}\n")
        (OUT_DIR / f"{book}.txt").write_text("\n".join(parts), encoding="utf-8")
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
