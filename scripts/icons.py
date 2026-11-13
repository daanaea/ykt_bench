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

    def dash_columns(min_w, ratio):
        dashes = [(x, y + bh / 2) for x, y, bw, bh, _ in st[1:]
                  if min_w * w < bw < 0.05 * w and bh <= max(4, 0.005 * w) and bw > ratio * bh]
        # legend dashes line up in two columns of equal x; stray dashes don't
        clusters = []
        for d in sorted(dashes):
            if clusters and d[0] - clusters[-1][-1][0] < 0.01 * w:
                clusters[-1].append(d)
            else:
                clusters.append([d])
        clusters = sorted((c for c in clusters if len(c) >= 3), key=len, reverse=True)[:2]
        return sorted(clusters, key=lambda c: c[0][0])

    # "—" em-dashes in most books; grade 6 uses a shorter "–"
    clusters = dash_columns(0.012, 4)
    if len(clusters) < 2:
        clusters = dash_columns(0.007, 3)

    mask = cv2.morphologyEx(ink_mask(img), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cols = []
    for col in clusters:
        col.sort(key=lambda d: d[1])
        gap = np.median(np.diff([d[1] for d in col])) if len(col) > 1 else 0.08 * w
        boxes = []
        for x, yc in col:
            y0, y1 = int(max(0, yc - 0.5 * gap)), int(yc + 0.5 * gap)
            x0 = int(max(0, x - 1.6 * gap))
            k, _, s2, _ = cv2.connectedComponentsWithStats(mask[y0:y1, x0:int(x) - 2])
            parts = [s for s in s2[1:] if s[4] > 0.02 * gap * gap]
            if not parts:
                continue
            # the icon is the blob nearest the dash; take everything that
            # overlaps it horizontally (an icon can split into pieces)
            near = max(parts, key=lambda s: s[0] + s[2])
            group = [s for s in parts if s[0] + s[2] > near[0] - 0.1 * gap]
            bx0 = min(s[0] for s in group); by0 = min(s[1] for s in group)
            bx1 = max(s[0] + s[2] for s in group); by1 = max(s[1] + s[3] for s in group)
            boxes.append((x0 + bx0, y0 + by0, bx1 - bx0, by1 - by0))
        cols.append(boxes[:n_rows])
    # icons share one size: square every crop to the median side
    side = int(np.median([max(b[2], b[3]) for c in cols for b in c]))
    out = []
    for c in cols:
        out.append([(int(x + bw / 2 - side / 2), int(y + bh / 2 - side / 2), side, side)
                    for x, y, bw, bh in c])
    return out


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


def _tesseract(gray: np.ndarray, psm: str, digits: bool = False) -> str:
    import subprocess
    ok, png = cv2.imencode(".png", gray)
    cmd = ["tesseract", "stdin", "stdout", "--psm", psm, "-l", "eng"]
    if digits:
        cmd += ["-c", "tessedit_char_whitelist=0123456789."]
    return subprocess.run(cmd, input=png.tobytes(), capture_output=True
                          ).stdout.decode("utf-8", "replace")


def _read_badge(region: np.ndarray, side: int):
    """Number printed inside an oval badge right of the icon (grades 5–11)."""
    if region.size == 0:
        return None
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    ink = ((gray < 170) | (hsv[..., 1] > 70)).astype(np.uint8)
    cnts, _ = cv2.findContours(ink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in sorted(cnts, key=lambda c: cv2.boundingRect(c)[0]):
        bx, by, bw, bh = cv2.boundingRect(c)
        if 0.6 * side < bw < 2.2 * side and 0.3 * side < bh < 1.1 * side and bw > bh:
            px, py = int(0.16 * bw), int(0.2 * bh)
            inner = gray[by + py:by + bh - py, bx + px:bx + bw - px]
            if inner.size == 0:
                continue
            inner = cv2.resize(inner, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            _, inner = cv2.threshold(inner, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            inner = cv2.copyMakeBorder(inner, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
            m = re.search(r"(\d{1,3})", _tesseract(inner, "7", digits=True))
            return int(m.group(1)) if m else None
    return None


def read_row_number(img: np.ndarray, x: int, y: int, side: int):
    """OCR the exercise number on the icon's row ("89.", "13.").

    Icons sit left of the header (number to their right) or, for a few, in
    the right margin (number at the start of the row). Returns int or None.
    """
    import subprocess
    h, w = img.shape[:2]
    y0, y1 = max(0, int(y - 0.3 * side)), min(h, int(y + 1.3 * side))
    if x < w / 2:
        x0, x1 = x + side, min(w, x + side + int(0.3 * w))
    else:
        x0, x1 = int(0.04 * w), x
    band = img[y0:y1, x0:x1]
    if band.size == 0:
        return None
    if x < w / 2:
        n = _read_badge(img[y0:y1, x + side:min(w, x + int(3.2 * side))], side)
        if n is not None:
            return n
    # variant 1: as printed (grades 1–4 print coloured numbers)
    # variant 2: black print only (coloured badge outlines break the layout)
    hsv = cv2.cvtColor(band, cv2.COLOR_BGR2HSV)
    black = np.where((hsv[..., 2] < 110) & (hsv[..., 1] < 90), 0, 255).astype(np.uint8)
    for variant in (band, black):
        big = cv2.resize(variant, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        ok, png = cv2.imencode(".png", big)
        out = subprocess.run(["tesseract", "stdin", "stdout", "--psm", "11", "-l", "eng", "tsv"],
                             input=png.tobytes(), capture_output=True
                             ).stdout.decode("utf-8", "replace")
        best = None
        for row in out.splitlines()[1:]:
            f = row.split("\t")
            if len(f) < 12:
                continue
            m = re.fullmatch(r"[(\[{]?(\d{1,3})[.,][)\]}]?", f[11].strip())
            if m:
                left = int(f[6])
                if best is None or left < best[0]:
                    best = (left, int(m.group(1)))
        if best:
            return best[1]
    return None


DETECT_SCALE = 0.5      # match on half-resolution images for speed
SCALES = (0.8, 0.9, 1.0, 1.12, 1.25)
THRESHOLD = 0.72


def detect_icons(img: np.ndarray, templates):
    """[(label, score, x, y, side)] for icons on a page, in full-res pixels."""
    small = cv2.resize(img, None, fx=DETECT_SCALE, fy=DETECT_SCALE, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    hits = []
    for label, tm in templates:
        for s in SCALES:
            t = cv2.resize(tm, None, fx=DETECT_SCALE * s, fy=DETECT_SCALE * s,
                           interpolation=cv2.INTER_AREA)
            tg = cv2.cvtColor(t, cv2.COLOR_BGR2GRAY)
            if tg.shape[0] >= gray.shape[0] or tg.shape[1] >= gray.shape[1]:
                continue
            res = cv2.matchTemplate(gray, tg, cv2.TM_CCOEFF_NORMED)
            ys, xs = np.where(res >= THRESHOLD)
            for y, x in zip(ys, xs):
                hits.append((float(res[y, x]), label, x, y, tg.shape[1]))
    # non-maximum suppression across labels and scales
    hits.sort(reverse=True)
    kept = []
    for score, label, x, y, side in hits:
        if all(abs(x - kx) > 0.6 * ks or abs(y - ky) > 0.6 * ks for _, _, kx, ky, ks in kept):
            kept.append((score, label, x, y, side))
    k = 1 / DETECT_SCALE
    return [(label, round(score, 3), int(x * k), int(y * k), int(side * k))
            for score, label, x, y, side in kept]
