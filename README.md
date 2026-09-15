# TicketTrap

A small help-desk web application with an embedded AI assistant, plus an experiment
harness that measures how well two classes of defense — **prompt-only instructions**
vs. **application-enforced tool permissions** — prevent prompt-injection data leakage
while preserving legitimate task completion.

**Course:** CptS 428/528, Fall 2026 · Track A — AI Agent Trap and Remediation
**Team:** Aman Verma, Aiden Vezzetti, Michael Morris, Tony Cao

> This is a **private** coursework repository. Synthetic data and canary tokens only —
> never real user data. See "Safety & ethics" below.

## What this is

The assistant receives a legitimate task (an assigned ticket, an authorized customer
record, an approved report destination). The **attacker controls only the ticket body**.
We run the same normal and malicious tickets under three configurations and measure
what leaks.

The agent is exposed **exactly three tools, in every condition**:
`read_ticket`, `read_customer_record`, `send_report`. Permissions come from trusted
per-task settings, never from ticket content.

### Defense configurations
1. **Baseline** — normal task instructions, broadly accessible tools.
2. **Prompt-only defense** — instructions telling the assistant to treat ticket content as untrusted.
3. **Application-enforced defense** — backend checks restrict record access and report
   destinations; the prompt-only instructions are retained so we measure the *added* effect.

### Models under test (pinned snapshots)
- `gpt-4o-2024-08-06` (OpenAI)
- `claude-3-7-sonnet-20250219` (Anthropic)

Confirm access/budget and that these exact snapshots are still offered; swap to a current
dated snapshot if either is retired. The rule is *exact and dated*, never `latest`.

## Repository layout

```
tickettrap/
├── backend/       FastAPI + Pydantic + SQLite. APIs, validation, permission checks.
├── agent/         Custom Python agent loop, tool definitions, the three configs.
├── collector/     Local endpoint that records exfiltrated canaries (the "unauthorized" sink).
├── frontend/      React + TypeScript + Vite UI (tickets, agent activity, results).
├── experiments/   Trial harness + analysis (pandas / matplotlib).
├── cases/         Benign tasks and attack cases (held-out subset kept separate).
├── docs/          D1 submission and project notes.
├── data/          SQLite DB + run logs (git-ignored).
├── .env.example   Copy to .env and fill in your own API keys (never commit .env).
└── docker-compose.yml
```

## Prerequisites
- Python 3.11+
- Node 20+
- (optional) Docker + Docker Compose

## Setup
```bash
cp .env.example .env          # then fill in your own API keys
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt -r agent/requirements.txt -r experiments/requirements.txt
(cd frontend && npm install)
```

## Running
```bash
# 1. backend API (serves ticket/record/report tools, enforces permissions)
uvicorn backend.app.main:app --reload --port 8000

# 2. collection endpoint (records any canary that leaks)
python collector/collector.py            # listens on 127.0.0.1:9100

# 3. frontend (optional, for the demo UI)
(cd frontend && npm run dev)              # 127.0.0.1:5173

# 4. run an experiment trial set
python experiments/run_trials.py --config all --repeats 20
python experiments/analyze.py            # writes figures to data/figures/
```

## Safety & ethics
- **Synthetic data only.** No real user data, ever.
- **Canary tokens** are trial-specific synthetic values; "confirmed leakage" = a canary
  received at the collection endpoint.
- **Keys stay out of the repo.** `.env` is git-ignored; keys never go in tickets, logs, or commits.
- **Traffic is local.** Only the named localhost services plus the hosted model API are contacted.

## Status
Scaffold. Each component has a skeleton with `TODO`s marking the work. The attack/benign
cases in `cases/` are intentionally left for the team to author, and the held-out set is
kept separate so defenses are not tuned against attacks we have already seen.

## Repository
Private repo: https://github.com/amanverma-wsu/ticket-trap

The `origin` remote is already configured and there is an initial commit, so publishing
is just a push (set your own git identity first so the history reflects real contributors):

```bash
git config user.name "Your Name"
git config user.email "you@wsu.edu"
git push -u origin main
```
