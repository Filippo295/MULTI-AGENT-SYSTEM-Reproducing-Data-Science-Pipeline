# AFB Agent Team

A multi-agent system built on Claude Code that reproduces a full data science pipeline end to end, from raw data to a final report, with no hand-written orchestration code.

---

## The Problem

This project reproduces a fixed data science pipeline, originally run as a set of manual notebooks, on a new dataset. Doing that by hand means repeating the same sequence every time: clean the data, extract features from video and captions, run six statistical models in the right order, then write up a report. It also means keeping dozens of settings exactly the same as the original analysis, things like the number of clusters, the classification threshold, and the random seed, so the results stay comparable across runs.

This project turns that pipeline into seven agents, each responsible for one stage of the process, coordinated by a single orchestrator that runs them stage by stage.

---

## Architecture

Three ideas hold the system together: how decisions get made, how data moves, and how settings are managed.

**Control plane.** One agent, the Project Manager, runs the pipeline. It hands off each stage to one specialist, waits for that specialist to finish and report back, then moves to the next stage. Specialists never talk to each other directly, so all coordination sits in one place.

**Data plane.** Agents do not pass data between each other in messages. Every stage writes its output to a shared folder as a file, CSV, PNG, or JSON, and the next stage reads from there. A crash mid-run does not lose finished work, and anyone can open an intermediate file and see exactly what a stage produced.

**Config plane.** A single file, `afb_config.json`, holds every column name, numeric constant, and file path used anywhere in the pipeline. Every skill reads its settings from this one file through the shared `afb_common` package, so changing a setting once changes it everywhere.

### Roles

Each role is defined by which of Claude Code's built-in tools it can use, not by what its instructions say. Quick reference for the tools in the table below: `Agent` lets one agent hand off work to another. `Bash` runs a script. `Read` opens a file. `Write` creates a new file. `Edit` changes an existing file. `Glob` finds files by name. `Grep` searches inside files for text.

| Role | Tools | What it does |
|---|---|---|
| Project Manager | `Agent`, `Bash`, `Read`, `Write`, `Glob`, `Grep` | The only agent that can delegate. Runs the pipeline stage by stage, checks that expected output files exist, and routes failures: plumbing issues to the Programmer, methodology issues to the user. Also generates the final report itself. |
| Data Engineer | `Bash`, `Read`, `Glob` | Runs data cleaning, feature engineering, and merging. Cannot change what any of those steps compute, only run them. |
| Feature Extractor | `Bash`, `Read` | The only agent that connects to an external service. Calls Gemini through Vertex AI to pull features out of video and caption text, resuming from disk and saving progress every 25 rows so an interrupted run does not restart from zero. |
| Exploratory Analyst | `Bash`, `Read` | Runs descriptive analysis on the full dataset and summarizes what it finds. Limited to descriptive statements, no causal claims. |
| Statistical Modeler | `Bash`, `Read` | Runs the six statistical models. It has more freedom than the other roles: it can make judgment calls, like model selection, and writes down its reasoning when it does. |
| QA Reviewer | `Read`, `Bash`, `Glob`, `Grep` | Checks every output for row counts, missing files, and value ranges, then reports back to the Project Manager. Has no `Edit` or `Write` access, so it can flag a problem but never fix one itself. |
| Programmer | `Bash`, `Read`, `Edit`, `Write`, `Glob`, `Grep` | Fixes plumbing only: broken paths, missing dependencies, encoding errors. If a fix would change a result, it stops and escalates instead of making the change. |

The QA Reviewer and the Programmer work as a pair. The reviewer finds problems, the programmer fixes anything that does not touch the actual analysis, and anything that would change a result goes to a human instead.

### Skills

15 skills, grouped by stage.

**Data preparation** (Data Engineer)
- `afb-cleaning`: handles missing values in the raw dataset
- `afb-feature-engineering`: adds derived columns and the three prediction targets (engagement rate, comments-to-likes ratio, click-through rate)
- `afb-merge`: joins the cleaned data with the extracted features into the two datasets used by every later step

**Feature extraction** (Feature Extractor, via Gemini)
- `afb-extract-video`: pulls visual features (tone, pacing, format, and more) from the full video
- `afb-extract-hook`: pulls the hook strength (strong, medium, weak) from just the first three seconds of each video, since what keeps someone watching in the opening is a different signal from the full video
- `afb-extract-caption`: pulls tone, funnel stage, and length from the caption text

**Exploratory analysis** (Exploratory Analyst)
- `afb-eda`: descriptive statistics and plots on the full dataset, no modeling, just describing what is there

**Statistical analysis** (Statistical Modeler)
- `afb-markov`: models how likely a strong post is to be followed by another strong post, per creator
- `afb-moran`: tests whether a creator's post performance clusters in time
- `afb-clustering`: groups creators into three tiers by size, Macro, Mid-Size, Micro
- `afb-pareto`: plots the Pareto frontier of engagement rate against follower count, using the clustering tiers
- `afb-classification`: separates what drives comments from what drives likes
- `afb-regression`: fits regression models broken out by content type and creator size

**Setup and reporting**
- `afb-setup`: installs dependencies and builds the list of available videos, run once before anything else
- `afb-report`: generates the final report and exports it to PDF (Project Manager only)

### Data flow

Two views of the dataset move through the pipeline. View A is almost every row, about 10,000, and covers analyses that do not need video, EDA, Markov, Moran, and clustering. View B is the roughly 6,000 rows that have a video attached, used for classification and regression. Clustering's output, which tier each creator belongs to, feeds directly into both the Pareto analysis and the per-tier regressions that run later.

---

## Where Everything Lives

- **`afb_config.json`**: the single settings file for the whole project. It holds every column name in the dataset, every numeric constant (cluster count, classification threshold, random seed), and every file path the pipeline uses. Every skill reads from here instead of having values typed into the code.

- **`bootstrap.py`**: a script that installs every Python package the project needs. Run once before anything else.

- **`requirements.txt`**: the plain list of Python packages the project depends on, the one `bootstrap.py` installs from.

- **`afb_common/`**: shared code every skill imports when it runs. `config.py` loads `afb_config.json` once, so every skill reads its settings the same way instead of hardcoding them. `io.py` loads and saves the CSV files, and keeps the video ID column as text so it does not get corrupted into a number, a fix that matters everywhere since almost every skill loads or saves a CSV keyed by that same ID. `gemini.py` holds the logic for calling Gemini, imported only by the three extraction skills, so that logic exists in one place instead of being copied three times.

- **`roles/`**: seven files, one per role (Project Manager, Data Engineer, Feature Extractor, Exploratory Analyst, Statistical Modeler, QA Reviewer, Programmer). Each file is what Claude Code reads to know what that role is allowed to do and which tools it has.

- **`skills/`**: fifteen folders, one per skill. Each one has a `SKILL.md` describing what the skill does and when to run it, plus the Python script that does the actual work. The three extraction skills also include a `prompts.py` with the exact text sent to Gemini.

- **`project_report/`**: the finished output of one full pipeline run, the compiled PDF report, the presentation slides, and the plots referenced in them. This folder is not part of the system, it is what the system produced.

Raw data, generated intermediate files, and credentials are not included in this repository.

---

## What This Produces

- Two data views processed end to end: about 10,000 rows for the full pipeline, about 6,000 with an associated video for the extraction-dependent steps
- Six statistical models run per pipeline execution: Markov chain, Moran's I, clustering, Pareto frontier, classification, regression
- A final PDF report generated automatically from the numeric outputs, not written by hand
- Every numeric choice, cluster count, thresholds, random seed, frozen in one config file, so two runs on the same data produce the same result
- Guardrails are enforced by tool grants: for example instead of telling the QA Reviewer in its prompt not to modify files, it simply has no `Edit` or `Write` tool, so it cannot modify anything regardless of what it is told

---

## Tech Stack

**Orchestration**
- Claude Code: skills and subagents only, no hand-written API or SDK orchestration

**External model**
- `gemini-2.5-flash` via Vertex AI: video and caption feature extraction only

**Statistical modeling**
- `scikit-learn`, `statsmodels`, `shap`, `xgboost`

**Data handling**
- `pandas`, `numpy`

**Plotting**
- `matplotlib`, `seaborn`

**Report generation**
- `markdown`, `xhtml2pdf`
