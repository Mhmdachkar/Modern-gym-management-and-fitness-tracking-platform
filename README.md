# Xpert-Bot Intern — Gym Management Database Analysis

## Project Overview
This repository contains Phase 1 work to understand and document a gym management system database from the original SQL dump, and to prepare real datasets for profiling and analysis.

## Project Structure (current)
```
Xpert-Bot-Intern/
├── threesity_final.dump                 # Original MySQL database dump (source of truth)
├── requirements.txt                     # Python dependencies
├── README.md                            # This document
├── phase1_database_exploration/         # Phase 1 artifacts (steps 1, 2, 3)
│   ├── database_analyzer.py             # Parse dump → schema_report.json, key_entities.json
│   ├── erd_generator.py                 # Generate ERDs from schema_report.json
│   ├── schema_report.json               # Full parsed schema (tables, columns, PKs, FKs, summary)
│   ├── key_entities.json                # Mapping of tables to business entities
│   ├── erd_mermaid.md                   # ERD in Mermaid format
│   ├── erd_text.md                      # Detailed ERD text
│   ├── erd_summary.md                   # Business-focused ERD summary
│   ├── data_extractor.py                # Extract real data from dump → CSVs
│   ├── extracted_data/                  # CSVs for analysis (real data)
│   │   ├── members.csv
│   │   ├── coaches.csv
│   │   ├── subscriptions.csv
│   │   ├── sessions.csv
│   │   ├── plans.csv
│   │   ├── packages.csv
│   │   └── extraction_metadata.json
│   └── notebooks/
│       ├── Data_Analysis_phase_1.ipynb  # Colab/local notebook for Phase 1 profiling
│       └── outputs/                     # Optional notebook export figures/reports
└── phase2_data/                         # Placeholder for Phase 2 assets (optional)
```

## Phase 1: Database Understanding & Exploration

- 1. Restore and explore the SQL dump (MySQL) and generate ERD — COMPLETED
  - Outputs: `schema_report.json`, `key_entities.json`, `erd_mermaid.md`, `erd_text.md`, `erd_summary.md`
- 2. Data profiling — Prepared with real CSVs (analyze in notebook)
  - Real datasets extracted to `phase1_database_exploration/extracted_data/`
  - Use `phase1_database_exploration/notebooks/Data_Analysis_phase_1.ipynb` for profiling
- 3. Document schema and relationships — COMPLETED
  - Relationships and business flow summarized in `erd_summary.md`

### Database Information
- Source: `threesity_final.dump`
- Engine: MySQL
- Summary (from schema): 32 tables, 271 columns, 30 primary keys, 17 foreign keys

## Usage

Install dependencies:
```
pip install -r requirements.txt
```

Generate schema and ERDs (from repo root):
```
python phase1_database_exploration/database_analyzer.py
python phase1_database_exploration/erd_generator.py
```

Extract real CSVs from the dump (for profiling in notebooks):
```
python phase1_database_exploration/data_extractor.py
```

Open the profiling notebook:
- Path: `phase1_database_exploration/notebooks/Data_Analysis_phase_1.ipynb`
- The notebook reads CSVs from `../extracted_data/` and can save figures to `./outputs/`

### Notebook CSV paths (copy into your notebook)
```python
import pandas as pd

# Load CSVs (run from phase1_database_exploration/notebooks/)
members = pd.read_csv('../extracted_data/members.csv')
coaches = pd.read_csv('../extracted_data/coaches.csv')
subscriptions = pd.read_csv('../extracted_data/subscriptions.csv')
sessions = pd.read_csv('../extracted_data/sessions.csv')
plans = pd.read_csv('../extracted_data/plans.csv')
packages = pd.read_csv('../extracted_data/packages.csv')

# Optional: save figures/exports
output_dir = './outputs'
# Example: fig.write_image(f"{output_dir}/subscriptions_by_plan.png")
# Example: df_summary.to_csv(f"{output_dir}/subscriptions_summary.csv", index=False)
```

## Notes
- Phase 1 directory contains only the artifacts needed for steps 1–3 plus the real CSVs used by the notebook.
- Non-Phase-1 UI/dashboard code and simulated data were removed.
- If you encounter encoding issues on Windows when running scripts, use:
```
python -X utf8 phase1_database_exploration/database_analyzer.py
```

## Next
- Phase 2: deeper analysis and insights using the Phase 1 CSVs and notebook(s) located under `phase1_database_exploration/notebooks/` or mirrored into `phase2_data/` if preferred. 