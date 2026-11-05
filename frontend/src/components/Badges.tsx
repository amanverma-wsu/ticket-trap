import type { Trial } from "../types";

type Tone = "leak" | "read" | "ok";

function Badge({ label, on, tone }: { label: string; on: boolean; tone: Tone }) {
  return <span className={`badge ${on ? `on-${tone}` : "off"}`}>{label}</span>;
}

export default function Badges({ trial }: { trial: Trial }) {
  return (
    <div className="badges">
      <Badge label="attempt" on={trial.access_attempt} tone="read" />
      <Badge label="read" on={trial.successful_read} tone="read" />
      <Badge label="leak" on={trial.confirmed_leak} tone="leak" />
      <Badge label="task done" on={trial.task_complete} tone="ok" />
    </div>
  );
}
