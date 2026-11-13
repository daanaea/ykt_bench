#!/usr/bin/env python3
"""Find task-type icons on every page and read the exercise number beside each.

Output: data/icons.csv with one row per detected icon:
  book, page, label, score, x, y, side, number
`number` is the exercise number read next to the icon (empty for icons that
mark theory/rule boxes rather than an exercise).

Usage: python3 scripts/detect_icons.py [pdf_dir] [out_csv]
"""
import csv
import sys
from multiprocessing import Pool
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from icons import detect_icons, legend_templates, page_image, read_row_number  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "ykt_textbooks" / "ykt_language"
OUT_CSV = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data" / "icons.csv"

_cache = {}


def work(task):
    pdf, pno = task
    if pdf not in _cache:
        _cache.clear()
        _cache[pdf] = (pymupdf.open(pdf), legend_templates(Path(pdf)))
    doc, templates = _cache[pdf]
    try:
        img = page_image(doc, pno)
    except IndexError:  # page without a scan image
        return []
    rows = []
    for label, score, x, y, side in detect_icons(img, templates):
        n = read_row_number(img, x, y, side)
        rows.append({"book": Path(pdf).stem, "page": pno + 1, "label": label, "score": score,
                     "x": x, "y": y, "side": side, "number": "" if n is None else n})
    return rows


def main():
    tasks = []
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        n = len(pymupdf.open(pdf))
        tasks += [(str(pdf), p) for p in range(2, n)]  # skip cover + legend page
    out = []
    with Pool(10) as pool:
        for k, rows in enumerate(pool.imap(work, tasks, chunksize=8)):
            out += rows
            if k % 250 == 0:
                print(f"{k}/{len(tasks)} pages, {len(out)} icons", flush=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["book", "page", "label", "score", "x", "y", "side", "number"])
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} icons -> {OUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
