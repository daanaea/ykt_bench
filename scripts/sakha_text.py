"""Corpus-level repairs for Sakha text extracted from the textbook PDFs.

The lower-grade PDFs' text layer has three systematic word-level defects:
  * words broken by a stray space or "- " where the print had a line-break
    hyphen ("көр дөрөр", "кэп- сээ"),
  * hyphenated compounds whose hyphen was dropped ("Күндьыл" for "Күн-дьыл"),
  * Ҕ/Ҥ in all-caps headings mapped to Ў/ў.
Fixing them needs word statistics from the whole corpus, so this module builds
those once and applies conservative, frequency-backed repairs.
"""
import re
from collections import Counter

L = "а-яёҕҥөһүА-ЯЁҔҤӨҺҮ"
WORD = re.compile(f"[{L}]+")
LINE_HYPHEN = re.compile(f"([{L}])-\n([{L}])")
MID_HYPHEN_WORD = re.compile(f"(?<![{L}-])([{L}]+)-([{L}]+)(?![{L}-])")


def fix_glyphs(text: str) -> str:
    return text.replace("Ў", "Ҕ").replace("ў", "Ҥ")


class CorpusStats:
    def __init__(self, texts):
        self.words = Counter()      # plain tokens, lowercase
        self.hyph = Counter()       # "a-b" compounds keyed by lowercase "ab"
        self.hyph_form = {}         # lowercase "ab" -> most common "a-b" surface
        forms = Counter()
        for t in texts:
            t = fix_glyphs(t)
            joined = LINE_HYPHEN.sub(r"\1\2", t)
            self.words.update(w.lower() for w in WORD.findall(joined))
            for line in t.splitlines():
                for a, b in MID_HYPHEN_WORD.findall(line):
                    key = (a + b).lower()
                    self.hyph[key] += 1
                    forms[(key, f"{a}-{b}".lower())] += 1
        for (key, form), _ in forms.most_common():
            self.hyph_form.setdefault(key, form)

    def is_compound(self, joined: str) -> bool:
        """True if the corpus mostly writes this word with a hyphen."""
        k = joined.lower()
        form = self.hyph_form.get(k, "")
        if len(k) < 4 or min(map(len, form.split("-", 1)), default=0) < 2:
            return False  # "ч-ү"-style notation, not a compound word
        h, p = self.hyph[k], self.words[k]
        # plain counts include the very corruption we're fixing, so allow ties
        return (h >= 2 and h >= 2 * p) or (h >= 3 and h >= p)

    def join(self, a: str, b: str) -> str:
        """Join two fragments of one word, keeping a hyphen for compounds."""
        if self.is_compound(a + b):
            return _match_case(a, self.hyph_form[(a + b).lower()])
        return a + b


def _match_case(src: str, form: str) -> str:
    return form[0].upper() + form[1:] if src[:1].isupper() else form


def repair(text: str, st: CorpusStats) -> str:
    text = fix_glyphs(text)
    # "кэп- сээ" -> "кэпсээ" (mid-line leftover of a line-break hyphen).
    # Skip when both sides are real words: in table rows "көмө- а)" is two cells.
    def broken(m):
        a, b = m.group(1), m.group(2)
        ab = (a + b).lower()
        if st.words[ab] or st.hyph[ab] or min(st.words[a.lower()], st.words[b.lower()]) <= 1:
            return st.join(a, b)
        return m.group(0)
    text = re.sub(f"([{L}]+)- ([а-яёҕҥөһү]+)", broken, text)

    # "көр дөрөр" -> "көрдөрөр": join only when the joined word is attested
    # and one fragment is not a real word on its own.
    def merge(m):
        a, b = m.group(1), m.group(2)
        ab = (a + b).lower()
        if st.words[ab] >= 3 and min(st.words[a.lower()], st.words[b.lower()]) <= 2:
            return st.join(a, b)
        return m.group(0)
    pair = re.compile(f"(?<![{L}-])([{L}]+) ([а-яёҕҥөһү]+)(?![{L}-])")
    for _ in range(2):  # words split into three pieces need two passes
        text = pair.sub(merge, text)

    # "Күндьыл" -> "Күн-дьыл" when the corpus overwhelmingly hyphenates it
    def rehyphen(m):
        w = m.group(0)
        return _match_case(w, st.hyph_form[w.lower()]) if st.is_compound(w) else w
    text = re.sub(f"(?<![{L}-])[{L}]+(?![{L}-])", rehyphen, text)
    return text


def dehyphenate(text: str, st: CorpusStats) -> str:
    """Undo line-break hyphenation: "са-\\nлаата" -> "салаата"."""
    return re.sub(f"([{L}]+)-\n([{L}]+)",
                  lambda m: st.join(m.group(1), m.group(2)), text)
