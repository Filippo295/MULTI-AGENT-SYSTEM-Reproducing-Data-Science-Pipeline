#!/usr/bin/env python
"""Build the 30-slide project report PDF from slides.md, embedding the project plots."""
import sys
from pathlib import Path

import markdown as md_lib
from xhtml2pdf import pisa

BASE = Path(__file__).resolve().parent
MD = BASE / "slides.md"
OUT = BASE / "AFB_Project_Report.pdf"

CSS = """
@page { size: A4; margin: 1.8cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color:#222; line-height:1.5; }
h1 { font-size: 19pt; color:#1d3557; }
h2 { font-size: 13.5pt; color:#1d3557; border-bottom:1px solid #ccc; padding-bottom:3px; margin-top:18px; }
p { margin: 6px 0; text-align: justify; }
img { max-width: 100%; margin: 6px 0; }
em { color:#444; }
hr { border: none; border-top: 1px solid #ddd; }
"""

REPLACE = {"≠": " not ", "≈": "~", "→": "->", "←": "<-", "✓": "OK", "✗": "X",
           "•": "-", "≥": ">=", "≤": "<=", "×": "x"}


def sanitize(text):
    out = []
    for ch in text:
        try:
            ch.encode("cp1252")
            out.append(ch)
        except UnicodeEncodeError:
            out.append(REPLACE.get(ch, ""))
    return "".join(out)


def link_callback(uri, rel):
    p = (BASE / uri)
    return str(p) if p.exists() else uri


def main():
    text = sanitize(MD.read_text(encoding="utf-8"))
    body = md_lib.markdown(text, extensions=["tables", "sane_lists"])
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
    with open(OUT, "wb") as fh:
        res = pisa.CreatePDF(html, dest=fh, link_callback=link_callback, encoding="utf-8")
    if res.err:
        print(f"PDF render errors: {res.err}")
        sys.exit(1)
    print(f"PDF -> {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
