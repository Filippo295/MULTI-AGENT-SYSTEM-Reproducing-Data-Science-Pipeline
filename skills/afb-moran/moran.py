#!/usr/bin/env python
"""afb-moran — Moran's I (temporal autocorrelation of Views) for top creator(s).

Faithful to afb6 (Moran part); creator selection generalized to "most posts".
"""
import argparse
import re
import sys
from pathlib import Path

_p = Path(__file__).resolve()
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
from afb_common import CONFIG, path, load_dataset, save_csv, get_logger  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

log = get_logger("afb-moran")
C = CONFIG["columns"]
VALUE = C["reach_proxy"]
GROUP = C["group_var"]
K = CONFIG["constants"]["moran_k"]
N_CREATORS = CONFIG["constants"]["moran_top_creators"]
MIN_POSTS = CONFIG["constants"]["min_posts_per_creator"]
QCOL = {"HH": "#e63946", "LL": "#457b9d", "HL": "#f4a261", "LH": "#2a9d8f"}


def moran(reach_series):
    z = ((reach_series - reach_series.mean()) / reach_series.std()).values
    n = len(z)
    idx = range(K, n - K)
    z_i = np.array([z[i] for i in idx])
    z_lag = np.array([np.concatenate([z[i - K:i], z[i + 1:i + K + 1]]).mean() for i in idx])
    slope, intercept = np.polyfit(z_i, z_lag, 1)
    quad = np.array(["HH" if a >= 0 and b >= 0 else "LL" if a < 0 and b < 0
                     else "HL" if a >= 0 else "LH" for a, b in zip(z_i, z_lag)])
    return slope, intercept, z_i, z_lag, quad


def plot(creator, slope, intercept, z_i, z_lag, quad, out_png):
    fig, ax = plt.subplots(figsize=(6, 5))
    for q, col in QCOL.items():
        m = quad == q
        ax.scatter(z_i[m], z_lag[m], c=col, alpha=0.75, s=55, label=q,
                   edgecolors="white", linewidths=0.5, zorder=3)
    xs = np.linspace(z_i.min() - 0.2, z_i.max() + 0.2, 100)
    ax.plot(xs, slope * xs + intercept, color="black", lw=1.5, zorder=4)
    ax.axhline(0, color="gray", lw=0.8, ls="--"); ax.axvline(0, color="gray", lw=0.8, ls="--")
    ax.set_xlabel("Views standardized (z)"); ax.set_ylabel(f"Neighbour mean (lag, K={K})")
    ax.set_title(f"{creator} — Moran's I = {slope:.3f}", fontweight="bold")
    ax.legend(fontsize=8, title="Quadrant")
    fig.tight_layout(); fig.savefig(out_png, dpi=110); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "master.csv"))
    ap.add_argument("--output", default=str(path("models_dir") / "moran.csv"))
    args = ap.parse_args()

    df = load_dataset(args.input)
    counts = df[GROUP].value_counts()
    eligible = counts[counts >= MIN_POSTS]
    top = eligible.head(N_CREATORS).index.tolist()
    if not top:
        log.warning(f"no creator has >= {MIN_POSTS} posts; cannot run Moran's I")
        save_csv(pd.DataFrame(columns=["creator", "n_posts", "moran_I"]), args.output)
        return
    log.info(f"selected {len(top)} creator(s) with >= {MIN_POSTS} posts: {top}")
    plots = path("plots_dir"); plots.mkdir(parents=True, exist_ok=True)

    out = []
    for creator in top:
        sub = (df[df[GROUP] == creator]
               .assign(datetime=lambda d: pd.to_datetime(
                   d[C["date"]].astype(str) + " " + d[C["time"]].astype(str), errors="coerce"))
               .sort_values("datetime").reset_index(drop=True))
        if len(sub) < 2 * K + 1:
            log.info(f"skip {creator}: only {len(sub)} posts (<{2*K+1})")
            continue
        slope, intercept, z_i, z_lag, quad = moran(sub[VALUE])
        safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(creator))[:40]
        png = plots / f"moran_{safe}.png"
        plot(creator, slope, intercept, z_i, z_lag, quad, png)
        out.append({"creator": creator, "n_posts": len(sub), "moran_I": slope})
        log.info(f"{creator}: n={len(sub)}  Moran's I={slope:.3f}  -> {png.name}")

    save_csv(pd.DataFrame(out), args.output)
    log.info(f"saved -> {args.output}")


if __name__ == "__main__":
    main()
