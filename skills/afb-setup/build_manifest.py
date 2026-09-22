#!/usr/bin/env python
"""build_manifest — list the GCS video bucket and write video_manifest.csv (Filenames with a video).

Run before the video/hook extraction on a new dataset/bucket. Uses the gcloud CLI.
"""
import subprocess
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

log = get_logger("afb-build-manifest")
V, C = CONFIG["video"], CONFIG["columns"]


def main():
    prefix = f"gs://{V['gcs_bucket']}/{V['gcs_prefix']}/"
    log.info(f"listing {prefix} ...")
    res = subprocess.run(f"gcloud storage ls {prefix}", shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        log.error(f"gcloud failed: {res.stderr[:300]}")
        sys.exit(1)

    gcs_ids = set()
    for line in res.stdout.splitlines():
        line = line.strip()
        if line.endswith(".mp4"):
            name = line.split("/")[-1][:-4]            # strip .mp4
            gcs_ids.add(name[:-1] if name.endswith("_") else name)  # strip trailing underscore

    df = load_dataset(path("raw_dataset"))
    matched = set(df[C["key"]].astype(str)) & gcs_ids
    save_csv(pd.DataFrame({C["key"]: sorted(matched)}), path("processed_dir") / "video_manifest.csv")
    log.info(f"GCS videos: {len(gcs_ids)} | dataset rows with video: {len(matched)} -> video_manifest.csv")


if __name__ == "__main__":
    main()
