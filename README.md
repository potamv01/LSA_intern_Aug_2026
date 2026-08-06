# SCMD Data Engineering Bootcamp
## August 2026 LSA Intern Cohort

**Building a data pipeline for NHS Secondary Care Medicines data—from raw extract to insight-ready queries.**

---

## 🎯 Project Overview

This repository contains the code, documentation, and deliverables for a **4-week applied data engineering bootcamp** led by [Venkat Potamsetti](https://linkedin.com/in/venkat-potamsetti).

### The Challenge
The NHS spends billions annually on medicines across hospital Trusts but lacks real-time visibility into spending patterns, cost anomalies, and usage trends. This project teaches data engineering fundamentals by building a **production-ready pipeline** that transforms raw medicines data into actionable insights for procurement teams.

### The Dataset
**Source:** [NHS Business Services Authority (NHSBSA) Open Data Portal](https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price)  
**Dataset:** Secondary Care Medicines Data (SCMD) with indicative prices  
**Scope:** All NHS Trusts in England, monthly data since April 2021  
**Format:** CSV files, refreshed monthly (2-month lag)  
**License:** [Open Government Licence 3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

### Key Learning Outcomes
By the end of Week 4, you will have:
- ✅ **Designed** a scalable data architecture from scratch
- ✅ **Built** a reliable ETL pipeline (Extract → Transform → Load)
- ✅ **Implemented** data quality checks and validation gates
- ✅ **Deployed** a queryable data warehouse or local database
- ✅ **Documented** data lineage and governance practices
- ✅ **Communicated** findings through SQL queries and visualizations

**Most importantly:** You'll think like a data engineer—designing for scale, reliability, and trust.

---

## 📂 Repository Structure

```
scmd-data-engineering/
│
├── README.md                          # This file
├── .gitignore                         # Don't commit raw data or secrets
├── requirements.txt                   # Python dependencies
├── config.yaml                        # Project configuration (paths, credentials)
│
├── data/
│   ├── raw/                          # Raw CSV downloads from NHSBSA
│   │   └── scmd_202605.csv
│   ├── processed/                    # Cleaned, validated data
│   │   └── scmd_202605_processed.parquet
│   └── sandbox/                      # Scratch work, temporary files
│
├── src/                              # Core pipeline code
│   ├── __init__.py
│   ├── extract.py                    # Download SCMD CSVs
│   ├── transform.py                  # Clean, validate, enrich
│   ├── load.py                       # Store in warehouse/database
│   ├── validate.py                   # Data quality checks
│   └── pipeline.py                   # Orchestrate the full flow
│
├── tests/                            # Unit and integration tests
│   ├── test_extract.py
│   ├── test_transform.py
│   ├── test_load.py
│   └── test_validate.py
│
├── docs/                             # Documentation & reference materials
│   ├── SCMD_Data_Dictionary.md       # Column definitions & examples
│   ├── Architecture.md                # Design decisions & tech stack
│   ├── Data_Lineage.md               # Data flow diagram & ownership
│   ├── SCMD_Data_Passport.md         # Reference card (source, freshness, license)
│   ├── Week1_DataQuality_Report.md   # Initial findings & gaps
│   ├── Pipeline_Runbook.md           # How to run the pipeline
│   └── FAQ.md                        # Common questions & troubleshooting
│
├── notebooks/                        # Jupyter notebooks for exploration
│   └── eda_scmd.ipynb               # Exploratory data analysis
│
├── sql/                              # SQL queries for analysis
│   ├── top_medicines_by_cost.sql
│   ├── trust_benchmarking.sql
│   └── utilization_trends.sql
│
└── .github/
    └── CODEOWNERS                    # Who owns what
```

---

## 🛠️ Tech Stack

| Component | Options | Recommendation (for starters) |
|-----------|---------|-------------------------------|
| **Language** | Python 3.9+ or SQL | Python (more flexible) |
| **Data Processing** | Pandas, Polars, duckdb | Pandas (Week 1–2), Polars (Week 3+) |
| **Storage** | SQLite, PostgreSQL, BigQuery, S3+Athena | SQLite (local) or PostgreSQL (shared) |
| **Orchestration** | Airflow, Prefect, cron | None (Week 1), cron scripts (Week 2–3) |
| **Testing** | pytest, unittest | pytest |
| **Version Control** | Git + GitHub | Git (required) |
| **Documentation** | Markdown | Markdown (required) |

**No heavy infrastructure needed.** You can complete the bootcamp with just Python + SQLite on your laptop.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.9+** (check: `python --version`)
- **Git** (check: `git --version`)
- **A GitHub account** (if committing code)
- **~3 GB disk space** for downloaded CSVs

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_ORG/scmd-data-engineering.git
cd scmd-data-engineering
```

### 2. Set Up Your Environment
```bash
# Create a Python virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Download Sample Data
```bash
python src/extract.py --year 2026 --month 5
```
This downloads May 2026 SCMD data to `data/raw/scmd_202605.csv`.

### 4. Run Initial Validation
```bash
python src/validate.py data/raw/scmd_202605.csv
```
Check the output for data quality findings. (See `docs/Week1_DataQuality_Report.md` for known issues.)

### 5. Explore the Data
```bash
jupyter notebook notebooks/eda_scmd.ipynb
```
Or dive into the data dictionary in `docs/SCMD_Data_Dictionary.md`.

---

## 📅 Weekly Breakdown

### **Week 1: Explore & Validate**
- Understand SCMD structure and content
- Set up repository and version control
- Build data dictionary and lineage docs
- Identify data quality gaps
- **Deliverables:** Data dictionary, architecture doc, validation report

### **Week 2: Transform & Enrich**
- Clean raw data (handle nulls, deduplicate)
- Build transformation logic in Python/SQL
- Add derived fields (cost per unit, medicine classifications)
- Write unit tests for transformations
- **Deliverables:** Cleaned Parquet files, transformation code, test coverage

### **Week 3: Load & Orchestrate**
- Set up a database (SQLite, PostgreSQL, or BigQuery)
- Write idempotent load logic (safe to run multiple times)
- Build automated pipeline (Python script or Airflow DAG)
- Document the full pipeline runbook
- **Deliverables:** Operational database, runbook, automated pipeline

### **Week 4: Query & Communicate**
- Write SQL queries to answer business questions
- Create 2–3 sample reports or dashboards
- Present findings to stakeholders
- Document lessons learned
- **Deliverables:** SQL queries, reports, presentation

---

## 🔧 Running the Full Pipeline

Once everything is set up, run the complete pipeline with:

```bash
# Run all stages (extract → validate → transform → load)
python src/pipeline.py --year 2026 --month 5

# Or run individual stages
python src/extract.py --year 2026 --month 5
python src/validate.py data/raw/scmd_202605.csv
python src/transform.py data/raw/scmd_202605.csv
python src/load.py data/processed/scmd_202605.parquet
```

**Expected flow:**
```
raw CSV → validated ✓ → cleaned & enriched → loaded to database → ready for queries
```

Check `docs/Pipeline_Runbook.md` for troubleshooting.

---

## 📚 Key Documentation

| Document | Purpose | Read When |
|----------|---------|-----------|
| `docs/SCMD_Data_Dictionary.md` | Column definitions & examples | You're new to the data |
| `docs/Architecture.md` | Design decisions & tech choices | You want to understand the why |
| `docs/Data_Lineage.md` | Data flow & ownership | You need to trace where data comes from |
| `docs/SCMD_Data_Passport.md` | Quick reference card | You need basic facts fast |
| `docs/Week1_DataQuality_Report.md` | Known data quality issues | You're debugging data problems |
| `docs/Pipeline_Runbook.md` | How to run the pipeline | You're operating the system |
| `docs/FAQ.md` | Common questions | You're stuck |

---

## 🧪 Testing

Run the test suite to ensure everything works:

```bash
pytest tests/ -v
```

Write tests for any new code you add:
```bash
# Example test file: tests/test_transform.py
def test_null_handling():
    """Ensure nulls are handled consistently."""
    df = transform_medicines_data(sample_df)
    assert df.isnull().sum().sum() == 0
```

Coverage target: **>80% for critical logic** (extract, transform, validate).

---

## 🤝 Contributing

### Ground Rules
1. **Always work on a branch** (never commit directly to `main`)
   ```bash
   git checkout -b week-2-transform-logic
   ```

2. **Write meaningful commit messages**
   ```bash
   git commit -m "Add null-handling logic for Quantity_Issued field"
   ```

3. **Test your code before pushing**
   ```bash
   pytest tests/ -v
   ```

4. **Document what you changed**
   - Update relevant docs in `docs/`
   - Add docstrings to new functions
   - Update `CHANGELOG.md` (if we have one)

5. **Code review**
   - Open a Pull Request (PR) on GitHub
   - Tag a peer or instructor for review
   - Address feedback before merging

### Example Workflow
```bash
# Create a branch
git checkout -b fix-duplicate-rows

# Make your changes
# ... edit files ...

# Test
pytest tests/ -v

# Stage and commit
git add src/transform.py tests/test_transform.py docs/fixes.md
git commit -m "Remove duplicate rows based on Trust + Medicine + Month"

# Push
git push origin fix-duplicate-rows

# On GitHub: Open a PR, get reviewed, merge
```

---

## 📞 Getting Help

### Resources
- **Data questions:** [NHSBSA Data Services](mailto:DataServicesSupport@nhsbsa.nhs.uk) ((https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price) )
- **Python help:** [Real Python](https://realpython.com/), [w3schools](https://w3schools.com/python/), ChatGPT
- **SQL help:** [SQLite docs](https://www.sqlite.org/docs.html), [Mode Analytics SQL Tutorial](https://mode.com/sql-tutorial/)
- **Git help:** [GitHub Docs](https://docs.github.com/), [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)
- **Data engineering patterns:** [dbt docs](https://docs.getdbt.com/), [Apache Airflow docs](https://airflow.apache.org/docs/)

### Troubleshooting
- **Pipeline fails?** → Check `docs/FAQ.md` and `docs/Pipeline_Runbook.md`
- **Data looks weird?** → Refer to `docs/Week1_DataQuality_Report.md` for known issues
- **Git conflict?** → Ask an instructor or peer for help
- **Stuck for >15 min?** → Post in Slack or raise an issue on GitHub (don't go silent!)

---

## 📋 Data Dictionary Quick Reference

The SCMD dataset includes:
- **`Organisation_Code`** – NHS Trust ID
- **`Organisation_Name`** – Trust name (e.g., "Royal Free NHS Trust")
- **`VMP_Product_Name`** – Medicine name (e.g., "Paracetamol 500mg tablets")
- **`VMP_SNOMED_Code`** – SNOMED-CT code (standardized clinical term)
- **`Quantity_Issued`** – Units dispensed this month
- **`Indicative_Cost`** – Estimated cost (NOTE: indicative only, not actual)
- **`Period_Year`** – Financial year
- **`Period_Month`** – Month (1–12)

**Key caveat:** Costs are **indicative**—they don't reflect actual NHS spending due to confidential discounts and rebates. Use for trend analysis and benchmarking, not absolute cost predictions.

Full details in `docs/SCMD_Data_Dictionary.md`.

---

## 📊 Example Queries

Once data is loaded, you can answer questions like:

```sql
-- Which medicines had the biggest cost increase?
SELECT 
    vmp_product_name,
    MAX(indicative_cost) as peak_cost,
    MIN(indicative_cost) as low_cost,
    ROUND(100.0 * (MAX(indicative_cost) - MIN(indicative_cost)) / MIN(indicative_cost), 2) as pct_change
FROM medicines_fact
GROUP BY vmp_product_name
ORDER BY pct_change DESC
LIMIT 10;

-- How does my trust's spending compare to peers?
SELECT 
    organisation_name,
    SUM(indicative_cost) as total_spend,
    COUNT(DISTINCT vmp_product_name) as medicine_count,
    ROUND(AVG(indicative_cost), 2) as avg_cost_per_medicine
FROM medicines_fact
WHERE period_year = 2026 AND period_month = 5
GROUP BY organisation_name
ORDER BY total_spend DESC;

-- Which medicines are trending?
SELECT 
    vmp_product_name,
    period_month,
    SUM(quantity_issued) as monthly_volume
FROM medicines_fact
WHERE period_year = 2026
GROUP BY vmp_product_name, period_month
ORDER BY vmp_product_name, period_month;
```

See `sql/` for more examples.

---

## ✅ Checklist: Before You Start

- [ ] Python 3.9+ is installed
- [ ] Git is installed
- [ ] You've cloned this repository
- [ ] You've activated the virtual environment (`source venv/bin/activate`)
- [ ] You've installed dependencies (`pip install -r requirements.txt`)
- [ ] You've read `docs/SCMD_Data_Passport.md` (2 min read)
- [ ] You know what the project is trying to solve (re-read **Project Overview**)
- [ ] You've printed or bookmarked `docs/FAQ.md`

---

## 📝 License

This project uses data licensed under the **[Open Government Licence 3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)**.

The pipeline code (Python, SQL, docs) is provided for educational use within this bootcamp.

---

## 👥 Team

**Instructor:**
- Venkat Potamsetti ([LinkedIn]([https://linkedin.com/in/venkat-potamsett](https://www.linkedin.com/in/venkat-potamsetti-projectmanager-businessdataanalyst/))) — Physiotherapist, clinic owner, data engineer in training, bootcamp designer
- If the link does't work use this www.linkedin.com/in/venkat-potamsetti-projectmanager-businessdataanalyst 

**Cohort:** August 2026 LSA Learning & Development Group

**Support:**
- Slack: `#data-engineering-bootcamp`
- GitHub Issues: [Create an issue](../../issues) for bugs or questions
- Office Hours: [Check calendar for instructor availability]

---

## 🚀 Next Steps

1. **Now:** Clone the repo and run setup (should take <15 min)
2. **Week 1:** Start with Task 1.1 in `docs/Week1_Project_Spec.md`
3. **Ongoing:** Commit your work daily (even small changes!)
4. **Week 4:** Be ready to present your findings

---

## 📈 Success Metrics

By the end of the bootcamp, evaluate yourself on:

| Dimension | Level 1 | Level 2 | Level 3 |
|-----------|---------|---------|---------|
| **Data Understanding** | Can name the columns | Can explain why each column matters | Can describe data quality & limitations |
| **Code Quality** | Code runs | Code is tested & documented | Code follows best practices (DRY, SOLID) |
| **Pipeline Reliability** | Pipeline works manually | Pipeline is idempotent | Pipeline auto-recovers from failures |
| **Communication** | Silence or rambling | Clear explanations in docs | Concise docs + engaging presentations |
| **Collaboration** | Solo work | Asks for help when stuck | Helps peers + leaves good commit history |

Aim for **Level 2+ across all dimensions** by Week 4.

---

## 🎓 Learning Outcomes (From the Data Engineer's Perspective)

✅ **Systems thinking:** You understand how data flows through a system and where it can break  
✅ **Reliability mindset:** You design for failure recovery (idempotency, logging, monitoring)  
✅ **Data lineage:** You can trace any number back to its source  
✅ **Quality gates:** You know how to catch bad data before it reaches users  
✅ **Scalability:** You design pipelines that work for 1 month or 10 years of data  
✅ **Communication:** You document assumptions, trade-offs, and gotchas for your future self & teammates  

---

## 🙏 Acknowledgments

- **NHSBSA** for publishing the SCMD dataset openly
- **Your instructors & peers** for making this learning possible
- **The open-source community** (pandas, duckdb, pytest, etc.)

---

## 📞 Questions?

**Before you ask:**
1. Check `docs/FAQ.md`
2. Search the GitHub Issues
3. Review the relevant doc in `docs/`

**If you still need help:**
- Post in Slack
- Create a GitHub Issue with:
  - What you're trying to do
  - What happened (error message)
  - What you expected to happen
  - Steps to reproduce

---

## 🎯 Final Thought

> *"Data engineering is about making sure the right data gets to the right person, at the right time, in a form they can trust."*

Build with that in mind. Good luck! 🚀

---

**Last updated:** August 6, 2026  
**Version:** 1.0  
**Maintained by:** Venkat Potamsetti
