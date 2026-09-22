"""Single source of truth: loads afb_config.json and locates the project root.

Every skill script imports from here so that column names, constants, paths and
Gemini settings live in exactly one place (afb_config.json at the project root).
"""
import json
from pathlib import Path


def find_root(start=None):
    """Walk upward from `start` (default: this file) until afb_config.json is found."""
    p = Path(start or __file__).resolve()
    for parent in [p, *p.parents]:
        if (parent / "afb_config.json").exists():
            return parent
    raise FileNotFoundError("afb_config.json not found in any parent directory.")


ROOT = find_root()

with open(ROOT / "afb_config.json", encoding="utf-8") as _f:
    CONFIG = json.load(_f)


def path(key):
    """Resolve a configured path key to an absolute Path under the project root."""
    return (ROOT / CONFIG["paths"][key]).resolve()
