# TicketTrap

Our project for CptS 428/528 (Track A — AI Agent Trap and Remediation).

TicketTrap is a small help-desk app with an AI assistant that reads support tickets and writes
reports. We hide a prompt-injection attack inside a ticket and see whether the assistant can be
tricked into leaking a customer record it wasn't supposed to touch. Then we add defenses and
measure which ones actually stop it, and what they cost in legitimate task completion.

**Team:** Aman Verma, Aiden Vezzetti, Michael Morris, Tony Cao
**Repo:** https://github.com/amanverma-wsu/ticket-trap (private, coursework)

Private repo. Synthetic (fake) data and canary tokens only — never real user data.

## The idea

The assistant gets a normal job: one assigned ticket, one customer record it may read, and one
place it may send the report. The attacker can only edit the ticket text. We run the same normal
and malicious tickets three ways and measure what leaks.

The agent always has the same three tools — `read_ticket`, `read_customer_record`, `send_report`.
What it's allowed to do comes from trusted settings on our side, never from the ticket.

### The three setups we compare
1. **Baseline** — no real defense; tools wide open.
2. **Prompt-only** — we tell the assistant to treat ticket text as untrusted.
3. **App-enforced** — the backend blocks reading the wrong record or sending to the wrong place
   (we keep the prompt warning too, to measure what the backend checks add on top).

### Models we test
- `deepseek-flash` (DeepSeek-V4.1-Flash)
- `deepseek-v4-pro` (DeepSeek-V4-Pro)

Both run through DeepSeek's OpenAI-compatible API (`https://api.deepseek.com`). These are family
aliases rather than dated snapshots, so we log the exact model ID the API returns on every trial
to keep runs reproducible.

We pin the most specific model ID each provider offers (never a floating alias like `latest`) and
log the exact model ID returned on every trial, so runs are reproducible.

## Layout

\```
backend/     FastAPI + SQLite — the tools and the permission checks
agent/       our Python agent loop, tool definitions, the 3 configs
collector/   a small local server that logs any canary that leaks
frontend/    React + TypeScript + Vite — the UI
experiments/ scripts to run the trials and make the charts
cases/       benign tickets + attack tickets (held-out set kept separate)
docs/        the D1 write-up and project notes
data/        SQLite db + logs + results (git-ignored)
\```

## Setup

\```bash
cp .env.example .env            # put your own API keys in here
git config core.hooksPath .githooks   # enable the secret-scan pre-commit hook
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
\```

More setup (agent, experiments, frontend) is documented as those parts land.

## Safety

- Fake data only. No real users, ever.
- Canary tokens are random per-trial values; a canary reaching the collector is the only thing
  that counts as a leak.
- API keys stay out of the repo (`.env` is git-ignored; a pre-commit hook scans for keys).
- Everything runs on localhost; the only external calls are to the model APIs.

## Status

Work in progress, built in phases.

- [x] Phase 0 — repo hygiene & scaffold
- [x] Phase 1 — backend + permission checks
- [ ] Phase 2 — collector
- [ ] Phase 3 — agent loop
- [ ] Phase 4 — three configs + both providers
- [ ] Phase 5 — cases + harness + classifier
- [ ] Phase 6 — metrics + analysis
- [ ] Phase 7 — frontend
- [ ] Phase 8 — docker + reproducibility
- [ ] Phase 9 — real run
- [ ] Phase 10 — report + packaging

## Running the harness

Requires Python 3.10.

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python -m experiments.harness

This runs the full pipeline from a clean checkout with no API key, writes
`data/results.csv`, and prints the attack leak rate per configuration.
Run the test suite with `python -m pytest -q`.
