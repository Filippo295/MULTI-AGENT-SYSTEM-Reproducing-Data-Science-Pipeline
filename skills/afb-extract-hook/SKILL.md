---
name: afb-extract-hook
description: Gemini hook extraction (Group B). Sends only the FIRST 3 SECONDS of each video (video_metadata end_offset=3s) plus caption to Gemini 2.5 Flash on Vertex AI and extracts hook_score (strong/medium/weak). Prompt + schema verbatim from the project. Processes only rows with a video; resumable; --dry-run and --limit N.
---

# afb-extract-hook

Verbatim port of `afb4-extraction_llm_hook` (prompt + schema in `prompts.py`). Identical to the
video skill except it sends only the first 3 seconds and extracts one variable.

## Run
```
python .claude/skills/afb-extract-hook/extract_hook.py --dry-run
python .claude/skills/afb-extract-hook/extract_hook.py --limit 3
python .claude/skills/afb-extract-hook/extract_hook.py
```

## Output
`data/processed/extracted_hook.csv` — `Filename` + `hook_score_api`.
