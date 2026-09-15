"""Trial harness: for each (case x config x model), repeat N times with fresh state.

Records: model id, config, prompts, tool requests, outcomes, commit hash, deps.
Outcomes tracked separately: access ATTEMPT, successful READ, confirmed LEAK, task DONE.
"""
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="all", choices=["all", "baseline", "prompt_only", "app_enforced"])
    ap.add_argument("--repeats", type=int, default=20)
    ap.add_argument("--held-out", action="store_true", help="run the reserved evaluation set")
    args = ap.parse_args()

    # TODO:
    #  - load cases from cases/ (benign + attacks; held-out kept separate)
    #  - for each case x config x model x repeat:
    #       reset_and_seed() with a fresh canary
    #       set backend task permissions (trusted)
    #       run_agent(...)
    #       classify outcome: attempt / read / leak / task-complete
    #       append a row to data/results.csv
    print(f"Would run config={args.config} repeats={args.repeats} held_out={args.held_out}")


if __name__ == "__main__":
    main()
