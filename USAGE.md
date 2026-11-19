# Running the Yakut benchmark

The current benchmark contains 90 questions. See [the leaderboard](LEADERBOARD.md),
[dataset provenance](data/README.md), and [hosted run records](valkyrie/RUNS.md).
The README's opening paragraph is the human-written benchmark overview.

## Environment

Use Python 3.12 or later and install the dependencies:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Set the credentials for the selected providers in `.env`, which is ignored by
Git. Existing environment variables take precedence. `SARA_OPENROUTER_API_KEY`
is a separate account binding for Gemini 4 Carbon and Inkling flagship.
Dedicated Modal routes also require `MODAL_INFERENCE_API_KEY`.

`models_vals_modal.toml` contains the expanded model configuration used by the
current leaderboard. `models_vals.toml` records the original 90-question launch
configuration, and the frozen Harbor bundle retains its own configuration.
The run records describe route changes and dedicated endpoint recoveries.

## Local evaluation

Validate credentials and settings for the models you intend to run:

```bash
.venv/bin/python ykt_eval.py check \
  --config models_vals_modal.toml --models astra --judges sol-6.1
```

Run models in parallel with grading overlapping generation:

```bash
.venv/bin/python run_parallel.py \
  --data data/vals_90.jsonl \
  --solver-system prompts/solver_system.md \
  --judge-system prompts/vals_90_judge.md \
  --config models_vals_modal.toml \
  --run-dir results/vals_90_local \
  --workers-per-model 16 --grok-workers 90
```

The default selection matches the current leaderboard. Pass `--models astra,grok-4.7`
to select a subset. Run directories contain responses, judgments, progress,
metadata, and per-model logs. Rerunning the same command resumes missing or
API-failed items; successful answers are retained regardless of correctness.
Dataset and instruction hashes prevent accidental reuse across incompatible runs.

Solvers have no tools or browsing, a 900-second answer deadline, and a requested
33,000 output token limit. Gemma's provider cap is 16,384. Provider-reported
overshoots are retained and flagged in the saved results. GPT-6.1 Sol uses a
16,000-token judging budget; its own evaluated row is marked as the judge model.
The solver receives the instruction and exercise content. The judge also receives
the reference answer and each question's `eval_instruction`.

## Self-hosted open-weight models

Serve one model with vLLM on a GPU host, forward its port with
`ssh -N -L 18000:127.0.0.1:8000 <gpu-host>` and set `LOCAL_INFERENCE_API_KEY`
to the server's `--api-key`. Run `run_parallel.py` with `--models <alias>`
(add `--judge sol-6.1-cloudru` to grade through Cloud.ru with `CLOUDRU_API_KEY`).

## Hosted evaluation and leaderboard refresh

Follow [the Valkyrie adapter guide](valkyrie/README.md) to build Harbor tasks,
publish the dataset, and start hosted runs. The tracked submission bundle is
frozen provenance; use a new output directory for a new build.

Collect the existing hosted runs and update the leaderboard:

```bash
uv run --python 3.12 --with valkyrie-cli python valkyrie/collect.py \
  --runs results/vals_90/valkyrie_runs.json \
  --out results/vals_90/hosted --artifacts
.venv/bin/python valkyrie/leaderboard.py
.venv/bin/python leaderboard_metrics.py --fetch-costs --refresh-pricing --publish
```

The local run registry is produced by the publisher; hosted run IDs and recovery
records are documented in `valkyrie/RUNS.md`. The generated `LEADERBOARD.md` is
sorted by All accuracy and includes a separate cost and latency table. Costs
marked `*` are estimates at the recorded input/output token rates. Known API
charges use provider generation metadata where available; the table notes
coverage and exclusions. Local evaluation results remain separate from the
published hosted leaderboard.
