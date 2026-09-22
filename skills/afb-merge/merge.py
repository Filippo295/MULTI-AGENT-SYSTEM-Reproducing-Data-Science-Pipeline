#!/usr/bin/env python
"""afb-merge — join extraction outputs onto engineered data; emit View A + View B.

Faithful to afb5-dataset-merging, reels-only and without the Excel/QA harness.
Runs even when extraction outputs are absent (produces View A only).
"""
import argparse
import sys
from pathlib import Path

_p = Path(__file__).resolve()
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
from afb_common import CONFIG, path, load_dataset, save_csv, get_logger  # noqa: E402

import pandas as pd  # noqa: E402

log = get_logger("afb-merge")
C = CONFIG["columns"]
KEY = C["key"]
CAPTION = C["caption"]
VIDEO_FEATURES = [c for c in C["llm_video_features"] if c != "hook_score_api"]
VIDEO_INDICATOR = "tone_video_api"  # representative video column for View B membership

# extraction output files (written by the extraction skills) -> their feature columns
EXTRACTS = [
    ("extracted_caption.csv", C["llm_caption_features"]),
    ("extracted_video.csv", VIDEO_FEATURES),
    ("extracted_hook.csv", ["hook_score_api"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "engineered.csv"))
    ap.add_argument("--out-all", default=str(path("processed_dir") / "master.csv"))
    ap.add_argument("--out-video", default=str(path("processed_dir") / "master_video.csv"))
    args = ap.parse_args()

    df = load_dataset(args.input)
    log.info(f"loaded {len(df)} engineered rows")

    df["caption_length"] = df[CAPTION].str.split().str.len()

    pdir = path("processed_dir")
    for fname, feats in EXTRACTS:
        fpath = pdir / fname
        if not fpath.exists():
            log.info(f"extraction output not found (skipped): {fname}")
            continue
        ext = load_dataset(fpath).drop_duplicates(subset=KEY)
        keep = [KEY] + [c for c in feats if c in ext.columns]
        df = df.merge(ext[keep], on=KEY, how="left")
        log.info(f"joined {fname}: +{len(keep) - 1} columns")

    # drop failed extractions (ERROR rows) if video features were joined
    if VIDEO_INDICATOR in df.columns:
        err = df[VIDEO_INDICATOR].astype(str).str.startswith("ERROR")
        if err.any():
            log.info(f"dropping {int(err.sum())} rows with ERROR video extraction")
            df = df[~err].reset_index(drop=True)

    save_csv(df, args.out_all)
    log.info(f"View A (all rows) -> {args.out_all}: {len(df)} rows, {df.shape[1]} cols")

    if VIDEO_INDICATOR in df.columns:
        view_b = df[df[VIDEO_INDICATOR].notna()].reset_index(drop=True)
    else:
        view_b = df.iloc[0:0]
        log.warning("no video features present yet — View B is empty (run extraction first)")
    save_csv(view_b, args.out_video)
    log.info(f"View B (video rows) -> {args.out_video}: {len(view_b)} rows")


if __name__ == "__main__":
    main()
