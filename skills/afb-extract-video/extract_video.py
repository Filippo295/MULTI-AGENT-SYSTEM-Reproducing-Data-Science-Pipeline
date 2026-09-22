#!/usr/bin/env python
"""afb-extract-video — Gemini extraction of the 8 video variables (full video + caption).

Prompt + Pydantic schema are VERBATIM from afb4-extraction_llm_video (see prompts.py).
Processes only rows with a video (video_manifest.csv). Resumable; --dry-run; --limit N.
"""
import argparse
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_p = _here
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
sys.path.insert(0, str(_here))  # so `import prompts` (this skill's verbatim prompt) resolves
from afb_common import CONFIG, path, load_dataset, get_logger  # noqa: E402
from afb_common.gemini import run_extraction, gcs_uri  # noqa: E402
from prompts import SYSTEM_PROMPT, Features  # noqa: E402

import pandas as pd  # noqa: E402

log = get_logger("afb-extract-video")
C = CONFIG["columns"]

FEATURE_MAP = {"tone_video": "tone_video_api", "voice_speed_video": "voice_speed_video_api",
               "microkinetics_video": "microkinetics_video_api", "activity_video": "activity_video_api",
               "format_video": "format_video_api", "product_integration": "product_integration_api",
               "funnel": "funnel_api", "posizionamento": "posizionamento_api"}


def build_contents(row, types):
    part = types.Part.from_uri(file_uri=gcs_uri(row[C["key"]]), mime_type="video/mp4")
    cap = row[C["caption"]]
    cap = cap if isinstance(cap, str) and cap.strip() else "No caption provided"
    block = f"=== CAPTION DEL POST (input, da analizzare) ===\n{cap}\n=== FINE CAPTION ==="
    return [part, block]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "engineered.csv"))
    ap.add_argument("--manifest", default=str(path("processed_dir") / "video_manifest.csv"))
    ap.add_argument("--output", default=str(path("processed_dir") / "extracted_video.csv"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    df = load_dataset(args.input)
    manifest = set(pd.read_csv(args.manifest, dtype={C["key"]: str})[C["key"]].astype(str))
    df = df[df[C["key"]].astype(str).isin(manifest)].drop_duplicates(subset=C["key"]).reset_index(drop=True)
    log.info(f"{len(df)} unique videos to extract (manifest)")

    run_extraction(df, build_contents, Features, SYSTEM_PROMPT, args.output, FEATURE_MAP, log,
                   dry_run=args.dry_run, limit=args.limit, workers=args.workers)


if __name__ == "__main__":
    main()
