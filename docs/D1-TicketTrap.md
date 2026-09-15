# D1 — Team, Track, Target, and Scope
**CptS 428/528, Fall 2026 · Track A: AI Agent Trap and Remediation · Project: TicketTrap**

---

## 1. Team

- Aman Verma — CptS 428
- Aiden Vezzetti — CptS 428
- Michael Morris — CptS 428
- Tony Cao — CptS 428

---

## 2. Track

**Track A: AI Agent Trap and Remediation.**

We build a tool-using help-desk agent (not an autonomous browser agent), plant a prompt-injection trap in
untrusted ticket content, and measure how well two classes of defense, prompt-only instructions versus
application-enforced tool permissions, prevent confidential data leakage while preserving legitimate task
completion.

**Research question.** How effectively do application-enforced tool permissions prevent prompt-injection data
leakage compared with prompt-only defenses, while preserving legitimate task completion?

---

## 3. Target

**Application (what we will build).** TicketTrap, a small help-desk web application with an embedded AI assistant
that reads support tickets and prepares reports. Architecture:

- **Frontend:** React + TypeScript + Vite (ticket views, agent-activity view, results), served locally on `127.0.0.1:5173`.
- **Backend:** Python + FastAPI + Pydantic (APIs, input validation, permission checks), served on `127.0.0.1:8000`.
- **Data:** SQLite (synthetic customer records and trial metadata).
- **Agent worker:** a custom Python agent loop that calls a hosted model through its official SDK and logs every tool call in full.
- **Collection endpoint:** a local HTTP endpoint that records any data exfiltrated by a successful attack, at `http://127.0.0.1:9100/collect`.

The agent is exposed **exactly three tools, and only these three, in every condition**: `read_ticket`,
`read_customer_record`, and `send_report`. Tool permissions (which record IDs are readable, which report
destinations are allowed) come from trusted per-task settings, never from ticket content.

**Agents under test.** Our own TicketTrap agent (the custom Python loop above), run under two pinned models
spanning two providers, so we can see whether results generalize across models rather than reflecting one
model's quirks:

- `gpt-4o-2024-08-06` (OpenAI)
- `claude-3-7-sonnet-20250219` (Anthropic)

We pin exact API model snapshots, never a floating alias such as "latest", and record the snapshot ID with
every trial.

**Configurations compared** (the same normal and malicious tickets run across all three):

1. **Baseline:** normal task instructions, broadly accessible tools.
2. **Prompt-only defense:** instructions telling the assistant to treat ticket content as untrusted.
3. **Application-enforced defense:** backend checks restrict record access and report destinations; the
   prompt-only instructions are retained so we measure the added effect of the checks.

**Attack cases.** Malicious tickets span several injection families: direct instruction override, forged
system/authority framing, urgency ("important message") framing, obfuscation (encoding or hiding instructions
among data), and exfiltration through tool arguments, with a held-out subset reserved for final evaluation so
that defenses are not tuned against attacks we have already seen.

---

## 4. Threat model

**Who is the attacker, and what access do they start with?** An outside party who can file or edit support
tickets in TicketTrap, the same capability any customer of a help-desk system has. They have no backend
account and no access to system prompts, tool code, permission settings, the database, or the model. Their only
foothold is the free-text body of one synthetic ticket.

**What do they control?** Exactly one thing: the body of a single synthetic ticket that the agent reads via
`read_ticket` while performing a legitimate assigned task. They do not control the task instructions, the
authorized record, the approved report destination, the tool definitions, or the permission settings, all of
which come from trusted task configuration.

**What are they trying to achieve? (Security property to be violated.)** Confidentiality. The attacker's goal is
to make the agent step outside its assigned task and disclose an unrelated private customer record, reading a
record it was not authorized to read and sending it to a destination it was not authorized to use. We count the
attack as **confirmed leakage** only when a trial-specific synthetic canary from the unauthorized record is
received at the unauthorized local collection endpoint. We separately record (a) unauthorized-access
*attempts*, (b) *successful* unauthorized reads, and (c) legitimate task completion, so that attempted,
achieved, and leaked are never conflated.

**What are we not claiming?** Results apply only to the TicketTrap application, the specific pinned model
versions, and the specific attack and benign cases we test. We do not claim that all agents are vulnerable, that
our attacks are exhaustive, or that a defense that succeeds here stops every possible prompt-injection attack.
This is a bounded comparison, not a general security guarantee.

---

## 5. Scope statement

**What we will touch, and what we will not.** We run only the TicketTrap stack we build: the FastAPI backend,
the SQLite database of synthetic records, the custom Python agent worker, the local collection endpoint, and the
React frontend, all on team-controlled machines. Test traffic is limited to these named local services plus the
one external dependency below. We will not test, attack, or send traffic to any third-party system, any real
help-desk product, or any data we do not own.

**Where it runs.** Localhost only. Every component runs on the four team members' personal development laptops;
nothing runs on shared, public, or WSU-managed infrastructure.

**Source code.** All code is kept in a single private GitHub repository: https://github.com/amanverma-wsu/ticket-trap.

**External dependency and API keys.** The one non-local dependency is the hosted model API, so model processing
is not entirely local. The team uses its own personal paid API accounts for the providers named above, not WSU
or any shared institutional account. API keys are stored only in local environment variables or a git-ignored
secrets file, and are never committed to the repository, written to logs, or placed in ticket content.

**Data and safety rules.** Synthetic data only, no real user data. Canary tokens are trial-specific synthetic
values. Test traffic is restricted to the named local endpoints. Records and agent state are reset between
trials.

---

## AI Use Appendix

- **ChatGPT (OpenAI).** Used to draft the initial proposed technology stack and experiment design that became
  the project overview. The team reviewed these suggestions, adopted the proposed stack, and refined the
  experimental scope.
- **Claude (Anthropic).** Used to restructure the project overview into this D1 format, to identify required
  details that were missing, to fill drafting defaults (for example the collection-endpoint address and
  configuration wording), and to suggest methodological framing (two pinned models across providers, named
  attack families, and a held-out evaluation set). All project decisions — team roster, track, target, models,
  and scope — were made by the team, and the team reviewed and edited all wording.
- No implementation or experimental results are claimed at D1.
