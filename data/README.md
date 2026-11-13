# Саха тыла assignments (grades 1–11)

Built from `ykt_textbooks/ykt_language/*.pdf` by:

```
python3 scripts/extract_text.py      # PDFs -> ocr/ykt_language/*.txt
python3 scripts/detect_icons.py      # page images -> data/icons.csv (~3 min)
python3 scripts/parse_assignments.py # -> data/ykt_language_assignments.csv
python3 scripts/map_answers.py       # -> data/ykt_language_assignments_mapped.csv
```

## `ykt_language_assignments.csv` — every numbered assignment (4,397 rows)

| column | meaning |
|---|---|
| `id` | `g{grade}[p{part}][-L{lesson}\|-T{test}\|-RS\|-RE]-{number}`, e.g. `g3p1-L04-013`, `g9-089`, `g10-11-T2-005` |
| `grade`, `part`, `book` | `part` is 1/2 for two-volume grades |
| `chain` | `lesson` (grades 1–4 restart numbering each lesson), `main` (grades 5–11 number the whole book), `side` (tests/exam with their own 1…N), `review_task` / `review_exercise` (grade 9 end-of-book review: "N сорудах." / "N эрчиллии.") |
| `lesson` | lesson index (grades 1–4) or test index (`side`) |
| `number`, `printed_number` | position in the chain; differs from the printed number where the book misprints (grade 9: "46." twice, "47." for 53, "139." for 168) |
| `section`, `block` | nearest `§` heading or test title; block = `coherent_speech` (Ситимнээх саҥа), `test`, `review` |
| `icon` | task-type mark from the book's legend (Болдьох бэлиэ), e.g. `уустук сорудах`, `оонньуу`, `тыл баайа`; empty if none |
| `pdf_page_start/end` | PDF page = printed page number in all books |
| `instruction` | the task statement (line-break hyphenation removed) |
| `content` | material the task works on, up to the next heading / theory paragraph |
| `needs_visual` | 1 if the instruction refers to a picture, scheme, chart or chips |
| `truncated` | `heading` / `theory` when `content` was cut short; full span is in `raw_text` |
| `source` | `text_layer`, `vision` (grade 9 pp. 45–88, transcribed from images), or `mixed` |
| `raw_text` | everything from this header to the next one |

Icon sets: grades 1–4 — билсиһии, бодоруһуу, дьарык, ыраастык суруйуу, оонньуу,
суругунан үлэ, сыаналаныы, тыл баайа; grades 5–9 — өйдөө/болҕой, саҥаны билии,
кэтээн көрүү, бодоруһуу, хатылааһын, уустук сорудах, оонньуу, кэпсэтии сиэрэ;
grades 10–11 — өйдөө/болҕой, кэтээн көрүү, бодоруһуу, уустук сорудах,
литэрэтиирэни кытта ситим, ай-тут.

## `ykt_language_assignments_mapped.csv` — assignments with an answer in the book (192 rows)

Same columns plus `answer`, `answer_key` (key heading + page/question), `answer_key_page`
and `mapping`:

| `mapping` | how the answer was tied to the assignment |
|---|---|
| `test+number` | grades 10–11 Тургутуктар хоруйдара, by test name + question no. (43) |
| `exam+number` | grade 9 exam, "1 барыйаан хоруйа" table (9) |
| `icon` | page-keyed answer → the exercise on that page with the оонньуу icon (99) |
| `instruction` | → the exercise on that page whose instruction is a riddle/rebus/puzzle (28) |
| `only_exercise_on_page` | the page has one exercise (2) |
| `page_only` | weakest: no game-like exercise found on that page — check before use (11) |

Grade 8 has no answer key; grade 9's only key is for the exam.

## Known gaps

- Grades 1–4: 15 numbers (across 253 lessons) are missing (header absent or out of order in the
  text layer). Grade 9: no. 83 has no number in the text layer and is merged into no. 82.
- Content boundaries come from text alone; some theory paragraphs without a
  definitional marker remain at the end of `content`.
- Lower-grade text layer still has a few split or joined words that couldn't be
  repaired safely.
