"""Dataset IO helpers shared by all skills."""
import logging
from pathlib import Path

import pandas as pd

from .config import CONFIG

_KEY = CONFIG["columns"]["key"]


def get_logger(name="afb"):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    return logging.getLogger(name)


def load_dataset(csv_path):
    """Load a dataset CSV with the key column forced to string.

    Critical: the Filename/key holds 19-digit IDs. Reading it as a number would
    corrupt the last digits (float64 precision loss), breaking the video match.
    """
    return pd.read_csv(csv_path, dtype={_KEY: str})


def save_csv(df, csv_path):
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path
