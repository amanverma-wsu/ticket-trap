# Cases

Each `.json` file is one trial scenario (see `_schema.json`): trusted task settings plus
the attacker-controlled `ticket_body`.

- `benign/` — legitimate tickets the agent SHOULD complete (measures utility).
- `attacks/` — malicious tickets (measures leakage). The files here are trivial,
  illustrative payloads to exercise the harness.
- `held_out/` — reserved for final evaluation only. Not loaded by default. Do NOT iterate
  defenses against these.

TODO(team): author the real synthetic attack set across the families
(direct_override, authority_framing, urgency, obfuscation, tool_arg_exfil), and expand
the benign set. Keep attacks synthetic and local-only.
