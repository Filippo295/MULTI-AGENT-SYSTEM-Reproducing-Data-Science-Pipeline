# Skills (the toolbox)

15 micro-skills, one per pipeline component. Each is a folder with `SKILL.md`
(when-to-use + how-to-run) and a Python script that imports `afb_common`.
Group A = runs on all rows; Group B = runs on video rows only.

| Skill | Group | Purpose |
|-------|-------|---------|
| `afb-cleaning` | A | load (Filename as str), validate schema, impute missing Likes |
| `afb-feature-engineering` | A | `mese`/`fascia_oraria`/`Weekend`; targets ENGAGE_RATE, COMM_PER_LIKE, PERC_REACHED (Views) |
| `afb-extract-caption` | A | Gemini text → `tone_caption`, `funnel_caption` (brand="non specificato") |
| `afb-extract-video` | B | Gemini full video → 8 vars + microkinetics |
| `afb-extract-hook` | B | Gemini first-3s → `hook_score` |
| `afb-merge` | A/B | join extracted features, `caption_length`, drop ERROR rows → View A + View B |
| `afb-eda` | A+B | distributions + target correlations + plots |
| `afb-markov` | A | transition matrix on Views states, top creator(s) by post count |
| `afb-moran` | A | Moran's I scatterplot (K=3) on Views, top creator(s) |
| `afb-clustering` | A | KMeans k=3, label by follower size → creator→cluster export |
| `afb-pareto` | A | Pareto frontier (Followers vs ENGAGE_RATE), consumes clusters |
| `afb-classification` | B | Silent/Conversational (cut=0.75), RF+SHAP → NB top-5 + comparison |
| `afb-regression` | B | Lasso α=0.05 + OLS+AR(1)+clustered SE; scope = total / Macro / Micro |
| `afb-report` | — | assemble outputs + insights into the final Markdown report |
| `afb-setup` | — | environment check / dependency install wrapper around bootstrap.py |
