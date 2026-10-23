"""Turn a results.csv into summary rates and figures.

The headline figure is the security-utility tradeoff: for each configuration, the attack
leak rate (lower is better) against the benign task-completion rate (higher is better).
Aggregation is separated from plotting so the numbers are unit-tested and the plots get a
smoke test.

Expected results.csv columns: model, config, case_id, kind, attack_family, repeat,
access_attempt, successful_read, confirmed_leak, task_complete.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def load_results(path) -> pd.DataFrame:
    return pd.read_csv(path)


def summarize(df: pd.DataFrame) -> dict:
    attacks = df[df["kind"] == "attack"]
    benign = df[df["kind"] == "benign"]
    return {
        "leak_by_config": attacks.groupby("config")["confirmed_leak"]
        .agg(mean="mean", n="count", std="std").reset_index(),
        "rates_by_config": attacks.groupby("config")[
            ["access_attempt", "successful_read", "confirmed_leak"]
        ].mean().reset_index(),
        "utility_by_config": benign.groupby("config")["task_complete"]
        .agg(mean="mean", n="count").reset_index(),
        "leak_by_config_model": attacks.groupby(["config", "model"])["confirmed_leak"]
        .mean().reset_index(),
        "leak_by_family": attacks.groupby(["config", "attack_family"])["confirmed_leak"]
        .mean().reset_index(),
    }


def tradeoff_points(df: pd.DataFrame) -> pd.DataFrame:
    leak = df[df["kind"] == "attack"].groupby("config")["confirmed_leak"].mean()
    completion = df[df["kind"] == "benign"].groupby("config")["task_complete"].mean()
    return pd.DataFrame(
        {"attack_leak_rate": leak, "benign_completion": completion}
    ).reset_index()


def plot_tradeoff(df: pd.DataFrame, path: Path) -> Path:
    pts = tradeoff_points(df)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(pts["attack_leak_rate"], pts["benign_completion"], s=80)
    for _, r in pts.iterrows():
        ax.annotate(r["config"], (r["attack_leak_rate"], r["benign_completion"]),
                    xytext=(5, 5), textcoords="offset points")
    ax.set_xlabel("Attack leak rate (lower is better)")
    ax.set_ylabel("Benign task completion (higher is better)")
    ax.set_title("Security-utility tradeoff by configuration")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_leak_by_config(df: pd.DataFrame, path: Path) -> Path:
    leak = df[df["kind"] == "attack"].groupby("config")["confirmed_leak"].mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    leak.plot(kind="bar", ax=ax)
    ax.set_ylabel("Confirmed leak rate")
    ax.set_ylim(0, 1)
    ax.set_title("Confirmed leak rate by configuration")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def make_figures(df: pd.DataFrame, outdir) -> list:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    return [
        plot_tradeoff(df, outdir / "tradeoff.png"),
        plot_leak_by_config(df, outdir / "leak_by_config.png"),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="data/results.csv")
    ap.add_argument("--figures", default="data/figures")
    args = ap.parse_args()
    df = load_results(args.results)
    summary = summarize(df)
    for name, table in summary.items():
        print(f"== {name} ==")
        print(table.to_string(index=False))
        print()
    paths = make_figures(df, args.figures)
    print("figures:", ", ".join(str(p) for p in paths))


if __name__ == "__main__":
    main()
