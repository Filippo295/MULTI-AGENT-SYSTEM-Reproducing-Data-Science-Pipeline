---
name: afb-classification
description: Classification (Group B, video rows). Splits reels into Silent vs Conversational at the 75th percentile of COMM_PER_LIKE, runs a Random Forest + SHAP to rank features, and evaluates NB/SVM/KNN/LR/XGB across top-k feature subsets on f1_macro, f1_weighted, accuracy and train→test gap — emitting the full candidate table. It does NOT pick a winner; the statistical-modeler agent chooses the single best model by judgment. Reproduces afb8.
---

# afb-classification

Reproduces notebook `afb8-classification`, schema-adaptive, with model selection delegated to the agent.

## When to use
After merge, on `master_video.csv` (View B — rows with video features).

## Fixed rules (from config)
- Target cut = **75th percentile** of `COMM_PER_LIKE` → 0 = Silent, 1 = Conversational.
- Feature pool: log(Followers), log(Views), media_duration_sec, caption_length, Shares, Saves, ordinal
  maps (voice_speed/hook/posizionamento), binaries (Type of content, Weekend), one-hot of present
  nominal/LLM categoricals. Absent columns are skipped. `Likes`/`Comments` excluded (they build the target).
- RF + RandomizedSearchCV → SHAP ranking → evaluate **NB / SVM / KNN / LR / XGB** over
  top-5/10/15/20/25/30 on **f1_macro, f1_weighted, accuracy, gap** → emit the full candidate table.
- **Model selection is NOT done here.** The `statistical-modeler` agent reads the table and picks the
  single best by judgment (generalization → macro-F1 → supporting metrics → simplicity), writing
  `classification_final.json` with its justification.

## Run
```
python .claude/skills/afb-classification/classify.py --input data/processed/master_video.csv
```
Add `--quick` for a fast smoke run (smaller hyperparameter search).

## Output
- `outputs/models/classification_candidates.csv` — every model × subset with f1_macro/f1_weighted/accuracy/gap.
- `outputs/models/classification_shap.csv` — SHAP feature importance.
- `outputs/models/classification_meta.json` — cut threshold, class balance, ranked SHAP features.
- `outputs/models/classification_final.json` — **written by the statistical-modeler agent**: chosen model + metrics + justification.
