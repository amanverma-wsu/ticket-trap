"""Turn data/results.csv into rates and figures.

Key outputs:
  - leak rate by (config x model x attack family), with variance across repeats
  - the security-utility tradeoff: attack success vs. benign task completion per config
"""
from pathlib import Path

FIGDIR = Path(__file__).resolve().parents[1] / "data" / "figures"


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    # TODO: load results.csv with pandas, aggregate, and plot with matplotlib.
    print("Figures ->", FIGDIR)


if __name__ == "__main__":
    main()
