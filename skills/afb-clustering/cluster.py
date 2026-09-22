#!/usr/bin/env python
"""afb-clustering — creator-level KMeans (k=3), labelled by follower size.

Faithful to afb7 (reels clustering). Cluster names are assigned deterministically by
sorting centroids on median Followers (largest=Macro, middle=Mid-Size, smallest=Micro).
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
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402

log = get_logger("afb-clustering")
C = CONFIG["columns"]
VIEWS = C["reach_proxy"]
GROUP = C["group_var"]
K = CONFIG["constants"]["kmeans_k"]
RS = CONFIG["constants"]["random_state"]
NAMES_BY_RANK = ["Micro", "Mid-Size", "Macro"]  # ascending follower size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "master.csv"))
    ap.add_argument("--output", default=str(path("processed_dir") / "creator_cluster.csv"))
    args = ap.parse_args()

    df = load_dataset(args.input)
    agg = (df.groupby(GROUP)
             .agg(n_posts=(VIEWS, "size"),
                  Followers=("Followers", "median"),
                  Views=(VIEWS, "median"),
                  ENGAGE_RATE=("ENGAGE_RATE", "median"))
             .reset_index().dropna())
    log.info(f"{len(agg)} creators after aggregation")

    feats = pd.DataFrame({
        "Views_log": np.log1p(agg["Views"]),
        "Followers_log": np.log1p(agg["Followers"]),
        "ENGAGE_RATE": agg["ENGAGE_RATE"],
    })
    X = StandardScaler().fit_transform(feats)
    labels = KMeans(n_clusters=K, random_state=RS, n_init=30).fit_predict(X)
    agg["cluster"] = labels

    # deterministic naming by median followers per cluster
    order = agg.groupby("cluster")["Followers"].median().sort_values().index.tolist()
    name_map = {cl: NAMES_BY_RANK[rank] for rank, cl in enumerate(order)}
    agg["cluster_name"] = agg["cluster"].map(name_map)

    for name in NAMES_BY_RANK:
        sub = agg[agg["cluster_name"] == name]
        if len(sub):
            log.info(f"{name:9} n={len(sub):3}  med.Followers={sub['Followers'].median():,.0f}  "
                     f"med.ENGAGE_RATE={sub['ENGAGE_RATE'].median():.4f}")

    save_csv(agg, args.output)
    log.info(f"saved -> {args.output}")


if __name__ == "__main__":
    main()
