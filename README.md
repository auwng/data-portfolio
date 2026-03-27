# Seattle Public Library — Checkout Analysis

Analysis of 22M+ checkout records from the Seattle Public Library (SPL) spanning 2017–2025, exploring how reading habits have shifted across physical and digital formats over time.

---

## Project Scope

This project currently focuses on **library performance** — understanding checkout volumes, catalog utilization, demand concentration, and genre trends across physical books and digital ebooks.

Future analyses may expand to a **Seattle citizen lens**, exploring how checkout behavior varies across neighborhoods, demographics, and community needs.

---

## Dataset

**Source:** [Seattle Open Data — Checkouts by Title](https://data.seattle.gov/Community-and-Culture/Checkouts-by-Title/tmmm-ytt6/about_data)  
**Coverage:** January 2017 – 2025 (22M+ rows)  
**Formats covered:** Physical books, Digital ebooks (OverDrive/Libby, Hoopla, Freegal, Zinio)

---

## Data Pipeline

| Notebook | Purpose |
|---|---|
| [01_ingestion.ipynb](notebooks/01_ingestion.ipynb) | Ingests raw checkout data from the Socrata API with checkpoint/retry logic |
| [02_cleaning.ipynb](notebooks/02_cleaning.ipynb) | Deduplication, type normalization, work_key generation, physical/digital split |
| [03_qa.ipynb](notebooks/03_qa.ipynb) | Row count verification, uniqueness checks, data quality validation |

---

## Analyses

| Analysis | Report | Notebook |
|---|---|---|
| SPL Library Performance 2017–2025 | [Report](analyses/splreports/spl_performance_report.md) | [Notebook](analyses/spl_performance_2017_2025.ipynb) |

---

## Key Concepts

**Work** — defined as a unique title + creator combination, collapsing across editions. Physical libraries typically stock multiple editions of the same work (hardcover, paperback, large print), each catalogued as a distinct title. Analyzing at the title level overstates physical checkout breadth relative to digital, so all analyses use work as the primary unit.

---

## Key Findings

- Physical checkouts dropped sharply during COVID-19 closures in 2020 and have not recovered to pre-pandemic levels
- Digital checkouts were unaffected by COVID and have grown steadily since 2017
- Physical and digital catalogs have converged in breadth — both formats serve a similar number of distinct works per month post-2021
- The top 10% of works account for ~50% of total checkouts across both formats
- ~10,000 physical works and ~6,800 digital works are needed to capture 50% of monthly checkouts
- Digital checkouts are more concentrated among popular titles than physical, consistent with platform recommendation effects

---

## Repository Structure
```
seattle-checkouts/
├── README.md
├── notebooks/                            # Ingestion, cleaning, QA
│   ├── 01_ingestion.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_qa.ipynb
│   └── exploratory/                      # Scratch notebooks, not for publication
│       ├── 04_analysis_exploratory.ipynb
│       └── title_matching_development.ipynb
├── analyses/
│   ├── spl_performance_2017_2025.ipynb   # Final analysis notebook
│   ├── reports/
│   │   └── spl_performance_report.md
│   └── figures/                          # Final charts referenced in report
│       └── exploratory/                  # Exploratory charts, not in report
├── data/
│   ├── raw/                              # Gitignored
│   └── processed/                        # Gitignored
└── shared/
    └── utils/                            # Shared ingestion, cleaning, plotting utilities
        ├── ingestion.py
        ├── cleaning.py
        └── plotting.py
```

---

## Setup
```bash
# Install dependencies
pip install -r shared/requirements.txt

# Add your Socrata API token
echo "SEATTLE_API_TOKEN=your_token_here" > projects/seattle-checkouts/.env
```

---

## Tools & Libraries

- **Python** — pandas, matplotlib, pyarrow
- **JupyterLab** — analysis and visualization
- **Socrata API** — data ingestion
- **Parquet** — checkpoint storage for large dataset ingestion