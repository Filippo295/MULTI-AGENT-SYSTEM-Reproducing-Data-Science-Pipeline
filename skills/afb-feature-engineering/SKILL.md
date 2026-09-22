---
name: afb-feature-engineering
description: Second pipeline step. Builds the temporal features (mese, fascia_oraria, Weekend/Settimanale) and the reel targets (ENGAGE_RATE, COMM_PER_LIKE, PERC_REACHED) using Views in place of Reach. Schema-adaptive — skips CV-derived features (faccia/cognitive_overload/flashiness) when their inputs are absent. Use after afb-cleaning.
---

# afb-feature-engineering

Reproduces notebook `afb2-feature-engineering`, adapted to the reels-only new dataset.

## When to use
Right after `afb-cleaning`, on `data/processed/cleaned.csv`.

## What it does
- **Temporal features**: `fascia_oraria` (hour buckets: notte/mattina/pranzo/pomeriggio/cena/sera),
  `mese` (Italian month name), `Weekend/Settimanale` (Fri–Sun = weekend).
- **Targets (Views used in place of Reach)**:
  - `PERC_REACHED = Views / Followers`
  - `ENGAGE_RATE = (alpha*Likes + beta*Comments) / Views`  (alpha=1, beta=20 from config)
  - `COMM_PER_LIKE = Comments / Likes`
- **Skipped** (inputs absent in the new dataset, by design): `faccia`, `cognitive_overload`,
  `flashiness` — these needed the CV metrics, which are not recreated.

All rows are reels/tiktok, so every row gets the reel targets (no stories track).

## Run
```
python .claude/skills/afb-feature-engineering/engineer.py --input data/processed/cleaned.csv --output data/processed/engineered.csv
```

## Output
`data/processed/engineered.csv` — cleaned data + temporal features + the three targets.
