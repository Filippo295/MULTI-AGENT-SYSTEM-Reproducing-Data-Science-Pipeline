#!/usr/bin/env python
"""export_pdf — convert the final report.md (with its plots) into a self-contained PDF.

Run AFTER report.py (and the enrichment pass). Resolves the report's ../plots/ image links to
the real PNGs and embeds them, so the PDF is viewable anywhere (for the company audience).
"""
import argparse
import sys
from pathlib import Path

_p = Path(__file__).resolve()
while not (_p / "afb_config.json").exists():
    if _p.parent == _p:
        raise FileNotFoundError("afb_config.json not found above this script")
    _p = _p.parent
sys.path.insert(0, str(_p))
from afb_common import path, get_logger  # noqa: E402

import markdown as md_lib  # noqa: E402
from xhtml2pdf import pisa  # noqa: E402

log = get_logger("afb-export-pdf")
REPORT_DIR, PLOTS = path("report_dir"), path("plots_dir")

CSS = """
@page { size: A4; margin: 1.8cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.5pt; color:#222; line-height:1.45; }
h1 { font-size: 20pt; color:#1d3557; margin-bottom:2px; }
h2 { font-size: 14pt; color:#1d3557; border-bottom:1px solid #ccc; padding-bottom:3px; margin-top:16px; }
h3 { font-size: 11.5pt; color:#457b9d; margin-top:12px; }
p { margin: 5px 0; }
table { border-collapse: collapse; width: 100%; font-size: 8.5pt; margin: 6px 0; }
th, td { border: 1px solid #bbb; padding: 3px 5px; }
th { background:#eef2f7; }
img { max-width: 100%; }
blockquote { background:#f5f8fb; border-left:3px solid #457b9d; margin:6px 0; padding:5px 10px; }
"""

# The built-in PDF font renders WinAnsi (em-dash, accents, curly quotes). Map the few symbols
# outside it to safe equivalents so nothing renders as a missing-glyph box.
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
    if "plots/" in uri:
        name = uri.split("plots/", 1)[1]
        p = PLOTS / name
        if p.exists():
            return str(p)
    return uri


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(REPORT_DIR / "report.md"))
    ap.add_argument("--output", default=str(REPORT_DIR / "report.pdf"))
    args = ap.parse_args()

    text = sanitize(Path(args.input).read_text(encoding="utf-8"))
    body = md_lib.markdown(text, extensions=["tables", "sane_lists"])
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"

    with open(args.output, "wb") as fh:
        res = pisa.CreatePDF(html, dest=fh, link_callback=link_callback, encoding="utf-8")
    if res.err:
        log.error(f"PDF had {res.err} render errors")
        sys.exit(1)
    log.info(f"PDF -> {args.output} ({Path(args.output).stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
