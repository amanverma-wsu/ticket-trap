import type { Bundle, ConfigSummary } from "../types";

function pct(x: number) {
  return `${Math.round(x * 100)}%`;
}

function Metric({ name, value, tone }: { name: string; value: number; tone: "leak" | "read" | "ok" }) {
  return (
    <div className="metric">
      <div className="label">
        <span className="name">{name}</span>
        <span className="val">{pct(value)}</span>
      </div>
      <div className={`bar ${tone}`}>
        <span style={{ width: pct(value) }} />
      </div>
    </div>
  );
}

function ConfigCard({ c, desc }: { c: ConfigSummary; desc: string }) {
  return (
    <div className="config-card">
      <h3>{c.config}</h3>
      <p className="desc">{desc}</p>
      <Metric name={`Unauthorized read (n=${c.n_attacks})`} value={c.read_rate} tone="read" />
      <Metric name="Confirmed leak" value={c.leak_rate} tone="leak" />
      <Metric name={`Benign task completion (n=${c.utility_n})`} value={c.utility_rate} tone="ok" />
    </div>
  );
}

export default function Dashboard({ bundle }: { bundle: Bundle }) {
  const order = ["baseline", "prompt_only", "app_enforced"];
  const rows = [...bundle.summary.by_config].sort(
    (a, b) => order.indexOf(a.config) - order.indexOf(b.config)
  );
  return (
    <section>
      <h2 className="section">Security vs. utility by configuration</h2>
      <p className="sub">
        Lower read and leak rates are safer; higher benign completion means the defense did not
        break legitimate work. Rates are over the attack cases (read, leak) and benign cases (completion).
      </p>
      <div className="config-grid">
        {rows.map((c) => (
          <ConfigCard key={c.config} c={c} desc={bundle.config_descriptions[c.config] ?? ""} />
        ))}
      </div>
      <div className="legend">
        <span><span className="dot" style={{ background: "var(--read)" }} />unauthorized read of a record the agent was not assigned</span>
        <span><span className="dot" style={{ background: "var(--leak)" }} />confirmed leak: a canary reached the collector</span>
        <span><span className="dot" style={{ background: "var(--ok)" }} />benign ticket handled correctly</span>
      </div>
    </section>
  );
}
