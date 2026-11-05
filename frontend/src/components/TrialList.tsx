import type { Trial } from "../types";
import Badges from "./Badges";

export default function TrialList({
  trials,
  selectedId,
  onSelect,
}: {
  trials: Trial[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="trial-list">
      {trials.map((t) => (
        <button
          key={t.id}
          className={`trial-row ${t.id === selectedId ? "active" : ""}`}
          onClick={() => onSelect(t.id)}
        >
          <div className="top">
            <span className="cid">{t.case_id}</span>
            <Badges trial={t} />
          </div>
          <div className="meta">
            {t.config} · {t.kind === "attack" ? t.attack_family : "benign"}
          </div>
        </button>
      ))}
      {trials.length === 0 && (
        <div style={{ padding: 16, color: "var(--muted)", fontSize: "0.85rem" }}>
          No trials match these filters.
        </div>
      )}
    </div>
  );
}
