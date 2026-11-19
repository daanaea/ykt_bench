# YktBench: Sakha (Yakut) Language Primary School Knowledge Benchmark

This benchmark evaluates how well language models understand, write, and reason in Sakha (Yakut). Questions are drawn from text-only exercises in Sakha primary school textbooks (grades 1-4).

## Public test set

The [90-question dataset](data/vals_90.jsonl) comes from the `vals sub` sheet of
[`vals_90.xlsx`](data/vals_90.xlsx). The current leaderboard covers 20 models evaluated
on Valkyrie and Modal, plus ten community Sakha fine-tunes evaluated with the local
runner on a self-hosted GPU, with all 90 questions graded for each model. The failure
examples below count the original 20 models.

Each solver receives the exercise instruction and material. The judge receives
the answer key and any exercise-specific `eval_instruction`; those instructions
are never shown to the solver. The five supplied grading instructions override
the generic rubric where specified, including accepted Russian spellings.

## Results

See **[Leaderboard](LEADERBOARD.md)** for accuracy by model and school grade, partial credit, token usage, and an extended cost and latency table.

All models seem to have shallow vocabulary, fail to capture cultural code, and still make morphological mistakes in word formation. They are suprisingly good at supporting natural conversation though, until asked harder questions that show lack of depth in understanding Sakha language and culture.

### 1. Proverb: real word, wrong proverb

**Task:** Кистэлэҥ сурук. Буукубалары сааһылаан өс хоһоонун таһаар.  
*(Secret message. Unscramble the letters to reveal the proverb.)*

```
Үгсэ ыкайбаатҕын үсэб ыкайра.
```

**Reference:** Сүгэ кыайбатаҕын сүбэ кыайар. *(What an axe can't overcome, counsel will.)*  
**Fable:** Үгэс кыайбатаҕын сүбэ кыайар.

Fable turned the letters into **Үгэс** ("custom") instead of **Сүгэ** ("axe"). The word exists, but the proverb doesn't. Any native speaker knows this saying by heart.

### 2. Riddles: cultural code is missing

Sakha riddles depend on shared cultural imagery. **None of the 20 models solved all six, and 15 solved none.**

| Riddle | Answer | Models correct | Accuracy | Fable |
|---|---|---:|---:|:---:|
| 1. Кэллэрбин эрэ кэпсиэм… | Кэҕэ *(cuckoo)* | **1/20** | 5% | ✗ |
| 2. Соруннарбын эрэ субурутуом… | Өрүс эстэрэ *(river ice breakup)* | **0/20** | 0% | ✗ |
| 3. Турдарбын халлааҥҥа тиийиэм… | Суол *(road)* | **4/20** | 20% | ✓ |
| 4. Миигинэ суох ханна да олоруоххут суоҕа… | Дьиэ *(house)* | **0/20** | 0% | ✗ |
| 5. Испэр киириэҥ — мэҥиэстиэм… | Сохсо *(trap)* | **0/20** | 0% | ✗ |
| 6. Хараҕа суоҕу харахтыам… | Үөрэх кинигэтэ *(textbook)* | **0/20** | 0% | ✗ |

- **Riddle 1:** solved only by DeepSeek V4.1 Flash.
- **Riddle 3:** solved by Claude Fable 5.2, Claude Opus 5.5, GPT-6 Astra and GPT-6.1 Sol.

**Overall: 5 of 120 answers correct (4.2%).**

### 3. Word choice: shallow vocabulary and morphology

Fill in the blank. Common words like **билбэккэ** are easy. Rarer ones like **үгэнэ** trip up most models.

| Sentence | Answer | Models correct | Accuracy | Fable |
|---|---|---:|---:|:---:|
| Кыһын үлэ-хамнас … | 2) үгэнэ | **7/20** | 35% | ✓ |
| Ыраах алаастан от-мас … | 3) тиэйиллэр | **8/20** | 40% | ✗ |
| Күн аайы муус-мас киллэриитэ, хотон бүппэт … | 4) түбүгэ | **13/20** | 65% | ✓ |
| Кыһыҥҥы кылгас күн киирбитин … хаалыаҕыҥ. | 2) билбэккэ | **16/20** | 80% | ✓ |

Only Claude Opus 5.5 and Qwen3.8 Flash got all four. Fable got 3/4. It chose **тиэйэллэр** ("they haul") instead of **тиэйиллэр** ("is hauled"). The sentence needs the passive because от-мас is the subject. That's a word-formation error.

