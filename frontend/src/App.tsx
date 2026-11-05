import { useEffect, useMemo, useState } from "react";
import type { Bundle, Trial } from "./types";
import Dashboard from "./components/Dashboard";
import TrialList from "./components/TrialList";
import Transcript from "./components/Transcript";

const ALL = "all";

export default function App() {
  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [kind, setKind] = useState(ALL);
  const [config, setConfig] = useState(ALL);
  const [family, setFamily] = useState(ALL);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    fetch("results.json")
      .then((r) => {
        if (!r.ok) throw new Error(`results.json ${r.status}`);
        return r.json();
      })
      .then((b: Bundle) => setBundle(b))
      .catch((e) => setError(String(e)));
  }, []);

  const families = useMemo(() => {
    if (!bundle) return [];
    return Array.from(
      new Set(bundle.trials.map((t) => t.attack_family).filter(Boolean) as string[])
    ).sort();
  }, [bundle]);

  const filtered: Trial[] = useMemo(() => {
    if (!bundle) return [];
    return bundle.trials.filter(
      (t) =>
        (kind === ALL || t.kind === kind) &&
        (config === ALL || t.config === config) &&
        (family === ALL || t.attack_family === family)
    );
  }, [bundle, kind, config, family]);

  const selected = filtered.find((t) => t.id === selectedId) ?? null;

  if (error) {
    return (
      <div className="app">
        <div className="error">
          Could not load results.json ({error}). Run the exporter, or check it is in
          frontend/public/.
        </div>
      </div>
    );
  }
  if (!bundle) return <div className="app"><div className="loading">Loading…</div></div>;

  return (
    <div className="app">
      <header className="masthead">
        <h1>TicketTrap</h1>
        <p>
          A help-desk agent reads support tickets. A prompt injection hidden in a ticket tries to
          make it leak a customer record it was never assigned. This dashboard shows what each
          defense stops.
        </p>
        <span className={`sample-flag ${bundle.is_sample ? "" : "real"}`}>
          {bundle.is_sample ? "sample data" : "live data"} · {bundle.source} · {bundle.trials.length} trials
        </span>
      </header>

      <Dashboard bundle={bundle} />

      <h2 className="section">Trial explorer</h2>
      <p className="sub">Pick a trial to read the agent's full transcript and see where the defense acted.</p>

      <div className="filters">
        <select value={kind} onChange={(e) => { setKind(e.target.value); setSelectedId(null); }}>
          <option value={ALL}>all kinds</option>
          <option value="attack">attacks</option>
          <option value="benign">benign</option>
        </select>
        <select value={config} onChange={(e) => { setConfig(e.target.value); setSelectedId(null); }}>
          <option value={ALL}>all configs</option>
          {bundle.configs.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <select value={family} onChange={(e) => { setFamily(e.target.value); setSelectedId(null); }}>
          <option value={ALL}>all families</option>
          {families.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
      </div>

      <div className="explorer">
        <TrialList trials={filtered} selectedId={selectedId} onSelect={setSelectedId} />
        {selected ? (
          <Transcript trial={selected} />
        ) : (
          <div className="detail"><div className="empty">Select a trial on the left.</div></div>
        )}
      </div>

      <footer className="foot">
        Synthetic data and canary tokens only. Generated {bundle.generated_at}. CptS 428/528, Track A.
      </footer>
    </div>
  );
}
