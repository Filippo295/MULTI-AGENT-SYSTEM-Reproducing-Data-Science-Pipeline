#!/usr/bin/env python
"""afb-regression — log(ENGAGE_RATE) ~ Lasso-selected features + AR(1) lag, OLS clustered SE.

Faithful to afb9-regression. Runs total + the two most-populous clusters (by video-row count).
"""
import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

_p = Path(__file__).resolve()
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
from afb_common import CONFIG, path, load_dataset, save_csv, get_logger  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import statsmodels.api as sm  # noqa: E402
from sklearn.linear_model import Lasso  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

log = get_logger("afb-regression")
C = CONFIG["columns"]
RS = CONFIG["constants"]["random_state"]
ALPHA = CONFIG["constants"]["lasso_alpha"]
GROUP = C["group_var"]
PLOTS = path("plots_dir")

ORD_MAPS = {
    "voice_speed_video_api": {"assente": 0, "lenta": 1, "normale": 1, "veloce": 2},
    "hook_score_api": {"weak": 0, "medium": 1, "strong": 2},
    "posizionamento_api": {"non identificabile": 0, "accessibile": 0, "premium": 1, "lusso": 2},
}
BINARY = {
    "Weekend/Settimanale": {"settimanale": 0, "weekend": 1},
    "Type of content": {"INSTAGRAM_REEL": 0, "TIKTOK_POST": 1},
}
OHE_COLS = ["tone_video_api", "activity_video_api", "format_video_api", "microkinetics_video_api",
            "tone_caption_api", "Creator_gender", "mese", "fascia_oraria", "Industry",
            "funnel_api", "funnel_caption_api", "product_integration_api"]
BASE_NUM = ["media_duration_sec", "caption_length", "Shares", "Saves"]


def encode(df):
    df = df.copy()
    feats = ["Followers"] + [c for c in BASE_NUM if c in df.columns]
    for c, m in ORD_MAPS.items():
        if c in df.columns:
            df[c] = df[c].map(m).fillna(0); feats.append(c)
    for c, m in BINARY.items():
        if c in df.columns:
            df[c] = df[c].map(m); feats.append(c)
    present = [c for c in OHE_COLS if c in df.columns]
    if present:
        df = pd.get_dummies(df, columns=present, dtype=int)
        feats += [c for c in df.columns if any(c.startswith(o + "_") for o in present)]
    if "caption_length" in df.columns:
        df["caption_length"] = df["caption_length"].fillna(0)
    return df, feats


def fit(df, label, out_dir):
    df = df.reset_index(drop=True)
    if len(df) < 50:
        log.warning(f"[{label}] only {len(df)} rows — skipping")
        return
    df["TARGET_LOG"] = np.log(df["ENGAGE_RATE"] * 100 + 0.001)
    enc, feats = encode(df)
    X = enc[feats].fillna(0)
    Xs = pd.DataFrame(StandardScaler().fit_transform(X), columns=feats, index=enc.index)

    lasso = Lasso(alpha=ALPHA, max_iter=20000, random_state=RS).fit(Xs, enc["TARGET_LOG"])
    survivors = [f for f, c in zip(feats, lasso.coef_) if c != 0]
    log.info(f"[{label}] Lasso kept {len(survivors)}/{len(feats)} features")
    if not survivors:
        log.warning(f"[{label}] no features survived Lasso — skipping")
        return

    # AR(1) lag: previous post's log-target per creator (chronological)
    enc["datetime"] = pd.to_datetime(enc[C["date"]].astype(str) + " " + enc[C["time"]].astype(str),
                                     errors="coerce")
    enc = enc.sort_values([GROUP, "datetime"])
    enc["LAG"] = enc.groupby(GROUP)["TARGET_LOG"].shift(1)
    gmean = enc["LAG"].mean()
    enc["LAG"] = enc.groupby(GROUP)["LAG"].transform(lambda x: x.fillna(x.mean())).fillna(gmean)

    dm = sm.add_constant(Xs.loc[enc.index, survivors].copy())
    dm["LAG"] = enc["LAG"].values
    dm["TARGET_LOG"] = enc["TARGET_LOG"].values
    dm["CREATOR"] = enc[GROUP].values
    dm = dm.dropna().reset_index(drop=True)

    y = dm["TARGET_LOG"]
    groups = dm["CREATOR"]
    Xmodel = dm.drop(columns=["TARGET_LOG", "CREATOR"])
    res = sm.OLS(y, Xmodel).fit(cov_type="cluster", cov_kwds={"groups": groups})

    # diagnostics: residuals vs fitted + normal Q-Q (faithful to afb9)
    PLOTS.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f"Regression diagnostics — {label}")
    axes[0].scatter(res.fittedvalues, res.resid, alpha=0.4, s=12, color="teal")
    axes[0].axhline(0, color="red", lw=1)
    axes[0].set_title("Residuals vs Fitted"); axes[0].set_xlabel("Fitted"); axes[0].set_ylabel("Residual")
    sm.qqplot(res.resid, line="s", ax=axes[1], alpha=0.4, markersize=4)
    axes[1].set_title("Normal Q-Q")
    fig.tight_layout(); fig.savefig(PLOTS / f"regression_diag_{label}.png", dpi=100); plt.close(fig)

    coefs = pd.DataFrame({"feature": res.params.index, "coef": res.params.values,
                          "std_err": res.bse.values, "p_value": res.pvalues.values})
    save_csv(coefs, Path(out_dir) / f"regression_{label}.csv")
    log.info(f"[{label}] n={int(res.nobs)}  R2={res.rsquared:.3f}  "
             f"LAG coef={res.params.get('LAG', float('nan')):.3f}  -> regression_{label}.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "master_video.csv"))
    ap.add_argument("--clusters", default=str(path("processed_dir") / "creator_cluster.csv"))
    args = ap.parse_args()

    df = load_dataset(args.input)
    log.info(f"loaded {len(df)} video rows")
    out_dir = path("models_dir")

    fit(df, "total", out_dir)

    cl = pd.read_csv(args.clusters)[[GROUP, "cluster_name"]]
    df = df.merge(cl, on=GROUP, how="left")
    counts = df["cluster_name"].value_counts()
    top2 = counts.head(2).index.tolist()
    log.info(f"cluster post counts (video rows): {counts.to_dict()} -> regressing on {top2}")
    for name in top2:
        fit(df[df["cluster_name"] == name], name, out_dir)


if __name__ == "__main__":
    main()
