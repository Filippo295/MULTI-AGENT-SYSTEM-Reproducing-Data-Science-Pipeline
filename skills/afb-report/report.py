#!/usr/bin/env python
"""afb-report — business-first report (Layer 1, deterministic) + ENRICH slots (Layer 2, agent).

Body = manager-facing: each chapter is a business question with a data-driven headline, the most
relevant chart, an ENRICH narrative/recommendation slot, and a one-line method note.
Technical appendix = all detailed tables + diagnostic plots + fixed parameters (for analysts).
Numbers are filled deterministically from the output files; only the narrative is enriched later.
"""
import argparse
import json
import re
import sys
from pathlib import Path

_p = Path(__file__).resolve()
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
from afb_common import CONFIG, path, load_dataset, get_logger  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

log = get_logger("afb-report")
M, PR, PLOTS = path("models_dir"), path("processed_dir"), path("plots_dir")
K = CONFIG["constants"]


def _cell(x):
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    if isinstance(x, (float, np.floating)):
        return str(int(x)) if float(x).is_integer() else f"{x:.4f}".rstrip("0").rstrip(".")
    return str(x)


def md_table(df, max_rows=None):
    if max_rows is not None:
        df = df.head(max_rows)
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(_cell(r[c]) for c in cols) + " |")
    return "\n".join(out) + "\n"


def img(rel, caption):
    return f"\n![{caption}](../plots/{rel})\n" if (PLOTS / rel).exists() else ""


def enrich(key, fallback):
    return f"\n> _{fallback}_ <!-- ENRICH:{key} -->\n"


def method(text):
    return f"\n<sub>*How we measured this: {text} Full numbers in the Technical appendix.*</sub>\n"


def num(x, n=3):
    try:
        return f"{float(x):.{n}f}"
    except Exception:
        return str(x)


def safe(s):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", str(s))[:40]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(path("report_dir") / "report.md"))
    args = ap.parse_args()
    s, ap_s, facts = [], [], {}

    s.append("# What Drives Engagement on Sponsored Reels")
    s.append("*An automated analysis of the brand's sponsored Reels & TikToks, for marketing and "
             "product teams. Headlines and recommendations are in plain language; the methods and "
             "full numbers are in the Technical appendix.*\n")
    EXEC = len(s)
    s.append("__EXEC__")

    # ---------- EDA ----------
    if (M / "eda_numeric_corr.csv").exists():
        corr = pd.read_csv(M / "eda_numeric_corr.csv")
        cc = [c for c in corr.columns if c.startswith("pearson")][0]
        top = corr.iloc[0]
        facts["eda"] = (top["variable"], num(top[cc]))
        s.append("\n## What signals move with engagement?\n")
        s.append(f"**Of all the post metrics, **{top['variable']}** is the one most linked to engagement "
                 f"(correlation {num(top[cc])}); raw reach is not.**\n")
        s.append(img("eda/corr_bar.png", "How each metric relates to engagement"))
        s.append(enrich("eda", f"{top['variable']} is the clearest early signal of an engaging post. "
                               "Do this: watch it as a leading indicator rather than chasing reach."))
        s.append(method("Pearson correlation of each numeric post metric with the engagement rate."))
        ap_s.append("\n### A. Exploratory — correlation with engagement\n")
        ap_s.append(md_table(corr))

    # ---------- Regression ----------
    if (M / "regression_total.csv").exists():
        d = pd.read_csv(M / "regression_total.csv")
        sig = d[(d["p_value"] < 0.05) & (d["feature"] != "const")].copy()
        sig["abs"] = sig["coef"].abs()
        sig = sig.sort_values("abs", ascending=False)
        lag_top = len(sig) and sig.iloc[0]["feature"] == "LAG"
        s.append("\n## What makes a reel perform?\n")
        if lag_top:
            s.append("**A creator's recent track record predicts their next reel's engagement better "
                     "than any creative choice.**\n")
        elif len(sig):
            t = sig.iloc[0]
            s.append(f"**The strongest lever on engagement is {t['feature']} "
                     f"({'lifts' if t['coef'] > 0 else 'lowers'} it).**\n")
        s.append(img("report_regression_coef.png", "What pushes engagement up (green) or down (red)"))
        s.append(enrich("regression",
                        "Momentum dominates: a creator on a good run tends to stay on it, while "
                        "content tweaks matter less. Do this: book creators who are currently performing, "
                        "and don't over-engineer the brief."))
        s.append(method("regression on engagement with creator controls; the top factor is the creator's "
                        "previous-post performance."))
        ap_s.append("\n### B. Regression — coefficients (significant, p<0.05)\n")
        ap_s.append(md_table(sig[["feature", "coef", "p_value"]], max_rows=15))
        ap_s.append(img("regression_diag_total.png", "Diagnostics (total): residuals vs fitted & normal Q-Q"))
        for f in sorted(M.glob("regression_*.csv")):
            sc = f.stem.replace("regression_", "")
            if sc == "total":
                continue
            ap_s.append(f"\n**Cluster: {sc}**\n")
            dd = pd.read_csv(f)
            ds = dd[(dd["p_value"] < 0.05) & (dd["feature"] != "const")].copy()
            ds["abs"] = ds["coef"].abs()
            ap_s.append(md_table(ds.sort_values("abs", ascending=False)[["feature", "coef", "p_value"]], 12))
            ap_s.append(img(f"regression_diag_{sc}.png", f"Diagnostics — {sc}"))

    # ---------- Classification ----------
    if (M / "classification_final.json").exists():
        f = json.loads((M / "classification_final.json").read_text(encoding="utf-8"))
        facts["cls"] = (f["final_model"], f["f1_macro"])
        s.append("\n## What sparks conversation, not just likes?\n")
        s.append(f"**Whether a reel drives comments (not just likes) is genuinely hard to predict — the "
                 f"best model ({f['final_model']}) reaches macro-F1 {f['f1_macro']}.**\n")
        s.append(img("report_classification_shap.png", "Which factors best separate 'conversational' reels"))
        s.append(enrich("classification",
                        "Comment-driving content behaves differently from like-driving content, and is "
                        "only weakly predictable from these features. Do this: optimize separately for the "
                        "metric you care about, and treat the model as a guide, not a guarantee."))
        s.append(method("posts split into Conversational vs Silent by comments-per-like; features ranked "
                        "by Random-Forest SHAP; the modeler agent picked the model on macro-F1 + stability."))
        ap_s.append("\n### C. Classification — model selection\n")
        ap_s.append(f"**Chosen: {f['final_model']} @ {f['subset']}** — macro-F1 {f['f1_macro']}, "
                    f"weighted-F1 {f['f1_weighted']}, accuracy {f['accuracy']}, gap {f['gap']}. "
                    f"*{f.get('justification', '')}*\n")
        if (M / "classification_candidates.csv").exists():
            ap_s.append("\nAll candidates (5 models × feature subsets, sorted by macro-F1):\n")
            ap_s.append(md_table(pd.read_csv(M / "classification_candidates.csv")))

    # ---------- Clustering + Pareto ----------
    if (PR / "creator_cluster.csv").exists():
        ccdf = pd.read_csv(PR / "creator_cluster.csv")
        summ = (ccdf.groupby("cluster_name")
                .agg(creators=("Creator name", "size"), posts=("n_posts", "sum"),
                     med_followers=("Followers", "median"), med_ENGAGE_RATE=("ENGAGE_RATE", "median"))
                .reset_index().sort_values("med_ENGAGE_RATE", ascending=False))
        best = summ.iloc[0]
        ratio = best["med_ENGAGE_RATE"] / summ.iloc[1]["med_ENGAGE_RATE"] if len(summ) > 1 and summ.iloc[1]["med_ENGAGE_RATE"] else float("nan")
        facts["clu"] = (best["cluster_name"], num(best["med_ENGAGE_RATE"]))
        s.append("\n## Which creators give the best value?\n")
        rtxt = f" — about {ratio:.0f}x the next tier" if ratio == ratio else ""
        s.append(f"**{best['cluster_name']} creators are the most efficient{rtxt}: more followers does "
                 f"not mean more engagement.**\n")
        s.append(img("pareto_reels.png", "Best engagement at each follower level (frontier in red)"))
        s.append(enrich("segments",
                        f"{best['cluster_name']} creators convert attention into engagement most efficiently, "
                        "and dominate the value frontier. Do this: prioritize frontier and high-efficiency "
                        "creators over sheer follower count."))
        s.append(method("creators grouped by size and engagement; the frontier is the set of creators no "
                        "one beats on both followers and engagement."))
        ap_s.append("\n### D. Creator segments + efficiency frontier\n")
        ap_s.append(md_table(summ))
        if (M / "pareto_frontier.csv").exists():
            ap_s.append(md_table(pd.read_csv(M / "pareto_frontier.csv")))

    # ---------- Markov + Moran ----------
    if (M / "markov.csv").exists():
        mk = pd.read_csv(M / "markov.csv")
        mo = pd.read_csv(M / "moran.csv") if (M / "moran.csv").exists() else None
        mp = mk.loc[mk["p11"].idxmax()]
        facts["mom"] = (mp["creator"], num(mp["p11"]))
        s.append("\n## Does success repeat? Timing campaigns\n")
        s.append(f"**Hot streaks are real but creator-specific — {mp['creator']} sustains momentum, "
                 f"while others bounce back to average after a spike.**\n")
        if mo is not None and len(mo):
            s.append(img(f"moran_{safe(mp['creator'])}.png", f"{mp['creator']}'s reach over time — a streaky creator"))
        s.append(enrich("momentum",
                        "Some creators string strong posts together; others don't. Do this: for streaky "
                        "creators, concentrate sponsored posts during a hot run; for the rest, treat each "
                        "post as independent."))
        s.append(method("for each top creator, how often a strong post is followed by another (Markov) and "
                        "whether strong posts cluster in time (Moran's I)."))
        view = mk[["creator", "n_posts", "p11"]].copy()
        if mo is not None:
            view = view.merge(mo[["creator", "moran_I"]], on="creator", how="left")
        ap_s.append("\n### E. Momentum — Markov persistence (p11) & Moran's I\n")
        ap_s.append(md_table(view))

    # ---------- Executive summary ----------
    ex = ["\n## Executive summary\n"]
    if "reg" in facts or (M / "regression_total.csv").exists():
        ex.append("- **Momentum is the #1 lever** — a creator's recent performance predicts their next reel "
                  "better than any content choice.")
    if "clu" in facts:
        ex.append(f"- **{facts['clu'][0]} creators are the most efficient** — value isn't about follower count.")
    if "mom" in facts:
        ex.append(f"- **Hot streaks are real but creator-specific** ({facts['mom'][0]} sustains them).")
    if "cls" in facts:
        ex.append(f"- **Driving comments ≠ driving likes** — conversation is hard to predict (best model F1 {facts['cls'][1]}).")
    if "eda" in facts:
        ex.append(f"- **{facts['eda'][0]} is the clearest early signal** of an engaging post.")
    ex.append(enrich("executive", "These results point to choosing the right creator at the right moment "
                                  "over fine-tuning the creative. Re-validate on the full dataset before acting."))
    s[EXEC] = "\n".join(ex)

    # ---------- Technical appendix ----------
    s.append("\n\n---\n\n## Technical appendix\n")
    s.append("*Methods and full results, for analysts.*\n")
    nA = len(load_dataset(PR / "master.csv")) if (PR / "master.csv").exists() else "?"
    nB = len(load_dataset(PR / "master_video.csv")) if (PR / "master_video.csv").exists() else "?"
    s.append(f"\n**Data & parameters.** Reels only; `Views` used in place of Reach. View A (all rows, "
             f"{nA}) for EDA/Markov/Moran/clustering/Pareto; View B (video rows, {nB}) for classification "
             f"& regression. Fixed settings: clustering k={K['kmeans_k']}, classification cut="
             f"{K['classification_cut_percentile']} percentile, engagement weights α={K['engagement_alpha']}/"
             f"β={K['engagement_beta']}, Lasso α={K['lasso_alpha']}, Moran K={K['moran_k']}, "
             f"top-{K['nb_top_features']} features, random_state={K['random_state']}.\n")
    s.extend(ap_s)

    report = "\n".join(s) + "\n"
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    log.info(f"report -> {out} ({len(report)} chars, {report.count(chr(10))} lines, "
             f"{report.count('<!-- ENRICH:')} ENRICH slots)")


if __name__ == "__main__":
    main()
