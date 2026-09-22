#!/usr/bin/env python
"""afb-extract-hook — Gemini extraction of hook_score from the FIRST 3 SECONDS of the video.

Prompt + schema verbatim from afb4-extraction_llm_hook (see prompts.py).
Uses video_metadata end_offset='3s'. Processes only rows with a video. Resumable; --dry-run; --limit N.
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
sys.path.insert(0, str(_here))
from afb_common import CONFIG, path, load_dataset, get_logger  # noqa: E402
from afb_common.gemini import run_extraction, gcs_uri  # noqa: E402
from prompts import SYSTEM_PROMPT, Features  # noqa: E402

import pandas as pd  # noqa: E402

log = get_logger("afb-extract-hook")
C = CONFIG["columns"]
FEATURE_MAP = {"hook_score": "hook_score_api"}


def build_contents(row, types):
    part = types.Part(
        file_data=types.FileData(file_uri=gcs_uri(row[C["key"]]), mime_type="video/mp4"),
        video_metadata=types.VideoMetadata(end_offset="3s"),
    )
    cap = row[C["caption"]]
    cap = cap if isinstance(cap, str) and cap.strip() else "No caption provided"
    block = f"=== CAPTION DEL POST (input, da analizzare) ===\n{cap}\n=== FINE CAPTION ==="
    return [part, block]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "engineered.csv"))
    ap.add_argument("--manifest", default=str(path("processed_dir") / "video_manifest.csv"))
    ap.add_argument("--output", default=str(path("processed_dir") / "extracted_hook.csv"))
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
