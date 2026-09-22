---
name: afb-moran
description: Moran's I temporal-autocorrelation analysis (Group A, all rows). For the top creator(s) by post count, standardizes their Views series, builds a K-neighbour temporal lag, computes Moran's I (slope of the Moran scatterplot) and saves the quadrant-coloured scatterplot. Reproduces the Moran part of afb6.
---

# afb-moran

Reproduces the Moran's I analysis from `afb6`, generalized for autonomy.

## When to use
After merge, alongside `afb-markov`, in the Group-A analyses.

## Fixed rules (from config)
- Creator selection: **top 5 creators by post count with at least 25 posts**
  (`moran_top_creators`=5, `min_posts_per_creator`=25); fewer if not enough qualify;
  skip entirely if none do.
- Neighbours: **K = `moran_k`** (default 3) before and after each post.
- Metric: **Views**, standardized (z-score) per creator.

## Run
```
python .claude/skills/afb-moran/moran.py --input data/processed/master.csv
```

## Output
- `outputs/models/moran.csv` — Moran's I per creator.
- `outputs/plots/moran_<creator>.png` — quadrant-coloured Moran scatterplot per creator.
