---
name: afb-pareto
description: Pareto-frontier analysis (Group A, all rows). Consumes the creator->cluster table from afb-clustering and traces the non-dominated frontier of Followers vs ENGAGE_RATE (creators for whom no one else has both more followers and higher performance). Saves the coloured scatter + frontier list. Reproduces the Pareto part of afb7.
---

# afb-pareto

Reproduces the Pareto frontier from `afb7`, reels-only. Runs **after** `afb-clustering`.

## What it does
A creator is on the frontier if no other creator has simultaneously more Followers AND
higher ENGAGE_RATE. Points are coloured by cluster (Macro/Mid-Size/Micro).

## Run
```
python .claude/skills/afb-pareto/pareto.py --input data/processed/creator_cluster.csv
```

## Output
- `outputs/plots/pareto_reels.png` — scatter + frontier.
- `outputs/models/pareto_frontier.csv` — the non-dominated creators.
