import type { Trial, ToolCall } from "../types";
import Badges from "./Badges";

function containsCanary(obj: unknown, canary: string | null): boolean {
  if (!canary) return false;
  try {
    return JSON.stringify(obj).includes(canary);
  } catch {
    return false;
  }
}

function argsLine(a: Record<string, unknown>) {
  return Object.entries(a)
    .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
    .join(", ");
}

function ToolRow({ call, canary }: { call: ToolCall; canary: string | null }) {
  const flagged = containsCanary(call.result, canary) || containsCanary(call.arguments, canary);
  const ok = (call.result as { ok?: boolean })?.ok;
  return (
    <div className={`tool ${flagged ? "flagged" : ""}`}>
      <div className="call">
        <span className="fn">{call.name}</span>
        <span className="args">({argsLine(call.arguments)})</span>
      </div>
      <div className="res">
        {ok === false ? "blocked / not ok" : "ok"}
        {flagged && <span className="canary-hit"> — secret canary present</span>}
      </div>
    </div>
  );
}

export default function Transcript({ trial }: { trial: Trial }) {
  return (
    <div className="detail">
      <h3>{trial.case_id}</h3>
      <div className="detail-meta">
        {trial.config} · {trial.model} · repeat {trial.repeat}
        {trial.attack_family ? ` · ${trial.attack_family}` : " · benign"}
      </div>
      <div style={{ marginBottom: 14 }}>
        <Badges trial={trial} />
      </div>

      <div className="ticket">
        <span className="k">Ticket body (attacker-controlled for attacks)</span>
        {trial.ticket_body || "(none)"}
      </div>

      {trial.transcript.map((s) => (
        <div className="step" key={s.step}>
          <div className="step-head">step {s.step}</div>
          {s.text ? <div className="say">{s.text}</div> : null}
          {s.tool_calls.map((c, i) => (
            <ToolRow key={i} call={c} canary={trial.canary} />
          ))}
        </div>
      ))}
    </div>
  );
}
