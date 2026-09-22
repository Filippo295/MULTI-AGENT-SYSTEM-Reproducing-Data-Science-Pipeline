#!/usr/bin/env python
"""afb-pareto — Pareto frontier of Followers vs ENGAGE_RATE per creator.

Faithful to afb7 (Pareto part). Consumes creator_cluster.csv from afb-clustering.
"""
import argparse
import sys
from pathlib import Path

_p = Path(__file__).resolve()
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
from afb_common import CONFIG, path, save_csv, get_logger  # noqa: E402

import pandas as pd  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

log = get_logger("afb-pareto")
GROUP = CONFIG["columns"]["group_var"]
COLORS = {"Macro": "#4C72B0", "Mid-Size": "#55A868", "Micro": "#DD8452"}


def frontier(df, x="Followers", y="ENGAGE_RATE"):
    d = df.sort_values(x, ascending=False).reset_index(drop=True)
    best, on = -float("inf"), []
    for _, r in d.iterrows():
        if r[y] >= best:
            on.append(True); best = r[y]
        else:
            on.append(False)
    d["on_frontier"] = on
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "creator_cluster.csv"))
    ap.add_argument("--plot", default=str(path("plots_dir") / "pareto_reels.png"))
    ap.add_argument("--output", default=str(path("models_dir") / "pareto_frontier.csv"))
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    d = frontier(df)
    front = d[d["on_frontier"]].sort_values("Followers")
    log.info(f"{len(front)} creators on the Pareto frontier")

    path("plots_dir").mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, grp in d.groupby("cluster_name"):
        ax.scatter(grp["Followers"], grp["ENGAGE_RATE"], s=50, alpha=0.7,
                   label=name, c=COLORS.get(name, "#888"))
    ax.plot(front["Followers"], front["ENGAGE_RATE"], "--", color="crimson", lw=1.5, label="Frontier")
    ax.scatter(front["Followers"], front["ENGAGE_RATE"], marker="D", s=80, color="crimson", zorder=4)
    ax.set_xscale("log"); ax.set_xlabel("Followers (log)"); ax.set_ylabel("ENGAGE_RATE")
    ax.set_title("Pareto Frontier — Reels", fontweight="bold"); ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(args.plot, dpi=110); plt.close(fig)

    save_csv(front[[GROUP, "Followers", "ENGAGE_RATE", "cluster_name"]], args.output)
    log.info(f"saved -> {args.output} and plot -> {args.plot}")


if __name__ == "__main__":
    main()
