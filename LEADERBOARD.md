# Leaderboard

Last updated: Nov 17, 2026

> Are frontier models able to complete primary school students' assignments in Sakha (Yakut) language?

A set of 90 test problems from elementary school Sakha language textbooks from Grade 1 to Grade 4.
Consists of text-only problems, mainly consisting of grammar problems and riddles.

Judge model: GPT-6.1 Sol. No internet access or tools. 900-second time limit, 33k token output limit.

| Model Name | Company | All | Partial credit | Grade 1 | Grade 2 | Grade 3 | Grade 4 | Max reported output tokens |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Claude Fable 5.2 | Anthropic | **64.4** | 78.7 | 90.9 | 56.0 | 71.4 | 50.0 | 14149 |
| Gemini 4 Carbon | Google | 51.1 | 59.3 | 45.5 | 48.0 | 67.9 | 41.7 | 33000 |
| GPT-6 Astra | OpenAI | 41.1 | 61.2 | 45.5 | 44.0 | 39.3 | 37.5 | 21775 |
| Claude Opus 5.5 | Anthropic | 41.1 | 63.2 | 27.3 | 40.0 | 42.9 | 45.8 | 15301 |
| GPT-6.1 Sol | OpenAI | 38.9 | 58.8 | 45.5 | 36.0 | 50.0 | 25.0 | 28446 |
| DeepSeek V4.1 Flash | DeepSeek | 25.6 | 42.3 | 45.5 | 20.0 | 32.1 | 16.7 | 33000 |
| Qwen3.8 2.4T A95B | Alibaba | 24.4 | 37.4 | 9.1 | 36.0 | 25.0 | 20.8 | 33000 |
| Inkling NVFP4 | Thinking Machines Lab | 24.4 | 40.8 | 45.5 | 24.0 | 21.4 | 20.8 | 33000 |
| Grok 4.7 | SpaceX (xAI) | 23.3 | 32.3 | 18.2 | 32.0 | 28.6 | 12.5 | **51390** |
| Inkling 2 Small | Thinking Machines Lab | 22.2 | 34.5 | 27.3 | 16.0 | 32.1 | 16.7 | 33000 |
| Inkling | Thinking Machines Lab | 22.2 | 41.9 | 27.3 | 16.0 | 25.0 | 25.0 | 33000 |
| Muse Spark Open | Meta | 21.1 | 41.8 | 18.2 | 24.0 | 17.9 | 25.0 | 33000 |
| GLM 5.3 | Z.ai | 14.4 | 21.9 | 18.2 | 12.0 | 21.4 | 8.3 | 33000 |
| Qwen3.8 Flash | Alibaba | 14.4 | 18.8 | 9.1 | 20.0 | 17.9 | 8.3 | 33000 |
| Kimi K3.1 Pro | Moonshot AI | 12.2 | 21.1 | 9.1 | 12.0 | 10.7 | 16.7 | 33000 |
| Qwen3.5 27B Sah | lab-ii | 11.1 | 16.6 | 18.2 | 24.0 | 3.6 | 4.2 | 33000 |
| Qwen3.8 27B | Alibaba | 6.7 | 9.3 | 9.1 | 0.0 | 10.7 | 8.3 | 33000 |
| GigaChat 3.5 Ultra | Sber | 6.7 | 14.2 | 9.1 | 12.0 | 3.6 | 4.2 | 900 |
| Gemma 4 31B | Google | 4.4 | 6.4 | 0.0 | 8.0 | 3.6 | 4.2 | 16384 |
| Mistral Large 4 | Mistral AI | 3.3 | 3.9 | 0.0 | 8.0 | 3.6 | 0.0 | 33000 |
| Aina 14B Instruct (2025-10-01) | lab-ii | 3.3 | 9.0 | 0.0 | 8.0 | 0.0 | 4.2 | 33000 |
| MiniMax M3.1 Flash | MiniMax | 2.2 | 2.7 | 0.0 | 4.0 | 0.0 | 4.2 | 33000 |
| Aina 14B Instruct (2025-10-21) | lab-ii | 2.2 | 8.0 | 9.1 | 4.0 | 0.0 | 0.0 | 33000 |
| TABIS 1.1 0.8B (experimental) | tabis | 1.1 | 1.5 | 0.0 | 4.0 | 0.0 | 0.0 | 33000 |
| Qwen3 4B Sah (instruct) | lab-ii | 1.1 | 2.2 | 0.0 | 0.0 | 3.6 | 0.0 | 33000 |
| Yakut Qwen3.5 4B GRPO | loalkota | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 33000 |
| TinyLlama Sakha Instruct | lab-ii | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 485 |
| Llama 3.2 Sah (instruct) | lab-ii | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 33000 |
| Gemma 4B Sah (instruct) | lab-ii | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 33000 |
| TranslateGemma 12B Sah | lab-ii | 0.0 | 0.9 | 0.0 | 0.0 | 0.0 | 0.0 | 323 |

### Cost and latency

| Model Name | Company | Avg in s | Median in s | p95 in s | Max in s | Timeouts # | Input token # | Output token # | Usage coverage | Input $/1M | Output $/1M | Estimated cost $ | Actual API cost $ | Cost coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Fable 5.2 | Anthropic | 16.7 | 8.4 | 48.7 | 195.6 | 0 | 38,014 | 111,826 | 90/90 | 8 | 40 | 4.7772* | 4.7772* | 0/90 |
| Gemini 4 Carbon | Google | 288.3 | 283.0 | 619.1 | 720.3 | 0 | 31,429 | 1,668,456 | 90/90 | 2 | 10 | 16.7474* | 16.7474 | 90/90 |
| GPT-6 Astra | OpenAI | 63.7 | 31.0 | 235.4 | 563.7 | 0 | 27,768 | 215,344 | 90/90 | 10 | 50 | 11.0449* | 11.0449* | 0/90 |
| Claude Opus 5.5 | Anthropic | 21.4 | 13.5 | 63.5 | 182.9 | 0 | 38,014 | 140,984 | 90/90 | 4 | 20 | 2.9717* | 2.9717 | 90/90 |
| GPT-6.1 Sol **(judge model)** | OpenAI | 56.5 | 23.8 | 179.6 | 608.1 | 0 | 27,768 | 210,598 | 90/90 | 2 | 10 | 2.1615* | 2.1615* | 0/90 |
| DeepSeek V4.1 Flash | DeepSeek | 66.2 | 46.7 | 186.6 | 253.3 | 0 | 31,010 | 1,096,750 | 90/90 | 0.14 | 0.42 | 0.4650* | 0.0866 | 9/90 |
| Qwen3.8 2.4T A95B | Alibaba | 97.5 | 68.1 | 220.7 | 239.7 | 0 | 34,056 | 1,374,978 | 90/90 | 2 | 6 | 8.3180* | 8.3180* | 0/90 |
| Inkling NVFP4 | Thinking Machines Lab | 102.7 | 89.9 | 252.8 | 282.1 | 0 | 28,398 | 1,066,946 | 90/90 | 1 | 4.05 | 4.3495* | 4.3495* | 0/90 |
| Grok 4.7 | SpaceX (xAI) | 601.3 | 696.2 | 900.0 | 900.0 | 29 | 93,698† | 1,578,639† | 61/90 | 2 | 6 | 9.6592*† | 9.5342 | 61/90 |
| Inkling 2 Small | Thinking Machines Lab | 94.2 | 69.5 | 310.6 | 385.4 | 0 | 30,830 | 1,423,542 | 90/90 | 0.3 | 1 | 1.4328* | 1.3956 | 88/90 |
| Inkling | Thinking Machines Lab | 103.1 | 90.8 | 252.5 | 273.7 | 0 | 28,488 | 1,096,215 | 90/90 | 1 | 4.05 | 4.4682* | 4.4601 | 90/90 |
| Muse Spark Open | Meta | 39.5 | 24.1 | 128.1 | 168.6 | 0 | 40,129 | 756,005 | 90/90 | 1.25 | 4.25 | 3.2632* | 3.2632* | 0/90 |
| GLM 5.3 | Z.ai | 139.0 | 80.3 | 428.1 | 534.2 | 0 | 29,788 | 1,422,380 | 90/90 | 0.0699 | 1.4 | 1.9934* | 4.2059 | 90/90 |
| Qwen3.8 Flash | Alibaba | 290.3 | 308.5 | 480.2 | 503.3 | 0 | 34,056 | 2,298,689 | 90/90 | 0.15 | 0.47 | 1.0855* | 0.4729 | 37/90 |
| Kimi K3.1 Pro | Moonshot AI | 45.3 | 29.9 | 186.3 | 230.6 | 0 | 37,198 | 554,751 | 90/90 | 0.2403 | 8.4023 | 4.6701* | 4.6701* | 0/90 |
| Qwen3.5 27B Sah | lab-ii | 158.0 | 67.2 | 687.1 | 695.0 | 0 | 30,636 | 718,939 | 90/90 | — | — | — | — | 0/90 |
| Qwen3.8 27B | Alibaba | 234.5 | 254.8 | 322.4 | 900.0 | 3 | 32,625† | 2,015,027† | 87/90 | 0.15 | 1.875 | 3.7831*† | 0.0941 | 4/90 |
| GigaChat 3.5 Ultra | Sber | 3.5 | 2.8 | 9.9 | 19.0 | 0 | 33,650 | 8,263 | 90/90 | 1.07 | 3.21 | 0.0625* | 0.0625* | 0/90 |
| Gemma 4 31B | Google | 18.5 | 8.1 | 62.8 | 329.6 | 0 | 29,739 | 130,015 | 90/90 | 0.2 | 0.4 | 0.0580* | 0.0366 | 66/90 |
| Mistral Large 4 | Mistral AI | 207.9 | 241.1 | 334.4 | 371.0 | 0 | 26,891 | 2,086,691 | 90/90 | 0.7 | 2.1 | 4.4009* | 4.4081 | 89/90 |
| Aina 14B Instruct (2025-10-01) | lab-ii | 6.3 | 1.0 | 2.3 | 316.0 | 0 | 30,586 | 53,131 | 90/90 | — | — | — | — | 0/90 |
| MiniMax M3.1 Flash | MiniMax | 127.6 | 133.8 | 268.2 | 363.2 | 0 | 46,129 | 2,066,608 | 90/90 | 0.15 | 0.6 | 1.2469* | 1.2124 | 90/90 |
| Aina 14B Instruct (2025-10-21) | lab-ii | 4.8 | 1.1 | 2.7 | 311.6 | 0 | 30,586 | 38,000 | 90/90 | — | — | — | — | 0/90 |
| TABIS 1.1 0.8B (experimental) | tabis | 2.4 | 1.0 | 1.4 | 61.3 | 0 | 30,173 | 69,355 | 90/90 | — | — | — | — | 0/90 |
| Qwen3 4B Sah (instruct) | lab-ii | 408.2 | 441.9 | 598.7 | 632.4 | 0 | 37,459 | 2,574,796 | 90/90 | — | — | — | — | 0/90 |
| Yakut Qwen3.5 4B GRPO | loalkota | 20.8 | 1.8 | 191.6 | 192.1 | 0 | 26,181 | 315,529 | 90/90 | — | — | — | — | 0/90 |
| TinyLlama Sakha Instruct | lab-ii | 1.2 | 1.2 | 1.9 | 2.3 | 0 | 30,730 | 6,090 | 90/90 | — | — | — | — | 0/90 |
| Llama 3.2 Sah (instruct) | lab-ii | 354.0 | 354.7 | 433.6 | 462.2 | 0 | 29,939 | 2,937,370 | 90/90 | — | — | — | — | 0/90 |
| Gemma 4B Sah (instruct) | lab-ii | 175.4 | 151.8 | 314.9 | 315.2 | 0 | 37,358 | 1,662,904 | 90/90 | — | — | — | — | 0/90 |
| TranslateGemma 12B Sah | lab-ii | 1.9 | 1.8 | 3.6 | 4.2 | 0 | 29,004 | 11,132 | 90/90 | — | — | — | — | 0/90 |

$\text{Estimated cost} = \frac{\text{reported input tokens × input price + reported output tokens × output price}}{1,000,000}$

Estimates use the current OpenRouter catalog's standard base rates; GigaChat uses user-supplied rates of $1.07 input and $3.21 output per 1M tokens.

These are API-equivalent estimates for logged usage, not historical bills or Modal GPU costs. Missing usage is not extrapolated to the full dataset.

Caching, batch discounts, time-of-day offers, and context-tier adjustments are not applied; recorded charges can differ.

Inkling NVFP4 uses standard Inkling API prices for its estimate; its Modal serving variant is recorded separately.

Known API cost shows the sum of retrieved OpenRouter charges when available; otherwise it shows the token-based estimate marked with \*. It is not total benchmark spend.

A dash means no reported token usage or charge is available, not free. Cost coverage counts only answers with a retrieved charge, including when a starred estimate is displayed; duplicate request IDs are charged once.

Judging, discarded/failed attempts, Modal token or GPU hosting charges (including warmup), storage, and net credit adjustments are excluded.

Provider changes and native reasoning translations remain documented in the run notes; latency figures are not measurements of thinking time.

[Metric and pricing snapshot](data/leaderboard_metrics.json) · [Current OpenRouter pricing catalog](https://openrouter.ai/api/v1/models) · [OpenRouter cost metadata](https://openrouter.ai/docs/api/api-reference/generations/get-generation)

Qwen3.5 27B Sah, TABIS 1.1 0.8B, Yakut Qwen3.5 4B GRPO and seven other lab-ii models (Aina, TranslateGemma, and the instruct versions of Qwen3 4B, Gemma 4B, Llama 3.2 and TinyLlama) are community Sakha fine-tunes served from their open weights with vLLM on one H200 and evaluated with the local runner; their cost columns are dashes and their latency is not comparable to API rows. They were graded by the same GPT-6.1 Sol judge through Cloud.ru. [Run notes](valkyrie/RUNS.md#community-sakha-fine-tunes--november-17-2026).

GPT-6.1 Sol grades with a 16,000-token
budget and receives each question's `eval_instruction`; solvers do not.

Max reported output tokens is the largest downloaded usage report, including reasoning tokens where reported.
Usage for unfinished runs may cover only a subset of graded answers.
Full run status and token-limit flags remain in the [saved results](valkyrie/leaderboard_snapshot.json).



[Run IDs](valkyrie/RUNS.md) · [Dataset](data/vals_90.jsonl) · [Settings](models_vals.toml)
