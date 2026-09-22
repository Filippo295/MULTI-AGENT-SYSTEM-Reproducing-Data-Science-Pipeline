#!/usr/bin/env python
"""afb-setup — environment preflight: install deps + report readiness."""
import argparse
import importlib
import subprocess
import sys
from pathlib import Path

_p = Path(__file__).resolve()
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
from afb_common import CONFIG, ROOT, path, get_logger  # noqa: E402

log = get_logger("afb-setup")
MODULES = ["pandas", "numpy", "sklearn", "statsmodels", "shap", "xgboost", "matplotlib",
           "seaborn", "google.genai", "pydantic", "tenacity"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    args = ap.parse_args()

    if args.install:
        log.info("installing dependencies (bootstrap.py) ...")
        subprocess.check_call([sys.executable, str(ROOT / "bootstrap.py")])

    checks = []
    missing = [m for m in MODULES if importlib.util.find_spec(m) is None]
    checks.append(("python dependencies", not missing, f"missing: {missing}" if missing else "all present"))

    ds = path("raw_dataset")
    checks.append(("input dataset", ds.exists(), str(ds)))

    try:
        import google.auth
        _, proj = google.auth.default()
        checks.append(("gemini auth (Vertex ADC)", True, f"project {proj}"))
    except Exception as e:
        checks.append(("gemini auth (Vertex ADC)", False, f"{type(e).__name__} — run `gcloud auth application-default login`"))

    man = path("processed_dir") / "video_manifest.csv"
    checks.append(("video manifest", man.exists(), str(man) if man.exists() else "not built yet"))

    log.info("=== readiness ===")
    for name, ok, detail in checks:
        log.info(f"  [{'OK ' if ok else 'XX '}] {name}: {detail}")
    ready = all(ok for _, ok, _ in checks[:2])  # deps + dataset are the hard requirements
    log.info(f"core pipeline ready: {ready} | extraction ready: {checks[2][1]}")


if __name__ == "__main__":
    main()
