#!/usr/bin/env python
"""afb-eda — distributions + target relationships for every meaningful variable present.

Faithful to afb3 (reels), schema-adaptive. Target = ENGAGE_RATE.
"""
import argparse
import re
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
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

log = get_logger("afb-eda")
TARGET = "ENGAGE_RATE"
NUM = ["Followers", "Views", "Likes", "Comments", "Shares", "Saves", "media_duration_sec", "caption_length"]
CAT = ["Type of content", "mese", "fascia_oraria", "Weekend/Settimanale", "Creator_gender", "Industry",
       "tone_video_api", "voice_speed_video_api", "microkinetics_video_api", "activity_video_api",
       "format_video_api", "product_integration_api", "funnel_api", "posizionamento_api",
       "hook_score_api", "tone_caption_api", "funnel_caption_api"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "master.csv"))
    args = ap.parse_args()

    df = load_dataset(args.input)
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    plots = path("plots_dir") / "eda"
    plots.mkdir(parents=True, exist_ok=True)

    num = [c for c in NUM if c in df.columns]
    cat = [c for c in CAT if c in df.columns]
    log.info(f"{len(num)} numeric + {len(cat)} categorical variables present")

    # numeric: correlation with target + histogram grid
    corr = []
    for c in num:
        s = pd.to_numeric(df[c], errors="coerce")
        corr.append({"variable": c, f"pearson_with_{TARGET}": round(s.corr(df[TARGET]), 4)})
    corr_df = pd.DataFrame(corr).sort_values(f"pearson_with_{TARGET}", key=lambda s: s.abs(), ascending=False)
    save_csv(corr_df, path("models_dir") / "eda_numeric_corr.csv")

    ncols = 3
    nrows = int(np.ceil(len(num) / ncols)) or 1
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 3.5 * nrows))
    for ax, c in zip(np.array(axes).ravel(), num):
        pd.to_numeric(df[c], errors="coerce").plot(kind="hist", bins=60, ax=ax, edgecolor="none")
        ax.set_title(c)
    for ax in np.array(axes).ravel()[len(num):]:
        ax.set_visible(False)
    fig.tight_layout(); fig.savefig(plots / "hist_numeric.png", dpi=100); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, max(3, 0.4 * len(corr_df))))
    ax.barh(corr_df["variable"][::-1], corr_df[f"pearson_with_{TARGET}"][::-1],
            color=["#2a9d8f" if v >= 0 else "#e63946" for v in corr_df[f"pearson_with_{TARGET}"][::-1]])
    ax.axvline(0, color="black", lw=1); ax.set_title(f"Correlation with {TARGET}")
    fig.tight_layout(); fig.savefig(plots / "corr_bar.png", dpi=100); plt.close(fig)

    # categorical: median target per category + boxplot
    rows = []
    thr = df[TARGET].quantile(0.99)
    for c in cat:
        sub = df[[c, TARGET]].dropna()
        if sub[c].nunique() < 2:
            continue
        grp = sub.groupby(c)[TARGET].agg(["median", "count"])
        for val, r in grp.iterrows():
            rows.append({"variable": c, "category": val, "median_target": round(r["median"], 5),
                         "count": int(r["count"])})
        safe = re.sub(r"[^A-Za-z0-9_-]+", "_", c)[:40]
        fig, ax = plt.subplots(figsize=(max(6, 0.8 * sub[c].nunique()), 5))
        sub[sub[TARGET] < thr].boxplot(column=TARGET, by=c, ax=ax)
        ax.set_title(f"{TARGET} by {c}"); plt.suptitle(""); ax.tick_params(axis="x", rotation=45)
        fig.tight_layout(); fig.savefig(plots / f"box_{safe}.png", dpi=100); plt.close(fig)

    save_csv(pd.DataFrame(rows), path("models_dir") / "eda_categorical_medians.csv")
    log.info(f"top |correlation|: {corr_df.iloc[0]['variable']} = {corr_df.iloc[0][f'pearson_with_{TARGET}']}")
    log.info(f"saved EDA tables + {2 + len([c for c in cat if df[c].nunique() >= 2])} plots -> outputs/")


if __name__ == "__main__":
    main()
