# Agents (the team) — 7 roles

| Role | Owns | Uses skills |
|------|------|-------------|
| **project-manager** | plans the run, sequences stages, runs bootstrap, handles failures, assembles deliverable | (delegates) + `afb-report` |
| **data-engineer** | data integrity, the A/B split | `afb-cleaning`, `afb-feature-engineering`, `afb-merge` |
| **feature-extractor** | the only agent touching Gemini; video access, batching, retries, resume | `afb-extract-caption`, `afb-extract-video`, `afb-extract-hook` |
| **exploratory-analyst** | descriptive analysis | `afb-eda` |
| **statistical-modeler** | all models | `afb-markov`, `afb-moran`, `afb-clustering`, `afb-pareto`, `afb-classification`, `afb-regression` |
| **qa-reviewer** | sanity checks (row counts, no leakage, deterministic repro), flags anomalies | read-only validation |
| **programmer** | runtime glue: I/O, schema adaptation, env/error fixes — **never alters model logic** | `afb-setup` + edits plumbing |
