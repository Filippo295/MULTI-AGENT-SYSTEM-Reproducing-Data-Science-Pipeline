"""Install all Python dependencies for the AFB agent pipeline.

Run once on any fresh machine (e.g. the teacher's PC) before the first pipeline run:

    python bootstrap.py

The orchestrator (Project Manager agent) also calls this automatically at the
start of a run, so a fresh checkout works without manual setup. Idempotent:
re-running just confirms everything is already installed.
"""
import subprocess
import sys
from pathlib import Path

REQ = Path(__file__).resolve().parent / "requirements.txt"


def main():
    print(f"AFB bootstrap: installing dependencies from {REQ.name} ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", str(REQ)])
    print("AFB bootstrap: all dependencies installed.")


if __name__ == "__main__":
    main()
