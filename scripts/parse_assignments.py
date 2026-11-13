#!/usr/bin/env python3
"""Parse numbered exercises (assignments) out of the extracted textbook text.

Input:  ocr/ykt_language/*.txt   (from extract_text.py)
        data/icons.csv           (from detect_icons.py, optional)
Output: data/ykt_language_assignments.csv

The text layer carries no fonts or layout, so exercise headers ("61. Күрэхтэһиҥ…")
look exactly like numbered sub-items inside an exercise ("1. Будулҕан тумаҥҥа…").
We pick the headers with a small dynamic program over every numbered line:
  * exercise numbers form a chain n, n+1, n+2… (grades 5–11 number the whole
    book; grades 1–4 restart at 1 every lesson),
  * tests/exams in grades 5–11 run their own 1…N "side chain", after which
    the main numbering resumes,
  * sub-item lists restart at 1 inside an exercise,
  * headers read like instructions (imperative verbs, questions).
The highest-scoring reading of the numbered lines wins.

Usage: python3 scripts/parse_assignments.py [ocr_dir] [out_csv]
"""
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sakha_text import CorpusStats, dehyphenate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OCR_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "ocr" / "ykt_language"
OUT_CSV = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data" / "ykt_language_assignments.csv"
ICONS_CSV = ROOT / "data" / "icons.csv"

UP = "А-ЯЁҔҤӨҺҮ"
LO = "а-яёҕҥөһү"
PAGE_RE = re.compile(r"^===== page (\d+)(?: \[(\w+)\])? =====$")
NUM_RE = re.compile(rf"^(\d{{1,3}})(?:\.(?:\s+(.*))?|\s+([«\"]?[{UP}].*))$")
SECTION_RE = re.compile(r"^\d{1,3}\s?§\.?\s*\S")
INLINE_NUM = re.compile(rf"(?<=[.?!»)])\s+(?=\d{{1,3}}\.\s+[«\"(\[]?[{UP}])")
# grade 9 review section: "1 сорудах. …" (task) and "1 эрчиллии. …" (exercise)
REVIEW_RE = re.compile(r"^(\d{1,2}) (сорудах|эрчиллии)\.\s*(.*)$")
# a test/exam heading starts a side chain of its own 1…N questions
SIDE_WORD = re.compile(r"(?i)тургутук\s*$|эксээмэн")
# answer keys and the table of contents close the part of a book with tasks
END_RE = re.compile(r"(?i)^(?:оонньуулар таайыылара|таайбараҥнар эппиэттэрэ:?|"
                    r"таабырыннар эппиэттэрэ:?|тургутуктар хоруйдара|\d барыйаан хоруйа|"
                    r"иһинээ.итэ)$")


class _SideRe:
    """Heading-like lines naming a test or exam (not sentences mentioning one)."""
    @staticmethod
    def search(text):
        return (len(text) < 60 and not re.match(r"\d", text)
                and not re.search(r"[.?!]$", text) and SIDE_WORD.search(text))


SIDE_RE = _SideRe()

# Recurring headings: they end an exercise's content and set its "block".
HEADINGS = {
    "Ситимнээх саҥа": "coherent_speech",
    "БИЛИИБИТИН БЭРЭБИЭРКЭЛЭНЭБИТ": "test",
    "Хатылааһын": "review",
    "СҮБЭ": None,                               # advice box, not a block
    "Үөрэнэр соругум": "",                      # unit start (grades 1–4)
    "Үөрэнэр сорукпун хайдах толордум": "",     # self-assessment after a test
}

# 2nd-person-singular imperatives common in instructions.
IMP_2SG = set("""
аах бул суруй ырыт тупсар хоруйдаа уһул оҥор туруор таай быһаар ый көр бэлиэтээ
толкуйдаа уларыт таһаар араар ситэр тарт эт кэпсээ наардаа үөрэт холбоо ааттаа
тэҥнээ сааһылаа ситимнээ толор уус ус кэпсэт ыллаа истэ иһит булан түмүктээ
сыаналаа санаа бэлэмнээ дакаастаа ааҕан хатылаа уруһуйдаа тылбаастаа тал
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
    number: int
    printed: str
    start: int            # line index of the header
    chain: str            # main | lesson | side | review
    chain_no: int = 0     # lesson / side-chain index
    end: int = 0          # exclusive
    section: str = ""
    block: str = ""


LETTER = f"[{UP}{LO}]"
SPACED = re.compile(rf"(?<!\S)(?:{LETTER} ){{3,}}{LETTER}(?!\S)")


def tidy(text: str) -> str:
    """Collapse letter-spaced emphasis ("Х о л о б у р") and runs of spaces."""
    text = SPACED.sub(lambda m: m.group(0).replace(" ", ""), text)
    return re.sub(r"[ \t]{2,}", " ", text)


def book_meta(book: str):
    m = re.match(r"Саха_тыла_(\d+(?:-\d+)?)(?:_(\d))?", book)
    return m.group(1), m.group(2) or ""


def is_stop(text: str) -> bool:
    """Lines that end an exercise's content."""
    return (text in HEADINGS or bool(SECTION_RE.match(text)) or bool(SIDE_RE.search(text))
            or bool(REVIEW_RE.match(text)) or bool(re.fullmatch(r"\d чааһа", text)))


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
        if END_RE.match(s):
            break
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
    if m:
        parts = [m.group(2) or m.group(3) or ""]
    else:
        parts = [REVIEW_RE.match(lines[i].text).group(3)]
    j = i + 1
    while j < len(lines) and len(parts) < limit:
        cur = " ".join(parts).rstrip()
        nxt = lines[j].text
        if NUM_RE.match(nxt) or is_stop(nxt):
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


def choose_headers(cands, lower: bool):
    """DP over numbered lines.

    cands: list of (line_idx, number, instr_score, lesson_reset, side_reset,
    last_inline_no). State = (L main/lesson number, s sub-item number,
    T side-chain number). Returns {cand_pos: (number, kind)}, kind ∈ ex|side.

    Weights: continuing a chain is worth most; a sub-item is cheap and
    preferred for lines that don't read like instructions; leaving a numbered
    line unexplained costs, so does restarting the count (a new lesson) unless
    a heading just announced one.
    """
    NEG = float("-inf")
    best = {(0, 0, 0): (0.0, None)}
    history = []
    for pos, (_, n, f, reset, side_reset, side_break, last_inline) in enumerate(cands):
        new = {}

        def push(state, score, back):
            if score > new.get(state, (NEG,))[0]:
                new[state] = (score, back)

        for (L, s, T0), (score, _) in best.items():
            T = 0 if side_break else T0  # a heading closed the test
            prev = (pos, (L, s, T0))
            push((L, s, T), score - 1.5, (prev, "skip"))
            # main-chain exercise header (leaves any side chain)
            if n == L + 1:
                push((n, 0, 0), score + 3 + 2 * f, (prev, "ex"))
            elif L + 1 < n <= L + 4 and L > 0:
                push((n, 0, 0), score + 1 + 2 * f - (n - L - 1), (prev, "ex"))
            elif n == 1 and (lower or L == 0):
                gain = (2.0 if reset else -1.5) + 2 * f
                push((1, 0, 0), score + gain, (prev, "ex"))
            elif L == 0 and n <= 3:  # book whose first exercise we missed
                push((n, 0, 0), score + 1 + 2 * f, (prev, "ex"))
            # misprinted number ("46." twice, "139." for 168): an
            # instruction-like line sitting where L+1 should be
            if (not lower and L > 0 and f >= 0.5 and n >= 10
                    and n != L + 1 and abs(n - (L + 1)) <= 40):
                push((L + 1, 0, 0), score + 2 * f - 0.5, (prev, "ex"))
            # test/exam questions: their own 1…N chain (grades 5–11)
            if not lower:
                if n == 1 and side_reset:
                    push((L, 0, 1), score + 2 + 2 * f, (prev, "side"))
                elif T > 0 and n == T + 1:
                    push((L, 0, n), score + 2.5 + 2 * f, (prev, "side"))
            # sub-item inside the current exercise ("1. … 2. …" may share a line)
            if (L > 0 or T > 0) and (n == s + 1 or n == 1):
                push((L, last_inline, T), score + 1.0 + 1.0 * (1 - f), (prev, "sub"))
        history.append(new)
        best = new

    state = max(best, key=lambda k: best[k][0])
    chosen = {}
    for pos in range(len(cands) - 1, -1, -1):
        _, back = history[pos][state]
        (_, prev_state), kind = back
        if kind == "ex":
            chosen[pos] = (state[0], "ex")
        elif kind == "side":
            chosen[pos] = (state[2], "side")
        state = prev_state
    return chosen


def detect_headers(lines, lower: bool):
    """[(line_idx, number, printed, kind)] of exercise headers in reading order."""
    cands = []
    reset_pending, side_pending, side_break = True, False, False
    for i, ln in enumerate(lines):
        if ln.text in HEADINGS and HEADINGS[ln.text] is not None:
            reset_pending = True
        if SIDE_RE.search(ln.text) or re.fullmatch(r"\d чааһа", ln.text):
            side_pending = True
        if (ln.text in HEADINGS or SECTION_RE.match(ln.text)
                or re.fullmatch(rf"[{UP}IVX\s.,:—-]{{5,}}", ln.text)):
            side_break = True
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
        cands.append((i, n, instr_score(text), reset_pending and n == 1,
                      side_pending and n == 1, side_break, last))
        reset_pending = side_pending = side_break = False

    chosen = choose_headers(cands, lower)
    return [(cands[p][0], num, str(cands[p][1]), kind)
            for p, (num, kind) in sorted(chosen.items())]


def split_buried_headers(lines, headers):
    """Find numbers missing from a chain buried mid-line and split them out.

    Between consecutive headers a and b (a < b-1) look for the missing
    "g. Capital…" after a sentence end, and break the line there.
    """
    splits = {}
    for (i, a, _, ka), (j, b, _, kb) in zip(headers, headers[1:]):
        if ka != kb:
            continue
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


def load_icons():
    """(book, page, number) -> [icon labels] for icons that sit by a number."""
    icons = defaultdict(list)
    if ICONS_CSV.exists():
        with ICONS_CSV.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["number"]:
                    icons[(r["book"], int(r["page"]), int(r["number"]))].append(r["label"])
    return icons


def parse_book(path: Path, stats: CorpusStats, icons):
    book = path.stem
    grade, part = book_meta(book)
    lower = grade in {"1", "2", "3", "4"}
    lines = load(path)
    headers = detect_headers(lines, lower)
    lines, n_split = split_buried_headers(lines, headers)
    if n_split:
        headers = detect_headers(lines, lower)

    # Walk the book once to attach section/block context and boundaries.
    exercises, section, block, side_title = [], "", "", ""
    lesson = side = 0
    hdr_at = {i: (n, printed, kind) for i, n, printed, kind in headers}
    for i, ln in enumerate(lines):
        if SECTION_RE.match(ln.text):
            title = ln.text
            if i + 1 < len(lines) and re.match(rf"[{LO}]", lines[i + 1].text):
                title += " " + lines[i + 1].text
            section, block = title, ""
        elif ln.text in HEADINGS and HEADINGS[ln.text] is not None:
            block = HEADINGS[ln.text]
        elif SIDE_RE.search(ln.text) and len(ln.text) < 60 and not ln.text.endswith("."):
            side_title = ln.text
        elif ln.text == "үөрэппити хатылааһын":
            section = "Алын кылаастарга үөрэппити хатылааһын"
        rm = REVIEW_RE.match(ln.text)
        if rm:  # grade 9 end-of-book review: two interleaved numberings
            kind = "review_task" if rm.group(2) == "сорудах" else "review_exercise"
            exercises.append(Exercise(int(rm.group(1)), rm.group(1), i, kind,
                                      section=section, block="review"))
        elif i in hdr_at:
            n, printed, kind = hdr_at[i]
            if kind == "side":
                if n == 1:
                    side += 1
                exercises.append(Exercise(n, printed, i, "side", side,
                                          section=side_title, block="test"))
            else:
                prev_main = [e for e in exercises if e.chain in ("main", "lesson")]
                if lower and (not prev_main or n <= prev_main[-1].number):
                    lesson += 1
                exercises.append(Exercise(n, printed, i, "lesson" if lower else "main",
                                          lesson if lower else 0,
                                          section=section, block=block))
    for a, b in zip(exercises, exercises[1:]):
        a.end = b.start
    if exercises:
        exercises[-1].end = len(lines)

    rows = []
    for ex in exercises:
        span = lines[ex.start:ex.end]
        parts, j = header_text(lines, ex.start)
        instruction = tidy(dehyphenate("\n".join(parts), stats).replace("\n", " ")).strip()

        # content: until a heading/section line, or a theory paragraph (5–11)
        body, truncated = [], ""
        for k in range(j, ex.end):
            t = lines[k].text
            if is_stop(t):
                truncated = "heading"
                break
            starts_sentence = re.match(rf"[{UP}]", t) and (
                not body or re.search(r"[.?!:»)]$", body[-1]))
            if not lower and body and starts_sentence and DEFINITION.search(t):
                truncated = "theory"
                break
            body.append(t)
        content = tidy(dehyphenate("\n".join(body), stats)).strip()
        raw = tidy(dehyphenate("\n".join(l.text for l in span), stats))

        prefix = {"main": "", "lesson": f"-L{ex.chain_no:02d}", "side": f"-T{ex.chain_no}",
                  "review_task": "-RS", "review_exercise": "-RE"}[ex.chain]
        page0 = span[0].page
        sources = {l.source for l in span}
        icon = icons.get((book, page0, int(ex.printed)), [])
        rows.append({
            "id": f"g{grade}" + (f"p{part}" if part else "") + f"{prefix}-{ex.number:03d}",
            "grade": grade,
            "part": part,
            "book": book,
            "chain": ex.chain,
            "lesson": ex.chain_no or "",
            "number": ex.number,
            "printed_number": ex.printed,
            "section": ex.section,
            "block": ex.block,
            "icon": "; ".join(dict.fromkeys(icon)),
            "pdf_page_start": page0,
            "pdf_page_end": span[-1].page,
            "instruction": instruction,
            "content": content,
            "needs_visual": int(bool(VISUAL.search(instruction))),
            "truncated": truncated,
            "source": sources.pop() if len(sources) == 1 else "mixed",
            "raw_text": raw,
        })
    return rows


GRADE_ORDER = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10-11": 10}


def main():
    paths = sorted(OCR_DIR.glob("*.txt"))
    stats = CorpusStats(p.read_text(encoding="utf-8") for p in paths)
    icons = load_icons()
    all_rows = []
    for p in paths:
        rows = parse_book(p, stats, icons)
        all_rows += rows
        by = defaultdict(int)
        for r in rows:
            by[r["chain"]] += 1
        print(f"{p.stem:28s} rows={len(rows):4d}  " + "  ".join(f"{k}={v}" for k, v in by.items())
              + f"  with_icon={sum(1 for r in rows if r['icon'])}")
    all_rows.sort(key=lambda r: (GRADE_ORDER[r["grade"]], r["part"], r["pdf_page_start"]))
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        w.writeheader()
        w.writerows(all_rows)
    print(f"wrote {len(all_rows)} rows -> {OUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
