# vals_90 runs

Published dataset: `yakut/vals-90@1`, immutable tag `v-1bfbfdb0441b`.

All 15 runs cover the same 90 tasks and were launched concurrently on Modal.
Per-answer deadline: 900 seconds. Requested output: 33,000 tokens, except
Gemma 4 31B at its API maximum of 16,384. Judge: GPT-6.1 Sol, 16,000 tokens.

| Model Name | Company | Run ID |
|---|---|---|
| Claude Fable 5.2 | Anthropic | `fea1bf47-69ec-41d4-867d-60734be402aa` |
| GPT-6 Astra | OpenAI | `392e635e-43cb-4d96-91f5-b5f728bb4830` |
| DeepSeek V4 Pro | DeepSeek | `1428ce18-270f-4702-aa74-9e7d8eda37f0` |
| Gemini 4 Argon | Google | `67d02148-9c8a-48d3-b8ca-49320ee76828` |
| GLM 5.3 | Z.ai | `ac59a29b-ee79-4750-bac2-ec6caf01a34f` |
| Grok 4.7 | SpaceX (xAI) | `35066cb0-074c-43c1-8942-743618bea169` |
| Gemma 4 31B | Google | `fc476ce6-16cc-4fe7-aac4-5509213e553a` |
| DeepSeek V4.1 Flash | DeepSeek | `f7c85dc8-c344-4a9e-be91-7bf445c4a8da` |
| Inkling | Thinking Machines Lab | `747d869c-d2db-4809-9431-23728b19c25e` |
| Inkling 2 Small | Thinking Machines Lab | `0b505d8b-b6eb-47c5-b229-200e381b0115` |
| Qwen3.8 Max | Alibaba | `8768945e-709f-447b-a486-15a0dba17a51` |
| Qwen3.8 Flash | Alibaba | `cc31a145-a908-4c92-985c-381ede148b0c` |
| Qwen3.8 27B | Alibaba | `7ba85ffb-bfb4-4e27-b260-3e9f6b4dd62e` |
| GPT-6.1 Sol (judge model) | OpenAI | `42b7c992-7578-4dcc-84cf-bfc40a5d53d9` |
| GigaChat 3.5 Ultra | Sber | `ea9722af-0fc1-47e1-9c5e-aec72c891dd9` |

Inspect any run with:

```bash
valkyrie run fetch fea1bf47-69ec-41d4-867d-60734be402aa
valkyrie tui
```

The input preserves all 90 selected rows, including 12 original picture flags.
Models receive text only. Five exercise-specific `eval_instruction` values are
provided to the judge, and excluded from solver input.

## Direct Modal inference recovery

The following runs retry only API-error tasks from the original runs.
The frozen question data and prompts are unchanged; task network allowlists
add the direct Modal endpoints. Dataset: `yakut/vals-90@2`, immutable tag
`v-e5b42b1c83d9`. Settings: [`models_vals_modal.toml`](../models_vals_modal.toml).
Completed answers from the original runs are preserved.

| Model Name | Questions retried | Run ID |
|---|---:|---|
| Inkling 2 Small | 2 | `328f7e27-a17f-4282-aac8-833e01177130` |
| DeepSeek V4.1 Flash | 81 | `d056dfe2-98a5-41ec-baac-db1368e32ae7` |

## Grok failed-request retry

On 2026-11-15 at 22:18 UTC, retried only `g3p2-L10-012` within run
`35066cb0-074c-43c1-8942-743618bea169`. The 89 graded answers were preserved.
The frozen agent and original settings were retained: 33,000 requested output
tokens, high reasoning, no tools, and a 900-second deadline. Retry concurrency: 1.

## Qwen3.8 27B direct Modal retry

Retried the 86 API-error questions using the same `Qwen/Qwen3.8-27B` weights
(revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`) on a dedicated H200
endpoint. The four graded original answers are retained.

- Run ID: `06783219-342e-4d8f-88cf-3ba050122b7a`
- Dataset: `yakut/vals-90@3`, immutable tag `v-260492c98b2d`
- Concurrency: 16; requested output limit: 33,000; answer deadline: 900 seconds
- Native reasoning: `xhigh`. Qwen's native API rejects `high`; `xhigh` is its
  documented highest/default reasoning level. This provider translation is
  recorded in `models_vals_modal.toml`.
- The endpoint returns to zero minimum GPU containers after the retry ends.

The managed presets for DeepSeek V4 Pro, Qwen3.8 Flash, and Gemma 4 31B currently
reject this workspace with a B200/Starter-plan access error. No substitute
checkpoints are merged into the original scores. Gemini 4 Argon and Qwen3.8 Max
0902 have no matching native Modal endpoint. At that snapshot, the available
Inkling NVFP4 variant had not been substituted. The expanded round below uses
the subsequently approved Qwen and Inkling replacements as fresh runs.

## Custom H200 recovery queue

Gemma 4 31B (24 failed questions) and Qwen3.8 Flash (53 failed questions) have
custom H200 servers and are queued for automatic readiness-checked recovery.
The watcher is `valkyrie/retry_modal.py`, using
`valkyrie/modal_recovery_plan.json`. It records run IDs when each server is ready.
Model revisions are pinned in the corresponding server source files.
Gemma retains non-thinking mode and 16,384 output tokens. Qwen Flash uses its
native `xhigh` reasoning tier and 33,000 output tokens. Both retain the
900-second answer deadline and original judge instructions.

## Expanded Modal round — November 16, 2026

Dataset: `yakut/vals-90@5`, immutable tag `v-0d2ba4f2b9e1`.
Agent: `yakut-text-modal-v4`. All four runs started in parallel at 04:52 UTC,
with eight concurrent tasks per model, 33,000 requested output tokens and a
900-second answer deadline. Each endpoint passed a generation smoke check.

| Model Name | Company | Modal serving mode | Run ID |
|---|---|---|---|
| Muse Spark Open | Meta | Shared | `8e70e46b-67bd-468b-b1b2-a06ff2a4db28` |
| Qwen3.8 2.4T A95B | Alibaba | Shared | `f3f61471-6fd1-4bb5-90d0-0bcbb47141f4` |
| Kimi K3.1 Pro | Moonshot AI | Shared | `aafbccc6-2ee5-469c-973e-5d5dd725cd21` |
| Inkling NVFP4 | Thinking Machines Lab | Shared | `c739bc58-e018-4453-b0f6-8209eb90ea53` |

Qwen3.8 2.4T A95B replaces the original Max-0902 row, and Inkling NVFP4
replaces the original Inkling row, as requested. Both run all 90 questions;
previous variant answers are archived and never merged into these scores.
Earlier model variants remain in the run records above.
Native reasoning is `xhigh` for Qwen and `high` for the other three models.
Question text, solver instructions, and judge instructions have the same
hashes as the preceding round. The judge still receives `eval_instruction`;
the solver does not. Only endpoint network allowlists changed in the tasks.

[Endpoint IDs, model IDs, and frozen hashes](modal_round4.json) ·
[Model settings](../models_vals_modal.toml)

To inspect these runs, use `valkyrie run fetch RUN_ID`. To reproduce the agent
bundle, build with `valkyrie/build.py`, `data/vals_90.jsonl`,
`prompts/solver_system.md`, `prompts/vals_90_judge.md`, and
`--models-config models_vals_modal.toml --allow-visual-text`.
Upload the resulting agent and task folders before starting a fresh run.

Dedicated endpoints are supported by the evaluator: the earlier Qwen3.8 27B
recovery used one successfully. Fresh managed dedicated deployments for
DeepSeek V4 Pro, Qwen3.8 Flash-Next, and Gemma 4 31B still fail with
`B200 GPUs are not available on the Starter plan`. No plan upgrade was made.
Shared endpoints bill per token; included Modal plan credits do not cover
shared endpoint usage. Dedicated endpoints bill for compute resources.

## Additional OpenRouter models — November 16, 2026

These independent 90-question runs use agent `yakut-text-expanded-v6` and
dataset `yakut/vals-90@v-166c93db5539` (see the machine-readable record for
the immutable version). Inference uses OpenRouter; Modal hosts the task
sandboxes. The solver/judge prompts and answer deadlines are unchanged.

| Model Name | Company | Initial concurrent questions | Run ID |
|---|---|---:|---|
| Mistral Large 4 | Mistral AI | 16 | `68907664-2ca6-4a51-8087-eba7f8329e5e` |
| MiniMax M3.1 Flash | MiniMax | 16 | `0f3cfd53-5d8c-49fc-9514-931372f8ada2` |
| Claude Opus 5.5 | Anthropic | 8 | `ee5e19ac-6533-4259-8957-ce3b0403a75d` |

Each requests high reasoning and 33,000 output tokens, with a 900-second
answer deadline. The original Opus judge configuration is unchanged;
`opus-5.5-eval` is a separate solver configuration using OpenRouter.
[Settings and frozen hashes](openrouter_round5.json).
Mistral's concurrency was subsequently raised from 16 to 24; model generation
settings were unchanged.

## Dedicated Gemma recovery — November 16, 2026

The managed Gemma endpoint still requires B200 access. Its original weights
were instead served on a dedicated H200 Modal server, `ykt-gemma-h200/Gemma`.
The endpoint passed a generation check with non-thinking mode and the original
16,384-token output limit. At 05:01 UTC, run
`f4fa983d-07d3-4886-909e-d866a6b48ea1` started the 24 previously failed tasks
at concurrency 16, preserving all 66 completed original answers. The answer
deadline remains 900 seconds. The server returns to zero minimum containers
after the recovery run ends. [Recovery settings and task IDs](dedicated_recovery.json).

At about 05:01 UTC, a batch across the expanded runs failed with Modal sandbox
infrastructure errors (`sandbox_get` authorization/internal service errors).
Only failed tasks were retried, with frozen agents and model settings retained.
These infrastructure failures are distinct from incorrect model answers.

## Gemini 4 Carbon — separate OpenRouter account

Run `e4410ff4-0d45-4301-9ea5-3ba9c5009129` evaluates all 90 questions with
`google/gemini-4-carbon`, high reasoning, 33,000 requested output tokens, and
a 900-second answer deadline. It uses agent `yakut-text-expanded-v7` and
the dedicated credential variable `SARA_OPENROUTER_API_KEY`, bound to the
Valkyrie secret `ykt-sara-openrouter-api-key`. The fresh Inkling flagship run
below uses the same separate key; other models retain their original keys.
Only secret names are committed; the key value stays in the ignored `.env`
and Valkyrie's secret store.

Carbon replaces the empty Argon row in the current 90-question leaderboard.
The original Argon run is archived in the run records.
[Run metadata](gemini_carbon_run.json).
Concurrency was subsequently raised from 8 to 24, then reduced when OpenRouter
reported insufficient available credits for concurrent in-flight requests.
Completed tasks were not restarted.

## Inkling flagship — separate OpenRouter account

Run `1e31e4ec-5a7a-403b-a986-cb7c88cfbf9b` evaluates the original
`thinkingmachines/inkling` flagship on all 90 questions, using
`SARA_OPENROUTER_API_KEY`, high reasoning, 33,000 requested output tokens,
and a 900-second answer deadline. The agent is `yakut-text-expanded-v8`.
This is a fresh run: the earlier seven answers from the original account
remain archived and are not merged. The concurrent Inkling NVFP4 evaluation
on Modal remains a separate row. [Run metadata](inkling_sara_run.json).
Concurrency was subsequently raised from 8 to 16, then reduced in response to
the separate account's credit-reservation errors. Completed tasks were not restarted.

The optional dedicated Inkling NVFP4 probe did not finish startup within
its readiness window and was stopped to release its four B300 GPUs.
The shared NVFP4 run continues; no answers from the probe enter the benchmark.

## Dedicated Qwen Flash recovery

The earlier H200 startup failure was traced to 33 missing weight shards.
`valkyrie/preload_qwen_flash.py` completes the pinned checkpoint download on
CPU and verifies every shard referenced by the index before GPU startup.
The repaired four-H200 server passed a generation check using `xhigh`
reasoning and a 33,000-token limit.

Run `08199a4a-8a30-49a2-9cad-135cc9c680e6` retries the 53 failed Qwen Flash
questions at concurrency 16, preserving the original 37 graded answers.
It uses agent `yakut-text-expanded-v8`; each answer keeps the 900-second
deadline. The server returns to zero minimum containers after the run ends.
[Recovery settings and task IDs](dedicated_recovery.json).

## Expanded snapshot before personal-account credit recovery

The expanded leaderboard has 18 complete 90-question model results out of 21.
Both dedicated recoveries finished: Gemma completed all 24 retry tasks and
Qwen Flash completed all 53 retry tasks. Their earlier answers were retained.
Both servers were returned to zero minimum containers after evaluation.
No newly evaluated model reported output above its requested token limit.

Gemini Carbon stopped after 48 graded questions and the fresh Inkling flagship
run stopped after 55 when the separate OpenRouter account exhausted its credits.
Their remaining queued tasks were stopped, and completed answers remain saved
for resumption after funding. DeepSeek V4 Pro remains at its earlier 23 graded
questions because this workspace cannot deploy its B200-based managed endpoint.

## Personal-account credit recovery

After the account was funded, the existing Gemini Carbon and Inkling flagship
runs resumed only their unfinished tasks: 42 for Gemini and 35 for Inkling.
The 48 Gemini answers and 55 Inkling answers already graded were preserved.
Both continue using `SARA_OPENROUTER_API_KEY`, their frozen agents, high
reasoning, a 33,000-token output limit, and a 900-second answer deadline.
The model runs execute in parallel; request concurrency is adjusted to the
available account balance to avoid the earlier credit-reservation errors.

DeepSeek V4 Pro is excluded from the current 90-question leaderboard as
requested. Its run history is retained for provenance.

## Final funded results

After the additional personal-account top-up, Gemini Carbon's concurrency was
raised to 16. The existing run finished all 90 questions on 2026-11-16; Inkling
flagship also finished all 90. Completed answers were preserved throughout;
only unfinished/API-failed tasks were resumed, with frozen model settings.

| Model Name | Correct | All | Partial credit | Max reported output tokens |
|---|---:|---:|---:|---:|
| Gemini 4 Carbon | 46/90 | 51.1% | 59.3% | 33,000 |
| Inkling | 20/90 | 22.2% | 41.9% | 33,000 |

Neither run reported output above the requested limit or a solver timeout.
All 20 models included in [the leaderboard](../LEADERBOARD.md) now have 90 graded
questions. Grok's earlier maximum report of 51,390 tokens and its limit flags
remain preserved. Final selected-response cost and latency metadata are saved
in [the metrics snapshot](../data/leaderboard_metrics.json); those costs exclude
judging, failed/discarded attempts, and Modal hosting.

## Community Sakha fine-tunes — November 17, 2026

Three open-weight Sakha fine-tunes, and then ten more models from lab-ii
([below](#lab-ii-models)), were evaluated on all 90 questions with the
local runner (`run_parallel.py`), not on Valkyrie. Run directory:
`results/vals_90_local`; there are no hosted run IDs.

| Model Name | Weights | Revision |
|---|---|---|
| Yakut Qwen3.5 4B GRPO | `loalkota/yakut-qwen3.5-4b-grpo-merged` | `eca1ccbcdfdb058d2375960feb0b8988839eb94d` |
| Qwen3.5 27B Sah | `lab-ii/Qwen3.5-27B-sah` | `5eda5ca74c904f7d757e3288f560378f7cfd2d7b` |
| TABIS 1.1 0.8B (experimental) | `tabisai/tabis-1.1-experimental`, `source/merged-hf-bf16` | `216a80251f3c8c9d5eefbcb9d5fed55ef41ae6c0` |

- Serving: vLLM 0.34.0 on one H200, original BF16 weights, 65,536-token context,
  one model at a time. The evaluator
  reaches the server through an SSH tunnel.
- Solver settings are unchanged: same solver prompt, no tools, 33,000 requested
  output tokens, 900-second answer deadline, 16 concurrent questions.
- Each model uses its own chat template and default mode: thinking is on for the
  two larger models (vLLM `qwen3` reasoning parser; only the final answer is
  graded) and off for TABIS, whose template disables it.
- Qwen3.5 27B Sah ships the base Qwen3.5 `generation_config.json` (temperature
  0.6, top_p 0.95, top_k 20, EOS `<|im_end|>` and `<|endoftext|>`). The other two
  merges dropped it and stop only on `<|endoftext|>`, so the same base values are
  passed explicitly in [`models_vals_modal.toml`](../models_vals_modal.toml).
- TABIS is saved as a multimodal Qwen3.5 class without preprocessor files; the
  base `Qwen/Qwen3.5-0.8B` `preprocessor_config.json` and
  `video_preprocessor_config.json` were placed next to it so it loads. Weights,
  tokenizer and template are untouched.
- Judge: the same GPT-6.1 Sol model, high reasoning, 16,000 tokens and the same
  judge prompt, but routed through Cloud.ru's Chat Completions endpoint with a
  strict JSON schema (`sol-6.1-cloudru`), because no OpenAI key was available.
  Earlier rows were graded through OpenAI's Responses API.
- Cost columns are dashes: there is no API price for self-hosted weights.
  Latency is measured on the dedicated H200 and is not comparable to API rows.

### lab-ii models

Ten more open-weight models from [lab-ii](https://huggingface.co/lab-ii) were
evaluated the same way on the same day: same run directory, solver settings,
judge route and H200, one model at a time.

| Model Name | Weights | Revision | Context | Chat template |
|---|---|---|---:|---|
| Aina 14B Instruct (2025-10-01) | `lab-ii/Aina-14B-Instruct-01-10-2025` (gated) | `4baaacaba2` | 40,960 | repository's own |
| Aina 14B Instruct (2025-10-21) | `lab-ii/Aina-14B-Instruct-21-10-2025` | `aa4eab3b562cdfa330588f3bdd87bd1cc614896e` | 40,960 | repository's own |
| TranslateGemma 12B Sah | `lab-ii/translategemma-12b-it-sah` | `82e352846d0549c91ece4278de0799303ad0361e` | 65,536 | Gemma 3 |
| Qwen3 4B Sah (base) | `lab-ii/qwen3-4b-base` | `6b23264ce081e025359f1dc5f3b82869c73da31c` | 32,768 | repository's own |
| Qwen3 4B Sah (instruct) | `lab-ii/qwen3-4b-instruct` | `8f49b36d4676311982aad5c973990912759fea6f` | 40,960 | repository's own |
| Gemma 4B Sah (base) | `lab-ii/gemma-4b-base` | `5f975e0fad00d0a416ef76442a000fe12d8154a6` | 65,536 | Gemma 3 |
| Gemma 4B Sah (instruct) | `lab-ii/gemma-4b-instruct` | `181798f0efd7d5c0993ec4ee641d5c5bc66ecb6c` | 65,536 | Gemma 3 |
| Llama 3.2 Sah (base) | `lab-ii/llama3.2-base` | `1540b69a07ccc3e8363bc9c9087777a28ff16ee6` | 65,536 | Llama 3 |
| Llama 3.2 Sah (instruct) | `lab-ii/llama3.2-instruct` | `e2f27380ddd67b5ce3cf60549f94d73e36d78706` | 65,536 | Llama 3 |
| TinyLlama Sakha Instruct | `lab-ii/TinyLlama-Sakha-Instruct` | `efe21dd4c368f61d992a5c42cc476f237feae421` | 2,048 | Alpaca |

- The three base checkpoints (Qwen3 4B, Gemma 4B, Llama 3.2) were run but are not
  listed on the leaderboard: they are continued-pretraining models, not
  assistants. Their answers and grades stay in the run directory.
- Several of these are continued-pretraining ("base") checkpoints or a
  translation model, not chat assistants. They are served as chat models
  anyway, so their rows measure how they behave when asked the benchmark
  questions directly.
- Repositories without a chat template get their base family's template. The
  Gemma template folds the system prompt into the first user turn; TinyLlama
  uses the Alpaca prompt from its model card, with the system prompt and the
  question joined into the instruction.
- The Gemma-family repositories ship no image-processor files, so the base
  Gemma 3 preprocessor configs were placed next to the weights so they load.
  Weights and tokenizers are untouched. Weights stored as float32 are served as
  bfloat16.
- Sampling comes from each repository's `generation_config.json` where it sets
  any, otherwise vLLM defaults. TinyLlama uses its card's settings (temperature
  0.7, top_k 50, top_p 0.95). End-of-turn and end-of-text stop tokens are passed
  explicitly for every model because several configs list only end-of-text.
- Context is the smaller of the serving default and the model's own limit. Two
  models cannot hold the 33,000-token output budget: TinyLlama (2,048) and
  Qwen3 4B Sah base (32,768). For them the request carries no output cap.
  TinyLlama then uses whatever the prompt leaves; for Qwen3 4B Sah base the
  server applied the repository's own `max_new_tokens` of 2,048, which cut 41
  of its 90 answers short. None of the 90 contained a final-answer marker.
- The vLLM `qwen3` reasoning parser is used only for the two Aina models, which
  emit `<think>` blocks. The two Qwen3 4B checkpoints never emit them, so the
  parser filed their whole output as reasoning and returned empty answers. That
  first Qwen3 4B Sah (instruct) run was discarded and both were run without the
  parser.
- `lab-ii/Aina-14B-Instruct-01-10-2025` is gated; it was fetched with an
  authorised Hugging Face login and each shard's SHA-256 was checked. One
  `qwen3-4b-base` shard arrived truncated and was replaced and checked the same
  way.
