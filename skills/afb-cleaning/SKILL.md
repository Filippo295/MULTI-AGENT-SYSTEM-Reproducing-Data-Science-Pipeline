---
name: afb-cleaning
description: First pipeline step. Cleans the raw AFB dataset — loads with Filename as string (prevents 19-digit ID corruption), coerces numerics, imputes missing Likes via the project's comment-percentile mapping, guards Views=0, and reports data quality. Use before feature-engineering on any new dataset.
---

# afb-cleaning

Reproduces notebook `afb1-cleaning`, adapted to the reels-only new dataset.

## When to use
The very first step of the pipeline, on the raw input CSV.

## What it does
1. Loads the CSV with the key column (`Filename`) forced to **string** — the TikTok
   IDs are 19 digits and would lose their last digits if parsed as a number.
2. Coerces numeric columns (`Followers`, `Views`, `Likes`, `Comments`, `Shares`,
   `Saves`, `media_duration_sec`).
3. Imputes missing `Likes` with the project's method: map the row's comment-percentile
   onto the like-percentile of the rows that have Likes.
4. Guards `Views == 0` (defensive — none observed, but would break ratio targets).
5. Reports columns absent vs UNITING (expected — CV metrics, brand, gender — not recreated),
   remaining missing values, and duplicate Filenames (collaborations are kept).

## Run
```
python .claude/skills/afb-cleaning/clean.py --input data/raw/new_dataset.csv --output data/processed/cleaned.csv
```
Defaults come from `afb_config.json`, so plain `python .../clean.py` also works.

## Output
`data/processed/cleaned.csv` — same rows, cleaned, ready for feature-engineering.
