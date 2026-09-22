#!/usr/bin/env python
"""afb-extract-caption — Gemini extraction of tone_caption + funnel_caption from caption TEXT.

Prompt + schema verbatim from afb4-extraction_llm_caption (see prompts.py). Text-only (no video),
so it runs on every row that has a caption. Brand is passed as "non specificato" (the new dataset
has no Brand name column). Resumable; --dry-run; --limit N.
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
from afb_common.gemini import run_extraction  # noqa: E402
from prompts import SYSTEM_PROMPT, Features  # noqa: E402

log = get_logger("afb-extract-caption")
C = CONFIG["columns"]
FEATURE_MAP = {"tone_caption": "tone_caption_api", "funnel_caption": "funnel_caption_api"}
# new dataset has no Brand name column -> pass "non specificato" (handled here, no fake column)
BRAND = "non specificato"


def build_contents(row, types):
    cap = row[C["caption"]]
    cap = cap if isinstance(cap, str) and cap.strip() else "No caption provided"
    brand = row["Brand name"] if "Brand name" in row and isinstance(row.get("Brand name"), str) else BRAND
    block = ("=== CAPTION DEL POST (input, da analizzare) ===\n"
             f"{cap}\n"
             "=== FINE CAPTION ===\n"
             f"Brand ufficialmente sponsorizzato: {brand}\n")
    return [block]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "engineered.csv"))
    ap.add_argument("--output", default=str(path("processed_dir") / "extracted_caption.csv"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    df = load_dataset(args.input)
    df = df[df[C["caption"]].notna()].drop_duplicates(subset=C["key"]).reset_index(drop=True)
    log.info(f"{len(df)} rows with a caption to extract")

    run_extraction(df, build_contents, Features, SYSTEM_PROMPT, args.output, FEATURE_MAP, log,
                   dry_run=args.dry_run, limit=args.limit, workers=args.workers)


if __name__ == "__main__":
    main()
