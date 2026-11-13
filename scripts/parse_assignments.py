#!/usr/bin/env python3
"""Parse numbered exercises (assignments) out of the extracted textbook text.

Input:  ocr/ykt_language/*.txt   (from extract_text.py)
Output: data/ykt_language_assignments.csv

The text layer carries no fonts or layout, so exercise headers ("61. Күрэхтэһиҥ…")
look exactly like numbered sub-items inside an exercise ("1. Будулҕан тумаҥҥа…").
We pick the headers with a small dynamic program over every numbered line:
  * exercise numbers form a chain n, n+1, n+2… (grades 5–11 number the whole
    book; grades 1–4 restart at 1 every lesson),
  * sub-item lists restart at 1 inside an exercise,
  * headers read like instructions (imperative verbs, questions).
The highest-scoring reading of the numbered lines wins.

Usage: python3 scripts/parse_assignments.py [ocr_dir] [out_csv]
"""
import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sakha_text import CorpusStats, dehyphenate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OCR_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "ocr" / "ykt_language"
OUT_CSV = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data" / "ykt_language_assignments.csv"

UP = "А-ЯЁҔҤӨҺҮ"
LO = "а-яёҕҥөһү"
PAGE_RE = re.compile(r"^===== page (\d+)(?: \[(\w+)\])? =====$")
NUM_RE = re.compile(rf"^(\d{{1,3}})(?:\.(?:\s+(.*))?|\s+([«\"]?[{'А-ЯЁҔҤӨҺҮ'}].*))$")
SECTION_RE = re.compile(r"^\d{1,3}\s?§\.?\s*\S")
INLINE_NUM = re.compile(rf"(?<=[.?!»)])\s+(?=\d{{1,3}}\.\s+[«\"(\[]?[{UP}])")

# Recurring headings: they end an exercise's content and set its "block".
HEADINGS = {
    "Ситимнээх саҥа": "coherent_speech",
    "БИЛИИБИТИН БЭРЭБИЭРКЭЛЭНЭБИТ": "test",
    "Хатылааһын": "review",
    "СҮБЭ": None,                               # advice box, not a block
    "Үөрэнэр соругум": "",                      # unit start (grades 1–4)
    "Үөрэнэр сорукпун хайдах толордум": "",     # self-assessment after a test
}

# 2nd-person-singular imperatives common in grades 1–4 instructions.
IMP_2SG = set("""
аах бул суруй ырыт тупсар хоруйдаа уһул оҥор туруор таай быһаар ый көр бэлиэтээ
толкуйдаа уларыт таһаар араар ситэр тарт эт кэпсээ наардаа үөрэт холбоо ааттаа
тэҥнээ сааһылаа ситимнээ толор уус ус кэпсэт ыллаа истэ иһит булан түмүктээ
сыаналаа санаа бэлэмнээ дакаастаа ааҕан хатылаа сурунаал уруһуйдаа тылбаастаа
сөпсөһүннэр сыһыар ааттаталаа ыйыталас солбуй эбэн кылгат сиһилээ
""".split())
IMP_2PL = re.compile(rf"[{LO}]{{2,}}(?:ыҥ|иҥ|уҥ|үҥ|ааҥ|ээҥ|ооҥ|өөҥ)$")
SOURCE_TAG = re.compile(r"\((?:[А-ЯЁҔҤӨҺҮ]{1,3}(?:-[А-ЯЁ]{1,3})?)\)")
DEFINITION = re.compile(r"\b(?:дэнэр|дэнэллэр|диэн ааттанар|ааттанар|дииллэр|ааттыыллар)\b")
VISUAL = re.compile(
    r"ойуу(?:га|ну|тан|ттан|нан|ҕа|у|лар\w*)?\b|хартыына|хаартыска|уруһуй|исхиэмэ|схема|фишка",
    re.I)


@dataclass
class Line:
    text: str
    page: int
    source: str


@dataclass
class Exercise:
    book: str
    lesson: int
    number: int
    start: int            # line index of the header
    end: int = 0          # exclusive
    section: str = ""
    block: str = ""
    extra: dict = field(default_factory=dict)


def book_meta(book: str):
    m = re.match(r"Саха_тыла_(\d+(?:-\d+)?)(?:_(\d))?", book)
    grade, part = m.group(1), m.group(2) or ""
    return grade, part


def load(path: Path):
    """Book text -> list of Lines, minus page markers and printed page numbers."""
    lines, page, source = [], 0, "text_layer"
    raw = path.read_text(encoding="utf-8").splitlines()
    for k, ln in enumerate(raw):
        m = PAGE_RE.match(ln)
        if m:
            page, source = int(m.group(1)), m.group(2) or "text_layer"
            continue
        s = ln.strip()
        if not s:
            continue
        # printed page number: a bare number that is the page's last line
        nxt = next((r for r in raw[k + 1:] if r.strip()), "")
        if re.fullmatch(r"\d{1,3}", s) and (not nxt or PAGE_RE.match(nxt)):
            continue
        # The text layer glues a header onto the previous bullet/sentence
        # ("• … ырыт. 3. Күнү-дьылы кэтээн көр"), so split before "N. Capital".
        pieces = INLINE_NUM.split(s) if s.startswith("•") else [s]
        for piece in pieces:
            lines.append(Line(piece.strip(), page, source))
    return lines


def header_text(lines, i, limit=4):
    """The instruction: header line plus continuation lines up to sentence end."""
    m = NUM_RE.match(lines[i].text)
    parts = [m.group(2) or m.group(3) or ""]
    j = i + 1
    while j < len(lines) and len(parts) < limit:
        cur = " ".join(parts).rstrip()
        nxt = lines[j].text
        if NUM_RE.match(nxt) or nxt in HEADINGS or SECTION_RE.match(nxt):
            break
        ends = re.search(r"[.?!:»)]$", cur) and not cur.endswith("-")
        if cur and ends and not re.match(rf"[{LO}]", nxt):
            break
        parts.append(nxt)
        j += 1
    return parts, j


def instr_score(text: str) -> float:
    words = re.findall(rf"[{UP}{LO}]+", text)
    low = [w.lower() for w in words]
    s = 0.0
    if any(IMP_2PL.search(w) for w in low):
        s += 0.6
    if any(w in IMP_2SG for w in low[:12]):
        s += 0.6
    if "?" in text:
        s += 0.3
    if text.rstrip().endswith(":"):
        s += 0.2
    if SOURCE_TAG.search(text):
        s -= 0.6
    if text[:1] and re.match(rf"[{LO}]", text[:1]):
        s -= 0.3
    return max(0.0, min(1.0, s))


def choose_headers(cands, restarts: bool):
    """DP over numbered lines.

    cands: list of (line_idx, number, instr_score, hard_reset, last_inline_no).
    State = (last exercise number, last sub-item number). Returns the set of
    candidate positions read as exercise headers.

    Weights: continuing the exercise chain is worth most; a sub-item is cheap
    and preferred for lines that don't read like instructions; leaving a
    numbered line unexplained costs, so does restarting the count (a new
    lesson), unless a unit/test heading just announced one.
    """
    NEG = float("-inf")
    best = {(0, 0): (0.0, None)}  # state -> (score, backpointer)
    history = []
    for pos, (_, n, f, reset, last_inline) in enumerate(cands):
        new = {}

        def push(state, score, back):
            if score > new.get(state, (NEG,))[0]:
                new[state] = (score, back)

        for (L, s), (score, _) in best.items():
            prev = (pos, (L, s))
            push((L, s), score - 1.5, (prev, "skip"))
            # exercise header
            if n == L + 1:
                push((n, 0), score + 3 + 2 * f, (prev, "ex"))
            elif L + 1 < n <= L + 4 and L > 0:
                push((n, 0), score + 1 + 2 * f - (n - L - 1), (prev, "ex"))
            elif n == 1 and (restarts or L == 0):
                gain = (2.0 if reset else -1.5) + 2 * f
                push((1, 0), score + gain, (prev, "ex"))
            elif L == 0 and n <= 3:  # book whose first exercise we missed
                push((n, 0), score + 1 + 2 * f, (prev, "ex"))
            # misprinted number (e.g. "46." twice, "139." for 168): an
            # instruction-like line sitting where L+1 should be
            if (not restarts and L > 0 and f >= 0.5 and n >= 10
                    and n != L + 1 and abs(n - (L + 1)) <= 40):
                push((L + 1, 0), score + 2 * f - 0.5, (prev, "ex"))
            # sub-item inside the current exercise ("1. … 2. …" may share a line)
            if L > 0 and (n == s + 1 or n == 1):
                push((L, last_inline), score + 1.0 + 1.0 * (1 - f), (prev, "sub"))
        history.append(new)
        best = new

    # backtrack
    state = max(best, key=lambda k: best[k][0])
    chosen = {}  # candidate position -> canonical exercise number
    for pos in range(len(cands) - 1, -1, -1):
        score, back = history[pos][state]
        (_, prev_state), kind = back
        if kind == "ex":
            chosen[pos] = state[0]
        state = prev_state
    return chosen


def detect_headers(lines, lower: bool):
    """Return [(line_idx, number)] of exercise headers, in reading order."""
    cands = []
    reset_pending = True
    for i, ln in enumerate(lines):
        if ln.text in HEADINGS and HEADINGS[ln.text] is not None:
            reset_pending = True
        m = NUM_RE.match(ln.text)
        if not m:
            continue
        n = int(m.group(1))
        parts, _ = header_text(lines, i)
        text = " ".join(parts) or (lines[i + 1].text if i + 1 < len(lines) else "")
        last = n  # follow "1. … 2. … 3. …" written on one line
        for k in map(int, re.findall(r"(?:^|\s)(\d{1,2})\.\s", ln.text)[1:]):
            if k == last + 1:
                last = k
        cands.append((i, n, instr_score(text), reset_pending and n == 1, last))
        if n == 1:
            reset_pending = False

    chosen = choose_headers(cands, restarts=lower)
    # (line_idx, canonical number, printed number)
    return [(cands[p][0], chosen[p], cands[p][1]) for p in sorted(chosen)]


def split_buried_headers(lines, headers):
    """Find numbers missing from a chain buried mid-line and split them out.

    Between headers a and b (a < b-1 in the same chain) look for the missing
    "g. Capital…" after a sentence end, and break the line there.
    """
    splits = {}
    for (i, a, _), (j, b, _) in zip(headers, headers[1:]):
        for g in range(a + 1, b) if 1 < b - a <= 4 else ():
            pat = re.compile(rf"(?<=[.?!»)…])\s+(?={g}\.\s+[«\"(\[]?[{UP}])")
            for k in range(i, j):
                m = pat.search(lines[k].text)
                if m and k not in splits:
                    splits[k] = m.end()
                    break
    out = []
    for k, ln in enumerate(lines):
        if k in splits:
            p = splits[k]
            out += [Line(ln.text[:p].strip(), ln.page, ln.source),
                    Line(ln.text[p:].strip(), ln.page, ln.source)]
        else:
            out.append(ln)
    return out, len(splits)


def parse_book(path: Path, stats: CorpusStats):
    book = path.stem
    grade, part = book_meta(book)
    lower = grade in {"1", "2", "3", "4"}
    lines = load(path)
    headers = detect_headers(lines, lower)
    lines, n_split = split_buried_headers(lines, headers)
    if n_split:
        headers = detect_headers(lines, lower)

    # Walk the book once to attach section/block context and boundaries.
    exercises, section, block, lesson = [], "", "", 0
    hdr_at = {i: (n, printed) for i, n, printed in headers}
    for i, ln in enumerate(lines):
        if SECTION_RE.match(ln.text):
            title = ln.text
            if i + 1 < len(lines) and re.match(rf"[{LO}]", lines[i + 1].text):
                title += " " + lines[i + 1].text
            section, block = title, ""
        elif ln.text in HEADINGS and HEADINGS[ln.text] is not None:
            block = HEADINGS[ln.text]
        if i in hdr_at:
            n, printed = hdr_at[i]
            if not exercises or n <= exercises[-1].number:
                lesson += 1
            exercises.append(Exercise(book, lesson, n, i, section=section, block=block,
                                      extra={"printed": printed}))
    for a, b in zip(exercises, exercises[1:]):
        a.end = b.start
    if exercises:
        exercises[-1].end = len(lines)

    rows = []
    for ex in exercises:
        span = lines[ex.start:ex.end]
        parts, j = header_text(lines, ex.start)
        instruction = dehyphenate("\n".join(parts), stats).replace("\n", " ").strip()

        # content: until a heading/section line, or a theory paragraph (5–11)
        body, truncated = [], ""
        for k in range(j, ex.end):
            t = lines[k].text
            if t in HEADINGS or SECTION_RE.match(t):
                truncated = "heading"
                break
            starts_sentence = re.match(rf"[{UP}]", t) and (
                not body or re.search(r"[.?!:»)]$", body[-1]))
            if not lower and body and starts_sentence and DEFINITION.search(t):
                truncated = "theory"
                break
            body.append(t)
        content = dehyphenate("\n".join(body), stats).strip()
        raw = dehyphenate("\n".join(l.text for l in span), stats)

        sources = {l.source for l in span}
        pages = [l.page for l in span]
        printed = ""
        rows.append({
            "id": f"g{grade}" + (f"p{part}" if part else "")
                  + (f"-L{ex.lesson:02d}" if lower else "") + f"-{ex.number:03d}",
            "grade": grade,
            "part": part,
            "book": book,
            "lesson": ex.lesson if lower else "",
            "number": ex.number,
            "printed_number": ex.extra["printed"],
            "section": ex.section,
            "block": ex.block,
            "pdf_page_start": pages[0],
            "pdf_page_end": pages[-1],
            "instruction": instruction,
            "content": content,
            "needs_visual": int(bool(VISUAL.search(instruction))),
            "truncated": truncated,
            "source": sources.pop() if len(sources) == 1 else "mixed",
            "raw_text": raw,
        })
        del printed
    return rows


def main():
    paths = sorted(OCR_DIR.glob("*.txt"))
    stats = CorpusStats(p.read_text(encoding="utf-8") for p in paths)
    all_rows = []
    for p in paths:
        rows = parse_book(p, stats)
        all_rows += rows
        nums = [r["number"] for r in rows]
        print(f"{p.stem:28s} exercises={len(rows):4d}  max_no={max(nums) if nums else 0}"
              f"  lessons={len({r['lesson'] for r in rows}) if rows and rows[0]['lesson'] else '-'}")
    order = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10-11": 10}
    all_rows.sort(key=lambda r: (order[r["grade"]], r["part"], r["pdf_page_start"], r["number"]))
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        w.writeheader()
        w.writerows(all_rows)
    print(f"wrote {len(all_rows)} rows -> {OUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
