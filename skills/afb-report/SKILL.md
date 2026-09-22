---
name: afb-report
description: Builds the final report for the company (marketing/product managers). Layer 1 (report.py) writes a business-first Markdown — each chapter a business question with a data-driven headline, the key chart, an ENRICH narrative slot, and a one-line method note — plus a Technical appendix (full tables, regression residual/Q-Q diagnostics, fixed parameters). Layer 2 (an agent) writes the narrative grounded in the numbers. Layer 3 (export_pdf.py) renders a self-contained PDF with charts embedded. Run last.
---

# afb-report

Business-first report in three steps.

## Layer 1 — factual backbone (deterministic)
```
python .claude/skills/afb-report/report.py
```
Writes `outputs/report/report.md`: a **business body** (5 chapters phrased as business questions — each
= a bold data-driven headline + the single most-relevant chart inline + a `<!-- ENRICH:key -->`
narrative slot + a one-line method note) and a **Technical appendix** (full tables, regression
residual/Q-Q diagnostics, fixed parameters). Every number comes from the output files.

## Layer 2 — narrative enrichment (agent, grounded)
An analyst/modeler agent rewrites each `<!-- ENRICH:key -->` slot (and the executive summary) into
manager-facing prose ending in a **"Do this:"** recommendation — changing only the narrative, never a
headline, number, table, chart, method note, or the appendix. Markers are removed when done.

## Layer 3 — PDF export (self-contained)
```
python .claude/skills/afb-report/export_pdf.py
```
Renders `outputs/report/report.pdf` with the charts embedded (sanitizes the few non-WinAnsi symbols so
nothing renders as a missing-glyph box). Share the PDF with the company; keep `report.md` in the repo.
