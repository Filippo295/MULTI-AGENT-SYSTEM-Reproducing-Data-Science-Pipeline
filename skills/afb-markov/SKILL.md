---
name: afb-markov
description: Markov-chain analysis (Group A, all rows). For the top creator(s) by post count, sorts their posts chronologically, defines state 0/1 as Views below/above that creator's mean, and computes the 2x2 transition matrix (the "fame/hot-streak" effect). Reproduces the Markov part of afb6.
---

# afb-markov

Reproduces the Markov chain from `afb6-markov-chain`, generalized for autonomy.

## When to use
After merge, as part of the Group-A (no-video) analyses.

## Fixed rules (from config)
- Creator selection: **top 5 creators by post count with at least 25 posts**
  (`markov_top_creators`=5, `min_posts_per_creator`=25); fewer if not enough qualify;
  skip entirely if none do. Replaces the hand-picked "BENNET" — no hardcoded names.
- Success metric: **Views** (in place of Reach), absolute (single-creator series).
- States: 0 = Views below creator mean, 1 = at/above.

## Run
```
python .claude/skills/afb-markov/markov.py --input data/processed/master.csv
```

## Output
`outputs/models/markov.csv` — one row per analyzed creator with n_posts and the four
transition probabilities (p00, p01, p10, p11).
