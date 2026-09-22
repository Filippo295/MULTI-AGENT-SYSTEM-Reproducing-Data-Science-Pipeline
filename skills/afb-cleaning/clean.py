#!/usr/bin/env python
"""afb-cleaning — load, validate, impute missing Likes, export cleaned CSV.

Faithful to afb1-cleaning, adapted to the reels-only new dataset.
"""
import argparse
import sys
from pathlib import Path

# --- locate project root & import shared helpers ---
_p = Path(__file__).resolve()
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
from afb_common import CONFIG, path, load_dataset, save_csv, get_logger  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

log = get_logger("afb-cleaning")
KEY = CONFIG["columns"]["key"]
NUMERIC = ["Followers", "Views", "Likes", "Comments", "Shares", "Saves", "media_duration_sec"]

UNITING_COLS = [
    "Creator name", "Creator_gender", "Filename", "Social permalink", "Channel",
    "Followers", "Type of content", "Post creation date", "Post creation time",
    "Post caption", "Reach", "Likes", "Comments", "Total clicks", "Brand name",
    "Industry", "Local", "Brand_SM", "media_duration_sec", "face_frame_ratio",
    "first_face_position_ratio", "motion_level", "saturation", "luminance",
    "contrast", "sharpness", "color_complexity",
]


def impute_likes(df):
    """Impute missing Likes via comment-percentile -> like-percentile mapping (afb1)."""
    likes = pd.to_numeric(df["Likes"], errors="coerce")
    comments = pd.to_numeric(df["Comments"], errors="coerce")
    valid_likes = likes[likes.notna()]
    valid_comments = comments[likes.notna()]
    missing_idx = df.index[likes.isna()]
    for idx in missing_idx:
        c = comments.loc[idx]
        if pd.isna(c):
            continue
        q = (valid_comments < c).mean()
        df.loc[idx, "Likes"] = int(round(valid_likes.quantile(q)))
    df["Likes"] = pd.to_numeric(df["Likes"], errors="coerce")
    return df, len(missing_idx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("raw_dataset")))
    ap.add_argument("--output", default=str(path("processed_dir") / "cleaned.csv"))
    args = ap.parse_args()

    df = load_dataset(args.input)
    log.info(f"loaded {len(df)} rows x {df.shape[1]} cols from {args.input}")

    absent = [c for c in UNITING_COLS if c not in df.columns]
    if absent:
        log.info(f"absent vs UNITING (expected, not recreated): {absent}")

    for c in NUMERIC:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df, n_imp = impute_likes(df)
    log.info(f"imputed {n_imp} missing Likes via comment-percentile mapping")

    n_zero_views = int((df["Views"] == 0).sum())
    if n_zero_views:
        log.warning(f"dropping {n_zero_views} rows with Views==0 (would break ratio targets)")
        df = df[df["Views"] != 0].reset_index(drop=True)

    miss = {c: int(df[c].isna().sum()) for c in df.columns if df[c].isna().sum()}
    log.info(f"remaining missing values: {miss}")
    log.info(f"duplicate {KEY} rows kept (collaborations): {int(df[KEY].duplicated().sum())}")

    save_csv(df, args.output)
    log.info(f"saved cleaned dataset -> {args.output} ({len(df)} rows)")


if __name__ == "__main__":
    main()
