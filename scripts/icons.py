"""Task-type icons ("Болдьох бэлиэ") for the Саха тыла textbooks.

Every book explains its margin icons in a legend on page 2. We crop the icons
from that legend as templates, find them on every page by template matching,
and read the exercise number printed just right of each icon.
"""
import re
from pathlib import Path

import cv2
import numpy as np
import pymupdf

# Legend layout: two columns, read top-to-bottom, left column first.
LEGENDS = {
    "lower": [  # grades 1–4
        ["билсиһии", "бодоруһуу", "дьарык", "ыраастык суруйуу"],
        ["оонньуу", "суругунан үлэ", "сыаналаныы", "тыл баайа"],
    ],
    "middle": [  # grades 5–9
        ["өйдөө, болҕой", "саҥаны билии", "кэтээн көрүү", "бодоруһуу"],
        ["хатылааһын", "уустук сорудах", "оонньуу", "кэпсэтии сиэрэ"],
    ],
    "upper": [  # grades 10–11
        ["өйдөө, болҕой", "кэтээн көрүү", "бодоруһуу"],
        ["уустук сорудах", "литэрэтиирэни кытта ситим", "ай-тут"],
    ],
}


def legend_set(book: str) -> str:
    g = re.match(r"Саха_тыла_(\d+)", book).group(1)
    return "lower" if int(g) <= 4 else "middle" if int(g) <= 9 else "upper"


def page_image(doc, pno: int) -> np.ndarray:
    """Render a page at the resolution of its embedded scan (BGR)."""
    page = doc[pno]
    xref = page.get_images()[0]
    scale = xref[2] / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale))
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR if pix.n == 3 else cv2.COLOR_RGBA2BGR)


def ink_mask(img: np.ndarray) -> np.ndarray:
    """Non-background pixels: dark or saturated (icons are colourful)."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return ((gray < 200) | (hsv[..., 1] > 60)).astype(np.uint8)


def find_legend_icons(img: np.ndarray, n_rows: int):
    """Locate legend icons via the "—" dash after each one. Boxes by column."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dark = (gray < 150).astype(np.uint8)
    n, _, st, _ = cv2.connectedComponentsWithStats(dark)
    dashes = [(x, y, bw, bh) for x, y, bw, bh, _ in st[1:]
              if 0.012 * w < bw < 0.05 * w and bh <= max(4, 0.005 * w) and bw > 4 * bh
              and 0.15 * h < y < 0.85 * h]
    # keep dashes that have an icon-sized blob of ink to their left
    mask = ink_mask(img)
    found = []
    for x, y, bw, bh in dashes:
        r = int(0.07 * w)
        x0, y0 = max(0, x - 2 * r), max(0, y - r)
        sub = mask[y0:y + r, x0:x - 2].copy()
        sub = cv2.morphologyEx(sub, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        k, lab, s2, _ = cv2.connectedComponentsWithStats(sub)
        if k < 2:
            continue
        i = 1 + int(np.argmax(s2[1:, 4]))
        ix, iy, iw, ih, area = s2[i]
        if iw > 0.025 * w and ih > 0.025 * w and 0.6 < iw / ih < 1.6:
            found.append((x0 + ix, y0 + iy, iw, ih))
    xs = sorted(b[0] for b in found)
    split = (xs[0] + xs[-1]) / 2
    cols = [sorted([b for b in found if b[0] < split], key=lambda b: b[1]),
            sorted([b for b in found if b[0] >= split], key=lambda b: b[1])]
    return [c[:n_rows] for c in cols]


def legend_templates(pdf: Path):
    """[(label, template_bgr)] cropped from the page-2 legend."""
    doc = pymupdf.open(pdf)
    img = page_image(doc, 1)
    grid = LEGENDS[legend_set(pdf.stem)]
    cols = find_legend_icons(img, max(map(len, grid)))
    out = []
    for labels, boxes in zip(grid, cols):
        for label, (x, y, bw, bh) in zip(labels, boxes):
            out.append((label, img[y:y + bh, x:x + bw].copy()))
    return out
