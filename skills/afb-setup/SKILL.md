---
name: afb-setup
description: Environment preflight. Installs Python dependencies (bootstrap) and checks readiness — config loads, input dataset present, Gemini/Vertex auth resolves, video manifest present. Run this first on any machine (e.g. the teacher's PC) before the pipeline. Reports a readiness summary.
---

# afb-setup

Makes the project runnable on a fresh machine and reports what's ready.

## Run
```
python .claude/skills/afb-setup/setup.py --install   # install deps + check everything
python .claude/skills/afb-setup/setup.py             # check only
```

## Checks
- Python dependencies (installs via `bootstrap.py` when `--install`).
- `afb_config.json` loads.
- Input dataset present at the configured path.
- Gemini auth resolves (Vertex ADC) — needed only for the extraction skills.
- `video_manifest.csv` present (built once from the GCS bucket).
