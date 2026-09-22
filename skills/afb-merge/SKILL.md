---
name: afb-merge
description: Joins the LLM extraction outputs (caption, video, hook) onto the engineered data, computes caption_length, drops failed-extraction (ERROR) rows, and emits the two analysis views — master.csv (View A, all rows) and master_video.csv (View B, rows that have video features). Run after feature-engineering and the extraction skills.
---

# afb-merge

Reproduces notebook `afb5-dataset-merging`, reels-only and Excel-free.

## When to use
After `afb-feature-engineering` and (ideally) the three extraction skills. It runs even
if extraction outputs are missing — it just produces View A with no video features and an
empty View B (useful for testing the non-Gemini path).

## What it does
1. Loads `engineered.csv`, computes `caption_length` (word count of `Post caption`).
2. Left-joins on `Filename` whichever extraction outputs exist in `data/processed/`:
   `extracted_caption.csv`, `extracted_video.csv`, `extracted_hook.csv`.
3. Drops rows whose video features are `ERROR:` (failed Gemini calls).
4. Writes:
   - **`master.csv`** — View A (all rows; video columns NaN where no video).
   - **`master_video.csv`** — View B (rows that have video features).

## Run
```
python .claude/skills/afb-merge/merge.py
```

## Output
`data/processed/master.csv` and `data/processed/master_video.csv`.
