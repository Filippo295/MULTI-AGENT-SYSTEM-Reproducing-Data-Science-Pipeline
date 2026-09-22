#!/usr/bin/env python
"""afb-markov — transition matrix on Views states for the top creator(s) by post count.

Faithful to afb6 (Markov part); creator selection generalized to "most posts".
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
from afb_common import CONFIG, path, load_dataset, save_csv, get_logger  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

log = get_logger("afb-markov")
C = CONFIG["columns"]
VALUE = C["reach_proxy"]      # Views
GROUP = C["group_var"]        # Creator name
N_CREATORS = CONFIG["constants"]["markov_top_creators"]
MIN_POSTS = CONFIG["constants"]["min_posts_per_creator"]


def transition_matrix(sub):
    sub = sub.assign(
        datetime=pd.to_datetime(sub[C["date"]].astype(str) + " " + sub[C["time"]].astype(str),
                                errors="coerce")
    ).sort_values("datetime").reset_index(drop=True)
    mean = sub[VALUE].mean()
    state = (sub[VALUE] >= mean).astype(int).tolist()
    counts = np.zeros((2, 2), dtype=int)
    for a, b in zip(state[:-1], state[1:]):
        counts[a][b] += 1
    rows = counts.sum(axis=1, keepdims=True)
    probs = np.divide(counts, rows, out=np.zeros_like(counts, float), where=rows != 0)
    return probs, len(sub)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "master.csv"))
    ap.add_argument("--output", default=str(path("models_dir") / "markov.csv"))
    args = ap.parse_args()

    df = load_dataset(args.input)
    counts = df[GROUP].value_counts()
    eligible = counts[counts >= MIN_POSTS]
    top = eligible.head(N_CREATORS).index.tolist()
    if not top:
        log.warning(f"no creator has >= {MIN_POSTS} posts; cannot run Markov chain")
        save_csv(pd.DataFrame(columns=["creator", "n_posts", "p00", "p01", "p10", "p11"]), args.output)
        return
    log.info(f"selected {len(top)} creator(s) with >= {MIN_POSTS} posts: {top}")

    out = []
    for creator in top:
        sub = df[df[GROUP] == creator]
        probs, n = transition_matrix(sub)
        out.append({"creator": creator, "n_posts": n,
                    "p00": probs[0, 0], "p01": probs[0, 1],
                    "p10": probs[1, 0], "p11": probs[1, 1]})
        log.info(f"{creator}: n={n}  stay-low={probs[0,0]:.3f}  stay-high={probs[1,1]:.3f}")

    save_csv(pd.DataFrame(out), args.output)
    log.info(f"saved -> {args.output}")


if __name__ == "__main__":
    main()
