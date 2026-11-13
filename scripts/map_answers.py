#!/usr/bin/env python3
"""Attach answers from the textbooks' answer keys to the assignments they solve.

Answer keys:
  grades 1–4   "Оонньуулар таайыылара"      keyed by page:  "56 с. — 1. Аҕа. 2. Ала."
  grades 5–7   "Таайбараҥнар/Таабырыннар эппиэттэрэ"  keyed by page: "с. 7: …"
  grade 9      "1 барыйаан хоруйа"          exam answers by task number (table;
                                            transcribed in ocr/manual/answers/)
  grades 10–11 "Тургутуктар хоруйдара"      keyed by test name + question number
Page-keyed answers belong to the game/riddle exercise on that page: we prefer
exercises marked with the "оонньуу" icon or whose instruction asks to solve a
riddle/puzzle, and pair several answers for one page with its games in order.

Input:  ocr/ykt_language/*.txt, data/ykt_language_assignments.csv
Output: data/ykt_language_assignments_mapped.csv
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_assignments import END_RE, PAGE_RE  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OCR_DIR = ROOT / "ocr" / "ykt_language"
MANUAL = ROOT / "ocr" / "manual" / "answers"
IN_CSV = ROOT / "data" / "ykt_language_assignments.csv"
OUT_CSV = ROOT / "data" / "ykt_language_assignments_mapped.csv"

GAME = re.compile(r"(?i)таай|таабырын|ребус|кроссворд|шарада|таайбараҥ|оонньуу|аптаах|"
                  r"ыһыллыбыт|көтүтүллүбүт буукуба|дьикти|ойуулары сөпкө|буукубалары|\bүһү\b")
PAGE_KEY = re.compile(r"(?:(\d{1,3})(?:\s*[—–-]\s*(\d{1,3}))?\s*сс?\.|с\.?\s*(\d{1,3})\s*:)\s*[—–-]?\s*")
TEST_STEM = {"лиэксикэ": "Лиэксикэ", "саҥа дорҕоон": "Саҥа дорҕоон", "морполуогуйа": "Морполуогуйа",
             "сиинтэксис": "Сиинтэксис", "истилиистикэ": "Истилиистикэ",
             "тыл култуурата": "Тыл култуура"}


def answer_section(book: str):
    """(heading, first page, text) of the book's answer key, or None."""
    manual = sorted(MANUAL.glob(f"{book}_p*.txt"))
    if manual:
        page = int(re.search(r"_p(\d+)", manual[0].stem).group(1))
        lines = manual[0].read_text(encoding="utf-8").strip().splitlines()
        return lines[0], page, "\n".join(lines[1:])
    text = (OCR_DIR / f"{book}.txt").read_text(encoding="utf-8")
    page, out, heading, start = 0, [], None, None
    for ln in text.splitlines():
        m = PAGE_RE.match(ln)
        if m:
            page = int(m.group(1))
            continue
        s = ln.strip()
        if heading is None:
            if END_RE.match(s) and not re.match(r"(?i)иһинээ", s):
                heading, start = s, page
            continue
        if re.match(r"(?i)^иһинээ.итэ$", s):
            break
        if re.fullmatch(r"\d{1,3}", s):  # printed page number
            continue
        out.append(s)
    return (heading, start, "\n".join(out)) if heading else None


def page_entries(text: str):
    """[(pages, answer)] from a page-keyed answer key."""
    flat = " ".join(text.split())
    marks = list(PAGE_KEY.finditer(flat))
    entries = []
    for m, nxt in zip(marks, marks[1:] + [None]):
        a = int(m.group(1) or m.group(3))
        b = int(m.group(2)) if m.group(2) else a
        ans = flat[m.end():nxt.start() if nxt else len(flat)].strip(" —–-")
        if ans:
            entries.append((list(range(a, b + 1)), ans))
    return entries


def test_entries(text: str):
    """[(test stem, question no, answer)] from 'Тургутуктар хоруйдара'."""
    out, stem = [], None
    buf = defaultdict(list)
    for ln in text.splitlines():
        low = ln.lower()
        hit = next((v for k, v in TEST_STEM.items() if low.startswith(k)), None)
        if hit and "тургут" in low:
            stem = hit
            continue
        if stem:
            buf[stem].append(ln)
    for stem, lines in buf.items():
        flat = " ".join(" ".join(lines).split())
        for part in re.split(r";\s*", flat.rstrip(".")):
            m = re.match(r"(\d{1,2})\.\s*(.+)", part.strip())
            if m:
                out.append((stem, int(m.group(1)), m.group(2).strip()))
    return out


def main():
    with IN_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_book = defaultdict(list)
    for r in rows:
        by_book[r["book"]].append(r)

    mapped, report = [], []
    for book, ex in by_book.items():
        sec = answer_section(book)
        if not sec:
            continue
        heading, key_page, text = sec
        n_before = len(mapped)

        if "тургутук" in heading.lower():
            side = [r for r in ex if r["chain"] == "side"]
            for stem, q, ans in test_entries(text):
                hit = [r for r in side if r["section"].lower().startswith(stem.lower())
                       and int(r["number"]) == q]
                if hit:
                    mapped.append({**hit[0], "answer": ans, "answer_key": f"{heading}: {stem}, {q}",
                                   "answer_key_page": key_page, "mapping": "test+number"})
                else:
                    report.append(f"{book}: no question for {stem} {q}")

        elif "барыйаан" in heading.lower():
            tsv = MANUAL / f"{book}_p{key_page}.tsv"
            exam = [r for r in ex if r["chain"] == "side" and "эксээмэн" in r["section"].lower()
                    and int(r["pdf_page_start"]) < key_page]
            with tsv.open(encoding="utf-8") as f:
                for a in csv.DictReader(f, delimiter="\t"):
                    hit = [r for r in exam if r["lesson"] == exam[0]["lesson"]
                           and int(r["number"]) == int(a["task"])]
                    if hit:
                        mapped.append({**hit[0], "answer": a["answer"],
                                       "answer_key": f"{heading}, {a['task']}",
                                       "answer_key_page": key_page, "mapping": "exam+number"})

        else:
            per_page = defaultdict(list)
            for pages, ans in page_entries(text):
                per_page[tuple(pages)].append(ans)
            used = set()
            for pages, answers in per_page.items():
                cands = [r for r in ex
                         if int(r["pdf_page_start"]) <= pages[-1] and int(r["pdf_page_end"]) >= pages[0]]

                def score(r):
                    s = 3 * ("оонньуу" in r["icon"]) + 2 * bool(GAME.search(r["instruction"]))
                    s += int(r["pdf_page_start"]) in pages
                    return s - 5 * (r["id"] in used)  # one answer per exercise if possible
                ranked = sorted(cands, key=score, reverse=True)
                good = [r for r in ranked if score(r) >= 2]
                pick = (good or ranked)[:len(answers)]
                used.update(r["id"] for r in pick)
                pick.sort(key=lambda r: (int(r["pdf_page_start"]), rows.index(r)))
                label = (f"{pages[0]}—{pages[-1]} сс." if len(pages) > 1 else f"{pages[0]} с.")
                for r, ans in zip(pick, answers):
                    conf = ("icon" if "оонньуу" in r["icon"] else
                            "instruction" if GAME.search(r["instruction"]) else "page_only")
                    if len(cands) == 1 and conf == "page_only":
                        conf = "only_exercise_on_page"
                    mapped.append({**r, "answer": ans, "answer_key": f"{heading}, {label}",
                                   "answer_key_page": key_page, "mapping": conf})
                if len(pick) < len(answers):
                    report.append(f"{book}: {label} has {len(answers)} answers, "
                                  f"{len(pick)} exercises found")
        print(f"{book:28s} key '{heading}' p{key_page}: mapped {len(mapped) - n_before}")

    cols = list(rows[0]) + ["answer", "answer_key", "answer_key_page", "mapping"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(mapped)
    print(f"wrote {len(mapped)} rows -> {OUT_CSV.relative_to(ROOT)}")
    for line in report:
        print("  !", line)


if __name__ == "__main__":
    main()
