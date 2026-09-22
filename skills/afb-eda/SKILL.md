---
name: afb-eda
description: Exploratory data analysis (descriptive). For every meaningful variable present, computes its distribution and its relationship with the target (ENGAGE_RATE) — numeric correlations + histograms, categorical median-by-group + boxplots. Schema-adaptive (skips absent variables). Reproduces afb3 (reels), on View A.
---

# afb-eda

Reproduces the exploratory analysis of `afb3-eda-reels`, adapted/schema-adaptive.

## When to use
After merge, on `master.csv` (View A). Video-extracted variables are plotted on their
available (video) rows.

## What it does
- **Numeric** (Followers, Views, Likes, Comments, Shares, Saves, media_duration_sec, caption_length):
  histogram grid + Pearson correlation with ENGAGE_RATE.
- **Categorical** (Type of content, mese, fascia_oraria, Weekend, + present LLM categoricals):
  count + median ENGAGE_RATE per category, with a boxplot each.

## Run
```
python .claude/skills/afb-eda/eda.py --input data/processed/master.csv
```

## Output
- `outputs/models/eda_numeric_corr.csv`, `eda_categorical_medians.csv`
- `outputs/plots/eda/hist_numeric.png`, `corr_bar.png`, `box_<var>.png`
