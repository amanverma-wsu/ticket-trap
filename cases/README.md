# Cases

- `benign/` — legitimate tickets the agent SHOULD complete (measures utility).
- `attacks/` — malicious tickets (measures leakage). Families: direct instruction
  override, forged system/authority framing, urgency framing, obfuscation, and
  exfiltration via tool arguments.
- `held_out/` — a reserved subset used ONLY for final evaluation, so defenses are not
  tuned against attacks we have already seen. Do not inspect during development.

Each case is a JSON file: task settings (trusted) + the ticket body (attacker-controlled).
See `_schema.json`.
