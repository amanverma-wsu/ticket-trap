# TicketTrap

Our project for CptS 428/528 (Track A: AI Agent Trap and Remediation).

TicketTrap is a small help-desk app with an AI assistant that reads support tickets and writes
reports. We hide a prompt-injection attack inside a ticket and check whether the assistant can be
tricked into leaking a customer record it was not supposed to touch. We then add defenses and
measure which ones stop it, and what they cost in legitimate task completion.

Team: Aman Verma, Aiden Vezzetti, Michael Morris, Tony Cao
Repository: https://github.com/amanverma-wsu/ticket-trap (private, coursework)

Synthetic (fake) data and canary tokens only, never real user data.

## The idea

The assistant gets a normal job: one assigned ticket, one customer record it may read, and one
place it may send the report. The attacker can only edit the ticket text. We run the same normal
and malicious tickets under three configurations and measure what leaks.

The agent always has the same three tools: `read_ticket`, `read_customer_record`, and
`send_report`. What it is allowed to do comes from trusted settings on our side, never from the
ticket.

## The three configurations we compare

1. Baseline: no real defense; the tools are wide open.
2. Prompt-only: we tell the assistant to treat ticket text as untrusted.
3. App-enforced: the backend blocks reading the wrong record or sending to the wrong place. We keep
   the prompt warning too, so we can measure what the backend checks add on top of it.

## Models we test

We run two DeepSeek models through OpenRouter's OpenAI-compatible API
(`https://openrouter.ai/api/v1`):

- `deepseek/deepseek-v4.1-flash`
- `deepseek/deepseek-v4-pro-0813`

We avoid floating aliases such as the `...-latest` slugs. OpenRouter can route a slug to different
backend providers, so we log the exact model ID the API returns on every trial to keep runs
reproducible.

## Layout

```
backend/      FastAPI + SQLite: the tools and the permission checks
agent/        the Python agent loop, tool definitions, and the three configs
collector/    a small local server that logs any canary that leaks
frontend/     React + TypeScript + Vite: the UI
experiments/  the harness, classifier, and analysis
cases/        benign tickets and attack tickets (held-out set kept separate)
docs/         the D1 and D2 write-ups and project notes
data/         SQLite db, logs, and results (git-ignored)
```

## Running the harness

Requires Python 3.10. From a clean clone of the repository:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m experiments.harness
```

This runs the full pipeline from a clean checkout with no API key. It wires the backend and
collector in process, drives them with a deterministic offline reference agent, writes
`data/results.csv`, and prints the attack leak rate per configuration. Run the test suite with:

```bash
python -m pytest -q
```

## Development setup

For live-model runs and contributing:

```bash
cp .env.example .env
git config core.hooksPath .githooks
```

Put your OpenRouter API key in `.env` for live-model runs. The `core.hooksPath` line enables the
pre-commit hook that scans staged files for keys.

## Safety

- Fake data only. No real users.
- Canary tokens are random per-trial values. A canary reaching the collector is the only thing that
  counts as a leak.
- API keys stay out of the repository. `.env` is git-ignored, and a pre-commit hook scans for keys.
- Everything runs on localhost. The only external calls are to the model API.

## Status

Built in phases.

- [x] Phase 0: repo hygiene and scaffold
- [x] Phase 1: backend and permission checks
- [x] Phase 2: collector
- [x] Phase 3: agent loop
- [x] Phase 4: three configs and the model provider
- [x] Phase 5: cases, harness, and classifier
- [ ] Phase 6: metrics and analysis
- [ ] Phase 7: frontend
- [ ] Phase 8: docker and reproducibility
- [ ] Phase 9: live-model run
- [ ] Phase 10: report and packaging
