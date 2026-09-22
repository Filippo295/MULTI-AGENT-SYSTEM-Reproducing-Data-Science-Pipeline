#!/usr/bin/env python
"""afb-feature-engineering — temporal features + reel targets (Views as Reach).

Faithful to afb2-feature-engineering, adapted to the reels-only new dataset.
CV-derived features (faccia/cognitive_overload/flashiness) are skipped because
their inputs are absent in the new dataset.
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

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

log = get_logger("afb-feature-engineering")
C = CONFIG["columns"]
K = CONFIG["constants"]

MESI = {1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile", 5: "maggio", 6: "giugno",
        7: "luglio", 8: "agosto", 9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"}


def map_fascia(h):
    if pd.isna(h):
        return np.nan
    h = int(h)
    if 0 <= h < 6:
        return "notte"
    if 6 <= h < 11:
        return "mattina"
    if 11 <= h < 15:
        return "pranzo"
    if 15 <= h < 18:
        return "pomeriggio"
    if 18 <= h < 21:
        return "cena"
    return "sera"  # 21-23


def add_temporal(df):
    hour = pd.to_numeric(df[C["time"]].astype(str).str[:2], errors="coerce")
    df["fascia_oraria"] = hour.map(map_fascia)
    dt = pd.to_datetime(df[C["date"]], errors="coerce")
    df["mese"] = dt.dt.month.map(MESI)
    df["Weekend/Settimanale"] = np.where(dt.dt.dayofweek <= 3, "settimanale", "weekend")
    return df


def add_targets(df):
    a, b = K["engagement_alpha"], K["engagement_beta"]
    reach = df[C["reach_proxy"]]  # Views
    df["PERC_REACHED"] = df["Followers"].where(df["Followers"] != 0).rdiv(reach)
    df["ENGAGE_RATE"] = (a * df["Likes"] + b * df["Comments"]) / reach
    df["COMM_PER_LIKE"] = df["Comments"] / df["Likes"].where(df["Likes"] != 0)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "cleaned.csv"))
    ap.add_argument("--output", default=str(path("processed_dir") / "engineered.csv"))
    args = ap.parse_args()

    df = load_dataset(args.input)
    log.info(f"loaded {len(df)} rows from {args.input}")

    df = add_temporal(df)
    log.info(f"temporal: fascia_oraria={df['fascia_oraria'].nunique()} cats, "
             f"mese={df['mese'].nunique()} cats")

    df = add_targets(df)
    for t in ["ENGAGE_RATE", "COMM_PER_LIKE", "PERC_REACHED"]:
        s = df[t]
        log.info(f"target {t}: n={s.notna().sum()} mean={s.mean():.4f} median={s.median():.4f}")

    skipped = ["faccia", "cognitive_overload", "flashiness"]
    log.info(f"skipped CV-derived features (inputs absent): {skipped}")

    save_csv(df, args.output)
    log.info(f"saved engineered dataset -> {args.output} ({len(df)} rows, {df.shape[1]} cols)")


if __name__ == "__main__":
    main()
