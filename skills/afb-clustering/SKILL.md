---
name: afb-clustering
description: Creator-level KMeans clustering (Group A, all rows). Aggregates posts to one row per creator (median Views, Followers, ENGAGE_RATE), log-transforms size, standardizes, fits KMeans k=3, and labels clusters by follower size (largest=Macro, middle=Mid-Size, smallest=Micro). Exports creator->cluster for the regression-by-cluster step. Reproduces the clustering of afb7 (reels).
---

# afb-clustering

Reproduces the clustering from `afb7-clustering`, reels-only.

## Fixed rules (from config)
- **k = 3** (no elbow/silhouette human choice; fixed).
- Features: `Views_log`, `Followers_log`, `ENGAGE_RATE` (creator medians).
- **Cluster naming is by follower size**, not by KMeans label number: the three centroids
  are sorted on median Followers → largest = **Macro**, middle = **Mid-Size**, smallest = **Micro**.

## Run
```
python .claude/skills/afb-clustering/cluster.py --input data/processed/master.csv
```

## Output
`data/processed/creator_cluster.csv` — one row per creator: medians (Followers, Views,
ENGAGE_RATE), `cluster`, `cluster_name`. Consumed by `afb-pareto` and `afb-regression`.
