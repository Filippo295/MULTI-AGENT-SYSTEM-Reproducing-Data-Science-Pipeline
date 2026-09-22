---
name: afb-extract-video
description: Gemini video extraction (Group B). Sends each video (from gs://afb-uniting-videos/nuovi-video/) plus its caption to Gemini 2.5 Flash on Vertex AI and extracts the 8 video variables (tone, voice_speed, microkinetics, activity, format, product_integration, funnel, posizionamento). Prompt + schema are verbatim from the project. Processes only rows with a video; resumable; supports --dry-run and --limit N.
---

# afb-extract-video

Verbatim port of `afb4-extraction_llm_video` (prompt + Pydantic schema live in `prompts.py`,
auto-extracted from the notebook). The Excel/human-QA harness is removed — output is a clean CSV.

## When to use
After feature-engineering, before merge. Needs Gemini credentials (Vertex ADC) + the videos in GCS.

## Behaviour
- Reads `engineered.csv`, keeps only Filenames in `video_manifest.csv` (rows that have a video).
- For each: full video via `gs://.../{Filename}_.mp4` + caption block → Gemini → 8 fields.
- **Resumable**: skips Filenames already in the output; **throttled** (2s); failed calls recorded as `ERROR:`.

## Run
```
python .claude/skills/afb-extract-video/extract_video.py --dry-run        # preview requests, no calls
python .claude/skills/afb-extract-video/extract_video.py --limit 3        # tiny live smoke test
python .claude/skills/afb-extract-video/extract_video.py                  # full run (resumable)
```

## Output
`data/processed/extracted_video.csv` — `Filename` + the 8 `*_api` columns.
