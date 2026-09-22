#!/usr/bin/env python
"""afb-classification — Silent vs Conversational; RF+SHAP feature selection; NB top-5 final.

Faithful to afb8-classification, schema-adaptive: only encodes columns that exist.
"""
import argparse
import json
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# --- Plumbing only (does NOT affect any computed result) ---
# Cap per-process BLAS/OpenMP thread pools so the outer RandomizedSearchCV's loky
# workers don't each spawn N native threads. Without this, nested parallelism
# (outer n_jobs=-1 x inner BLAS/OMP threads) oversubscribes the 16 CPUs, blows up
# memory, and the loky executor stalls/terminates workers on Windows. These env
# vars only control HOW the identical computation is scheduled across cores.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

_p = Path(__file__).resolve()
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
from afb_common import CONFIG, path, load_dataset, save_csv, get_logger  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV  # noqa: E402
from sklearn.svm import SVC  # noqa: E402
from sklearn.naive_bayes import GaussianNB  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
import shap  # noqa: E402
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except Exception:
    HAS_XGB = False

log = get_logger("afb-classification")
C = CONFIG["columns"]
RS = CONFIG["constants"]["random_state"]
CUT = CONFIG["constants"]["classification_cut_percentile"]
NB_TOP = CONFIG["constants"]["nb_top_features"]
REACH = C["reach_proxy"]

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
SCORING = {"f1_macro": "f1_macro", "f1_weighted": "f1_weighted", "accuracy": "accuracy"}


def encode(df):
    df = df.copy()
    df["Followers_log"] = np.log1p(df["Followers"])
    df["Views_log"] = np.log1p(df[REACH])
    feats = ["Followers_log", "Views_log"] + [c for c in BASE_NUM if c in df.columns]
    for c, m in ORD_MAPS.items():
        if c in df.columns:
            df[c] = df[c].map(m).fillna(0)
            feats.append(c)
    for c, m in BINARY.items():
        if c in df.columns:
            df[c] = df[c].map(m)
            feats.append(c)
    present_ohe = [c for c in OHE_COLS if c in df.columns]
    if present_ohe:
        df = pd.get_dummies(df, columns=present_ohe, dtype=int)
        feats += [c for c in df.columns if any(c.startswith(o + "_") for o in present_ohe)]
    if "caption_length" in df.columns:
        df["caption_length"] = df["caption_length"].fillna(0)
    return df, feats


def search(estimator, params, X, y, cv, n_iter):
    s = RandomizedSearchCV(estimator, params, n_iter=n_iter, scoring=SCORING, refit="f1_macro",
                           cv=cv, random_state=RS, return_train_score=True, n_jobs=-1)
    s.fit(X, y)
    i, r = s.best_index_, s.cv_results_
    return {"f1_macro": float(r["mean_test_f1_macro"][i]),
            "f1_weighted": float(r["mean_test_f1_weighted"][i]),
            "accuracy": float(r["mean_test_accuracy"][i]),
            "gap": float(r["mean_train_f1_macro"][i] - r["mean_test_f1_macro"][i])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(path("processed_dir") / "master_video.csv"))
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    qf = 0.2 if args.quick else 1.0

    df = load_dataset(args.input)
    log.info(f"loaded {len(df)} rows from {args.input}")

    soglia = df["COMM_PER_LIKE"].quantile(CUT)
    y = (df["COMM_PER_LIKE"] > soglia).astype(int)
    log.info(f"target cut @ p{int(CUT*100)} = {soglia:.5f} | class balance: {y.value_counts().to_dict()}")

    df, feats = encode(df)
    X = df[feats].fillna(0)
    log.info(f"feature matrix: {X.shape[1]} features, {len(X)} rows")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RS)

    # Random Forest for SHAP feature selection
    rf_params = {"n_estimators": [100, 200, 300, 500], "max_depth": [5, 8, 10, 15, 20, 30, None],
                 "min_samples_leaf": [10, 20, 30, 50], "max_features": ["sqrt", "log2", 0.3, 0.5],
                 "class_weight": ["balanced"]}
    # inner estimator n_jobs=1: parallelism is driven by the OUTER RandomizedSearchCV
    # (n_jobs=-1). Nesting inner n_jobs=-1 under the outer search oversubscribes CPUs
    # and deadlocks loky on Windows. n_jobs only changes scheduling, never the scores.
    rf_search = RandomizedSearchCV(RandomForestClassifier(random_state=RS, n_jobs=1), rf_params,
                                   n_iter=max(5, int(50 * qf)), scoring=SCORING, refit="f1_macro",
                                   cv=cv, random_state=RS, n_jobs=-1, return_train_score=True)
    rf_search.fit(X, y)
    log.info(f"RF best CV f1_macro = {rf_search.best_score_:.3f}")
    rf = RandomForestClassifier(**rf_search.best_params_, random_state=RS, n_jobs=1).fit(X, y)

    sv = shap.TreeExplainer(rf).shap_values(X)
    sv = sv[:, :, 1] if getattr(sv, "ndim", 0) == 3 else (sv[1] if isinstance(sv, list) else sv)
    imp = (pd.DataFrame({"feature": X.columns, "mean_abs_shap": np.abs(sv).mean(axis=0)})
           .sort_values("mean_abs_shap", ascending=False).reset_index(drop=True))
    save_csv(imp, path("models_dir") / "classification_shap.csv")

    ks = [k for k in [5, 10, 15, 20, 25, 30] if k <= X.shape[1]]
    models = {
        "NB": (GaussianNB(), {"var_smoothing": [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]}, False, 7),
        "SVM": (SVC(random_state=RS), {"C": [0.01, 0.1, 1, 10, 100], "kernel": ["linear", "rbf"],
                "gamma": ["scale", "auto"], "class_weight": ["balanced"]}, True, 20),
        "KNN": (KNeighborsClassifier(), {"n_neighbors": [3, 5, 7, 10, 15, 20, 25, 30],
                "weights": ["uniform"], "metric": ["euclidean", "manhattan"]}, True, 16),
        "LR": (LogisticRegression(random_state=RS, max_iter=1000), {"C": [0.001, 0.01, 0.1, 1, 10, 100],
               "penalty": ["l1", "l2"], "solver": ["liblinear"], "class_weight": ["balanced"]}, True, 12),
    }
    if HAS_XGB:
        spw = (y == 0).sum() / max(1, (y == 1).sum())
        models["XGB"] = (XGBClassifier(random_state=RS, n_jobs=1, eval_metric="logloss"),
                         {"n_estimators": [100, 200, 300], "max_depth": [2, 3, 4, 5],
                          "learning_rate": [0.01, 0.05, 0.1, 0.2], "subsample": [0.5, 0.7, 1.0],
                          "colsample_bytree": [0.5, 0.7, 1.0], "min_child_weight": [5, 10, 20, 30],
                          "scale_pos_weight": [spw]}, False, 30)

    rows = []
    n_models = len(models)
    n_subsets = len(ks)
    log.info(f"starting candidate sweep: {n_models} models x {n_subsets} subsets = "
             f"{n_models * n_subsets} fits over ks={ks}")
    for k in ks:
        sel = imp["feature"].head(k).tolist()
        Xk = X[sel]
        Xk_s = pd.DataFrame(StandardScaler().fit_transform(Xk), columns=sel, index=Xk.index)
        for name, (est, params, scale, n_iter) in models.items():
            log.info(f"  [top{k}] fitting {name} ...")
            r = search(est, params, Xk_s if scale else Xk, y, cv, max(3, int(n_iter * qf)))
            log.info(f"  [top{k}] {name} done: f1_macro={r['f1_macro']:.4f} gap={r['gap']:.4f}")
            rows.append({"model": name, "subset": f"top{k}", "n_features": k,
                         "f1_macro": round(r["f1_macro"], 4), "f1_weighted": round(r["f1_weighted"], 4),
                         "accuracy": round(r["accuracy"], 4), "gap": round(r["gap"], 4)})
        log.info(f"top{k} evaluated for {len(models)} models")
    cand = pd.DataFrame(rows).sort_values("f1_macro", ascending=False).reset_index(drop=True)
    save_csv(cand, path("models_dir") / "classification_candidates.csv")
    (path("models_dir") / "classification_meta.json").write_text(json.dumps(
        {"cut_threshold": float(soglia),
         "class_balance": {"silent": int((y == 0).sum()), "conversational": int((y == 1).sum())},
         "top_shap_features": imp["feature"].head(max(ks)).tolist()}, indent=2, ensure_ascii=False))
    log.info(f"saved {len(cand)} candidates (models x subsets) -> classification_candidates.csv")
    log.info("model SELECTION is left to the statistical-modeler agent (judgment framework) — no hardcoded winner")


if __name__ == "__main__":
    main()
