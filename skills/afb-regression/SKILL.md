---
name: afb-regression
description: Regression (Group B, video rows). Models log(ENGAGE_RATE) with Lasso feature selection (alpha=0.05) then OLS with an AR(1) lag (previous post's target per creator) and creator-clustered standard errors. Runs the total regression plus one per cluster for the TWO clusters with the most posts (Macro/Mid-Size/Micro selected by post count, not name). Reproduces afb9.
---

# afb-regression

Reproduces notebook `afb9-regression`, reels-only and schema-adaptive.

## When to use
After merge + clustering, on `master_video.csv` (View B) using `creator_cluster.csv`.

## Fixed rules (from config)
- Target: `log(ENGAGE_RATE*100 + 0.001)`.
- Feature pool: `Followers` (raw), media_duration_sec, caption_length, Shares, Saves, the
  ordinal maps, the binaries, and one-hot of present nominal/LLM categoricals. `Views`
  excluded (it's the target denominator); `Likes`/`Comments` excluded (they build the target).
- **Lasso alpha = 0.05** for selection, then **OLS + AR(1) lag + creator-clustered SE**.
- Per-cluster regressions on the **two clusters with the most posts** (by video-row count),
  plus the total — so the pair adapts to the data (Macro+Mid-Size, Macro+Micro, etc.).

## Run
```
python .claude/skills/afb-regression/regress.py --input data/processed/master_video.csv --clusters data/processed/creator_cluster.csv
```

## Output
`outputs/models/regression_<scope>.csv` (scope = total / <ClusterName> / <ClusterName>) — each
with coefficient, std error, p-value per retained feature, plus R² and n in the log.
