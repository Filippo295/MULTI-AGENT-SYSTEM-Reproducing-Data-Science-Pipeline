---
name: afb-extract-caption
description: Gemini caption extraction (Group A — text only, all rows with a caption). Sends the caption text (plus brand="non specificato", since the new dataset has no Brand name column) to Gemini 2.5 Flash and extracts tone_caption and funnel_caption. Prompt + schema verbatim from the project. No video needed; resumable; --dry-run and --limit N.
---

# afb-extract-caption

Verbatim port of `afb4-extraction_llm_caption` (prompt + schema in `prompts.py`). Text-only, so it
runs on every row that has a caption (~9,981), independent of whether a video exists.

## Notes
- Brand is passed as `"non specificato"` (no Brand name column in the new dataset) — handled in code,
  no fake column. Revisit if a brand column is ever added.

## Run
```
python .claude/skills/afb-extract-caption/extract_caption.py --dry-run
python .claude/skills/afb-extract-caption/extract_caption.py --limit 3
python .claude/skills/afb-extract-caption/extract_caption.py
```

## Output
`data/processed/extracted_caption.csv` — `Filename` + `tone_caption_api`, `funnel_caption_api`.
