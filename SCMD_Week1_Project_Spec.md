# NHS Secondary Care Medicines Data (SCMD)
## Week 1: Data Engineering Bootcamp Project Spec

---

## Part A: Business Context

### The Problem
The NHS spends billions annually on medicines across hospital Trusts, but lacks real-time visibility into:
- **Procurement costs** by medicine, trust, and time period
- **Usage patterns** (which medicines are trending up/down)
- **Cost anomalies** (unexpected price increases or volume changes)
- **Trust-level benchmarking** (how does my trust's spending compare to peers?)
- **Stockpiling or waste signals** (sudden spikes in single-dose issues)

This opaque spending landscape makes it hard for NHS procurement teams to negotiate better contracts or identify efficiency opportunities. They can't easily answer:
> *"Why did we spend £2.3M on Paracetamol in February, but £1.8M in March? Is that normal? Are other trusts experiencing the same trend?"*

### The Data Source
The **NHS Business Services Authority (NHSBSA)** publishes the **Secondary Care Medicines Data (SCMD)** dataset:
- **Scope:** All NHS Acute, Teaching, Specialist, Mental Health, and Community Trusts in England
- **What it covers:** Medicine quantities issued + indicative cost (from pharmacy stock control systems)
- **Granularity:** By Trust, by Medicine (VMP level), by Month
- **Key fields:**
  - `Organisation_Code` – NHS Trust identifier
  - `Organisation_Name` – Trust name (e.g., "Royal Free NHS Trust")
  - `VMP_Product_Name` – Medicine name (e.g., "Paracetamol 500mg tablets")
  - `VMP_SNOMED_Code` – SNOMED-CT identifier for the medicine
  - `Quantity_Issued` – Units dispensed this month
  - `Indicative_Cost` – Estimated cost (NOT actual net cost due to confidential rebates)
  - `Period_Year` – Financial year (e.g., 2026)
  - `Period_Month` – Month (1–12)
- **Historical coverage:** April 2021 → Present (monthly refresh with 2-month delay)
- **Licensing:** Open Government Licence 3.0 (freely available)

**Important caveat:** Costs are **indicative only**—they overestimate true NHS spend due to confidential procurement discounts. But they're perfect for *trend analysis* and *comparative benchmarking*.

### The Opportunity (For Interns)
Your job: **Build a data pipeline that transforms raw SCMD CSV files into a trusted, queryable repository of medicines data.**

**By the end of Week 4, your system will:**
1. **Ingest** monthly SCMD CSV exports from the NHSBSA portal
2. **Clean & validate** the data (handle nulls, duplicates, schema violations)
3. **Enrich** with derived fields (e.g., cost per unit, spend by therapeutic area)
4. **Store** in a cloud-native format (Parquet, cloud warehouse)
5. **Query** to uncover insights like:
   - "Which medicines had the biggest cost spike in the past 12 months?"
   - "How does our trust's antibiotic spending compare to regional peers?"
   - "Which trusts are outliers for a given medicine?"

---

## Part B: Data Architecture Overview

```
┌─────────────────────────────┐
│  NHSBSA Open Data Portal    │
│  (CSV files, monthly)       │
└──────────────┬──────────────┘
               │
               ▼
        ┌──────────────┐
        │   Extract    │
        │  (Download   │
        │  CSVs)       │
        └──────┬───────┘
               │
               ▼
        ┌──────────────────┐
        │   Load (Raw)     │
        │  Cloud Storage   │
        │  (CSV → Parquet) │
        └──────┬───────────┘
               │
               ▼
        ┌──────────────────┐
        │  Transform       │
        │ • Validate       │
        │ • Deduplicate    │
        │ • Enrich         │
        └──────┬───────────┘
               │
               ▼
        ┌──────────────────┐
        │  Curated Layer   │
        │ (Trusted facts)  │
        └──────┬───────────┘
               │
               ▼
        ┌──────────────────┐
        │  Query / Viz     │
        │  (Insights)      │
        └──────────────────┘
```

### Technical Stack (Flexible—Interns Choose)
- **Language:** Python or SQL (your choice)
- **Orchestration:** Apache Airflow, Prefect, or manual Python scripts (start simple)
- **Storage:** 
  - **Local option:** SQLite, DuckDB, or Postgres (easier to test)
  - **Cloud option:** Google BigQuery, AWS S3 + Athena, Azure Blob + Synapse
- **Data formats:** CSV (input) → Parquet or columnar (processed)
- **Repository:** GitHub (track your pipeline code + documentation)

**Goal:** By Week 4, interns have a reproducible pipeline that can re-run every month as new SCMD data drops.

---

## Part C: Week 1 Tasks (Step-by-Step)

### Task 1.1: Data Exploration & Codebook (2 hours)
**Goal:** Understand the SCMD dataset structure before writing any code.

#### Steps:
1. **Download sample data**
   - Go to https://opendata.nhsbsa.net/dataset/secondary-care-medicines-data-indicative-price
   - Download the most recent month's CSV (e.g., May 2026)
   - Save to your local working directory: `data/raw/scmd_202605.csv`

2. **Inspect the data in a spreadsheet or terminal**
   - **Spreadsheet:** Open in Excel/Sheets, look at columns, scroll through 50 rows
   - **Terminal:** Run `head -20 data/raw/scmd_202605.csv` | `tail -20` | `wc -l`
   
3. **Build a data dictionary**
   - Create a file: `docs/SCMD_Data_Dictionary.md`
   - For each column, document:
     - **Column name** (exact spelling)
     - **Data type** (text, number, date, etc.)
     - **Example values** (2–3 real examples from the CSV)
     - **Nulls/missing data:** Observed? Where?
     - **Valid range** (min/max for numeric columns)
   
4. **Document quirks & surprises**
   - Are there duplicate rows? (Check manually or with `sort | uniq -c`)
   - Any rows with missing key fields (e.g., blank VMP_Product_Name)?
   - Do Quantity_Issued and Indicative_Cost values look reasonable? (e.g., no negatives, no typos like "1,000" vs "1000")
   - Is Period_Year always 2025–2026? Any mismatches?

#### Deliverable:
- `docs/SCMD_Data_Dictionary.md` (< 2 pages)
- 5–10 sample rows from the CSV pasted into the doc
- List of at least 3 data quality observations (e.g., "18 rows have null VMP_SNOMED_Code")

#### Success Criteria:
✅ You can explain what each column means to a non-technical stakeholder  
✅ You've identified at least 2 data quality gaps before writing code  
✅ You have a baseline understanding of the data scale (how many trusts, medicines, etc.)

---

### Task 1.2: Set Up Your Data Repository (1 hour)
**Goal:** Create a structured folder layout + cloud storage connection.

#### Steps:
1. **Create a GitHub repo** (or local folder if no GitHub access)
   ```
   scmd-data-engineering/
   ├── data/
   │   ├── raw/              # Downloaded CSVs
   │   ├── processed/        # Cleaned data
   │   └── sandbox/          # Scratch work
   ├── src/
   │   ├── extract.py        # Download logic
   │   ├── transform.py      # Cleaning logic
   │   ├── load.py           # Storage logic
   │   └── validate.py       # Quality checks
   ├── docs/
   │   ├── SCMD_Data_Dictionary.md
   │   ├── Architecture.md
   │   └── Pipeline_Runbook.md
   ├── tests/
   │   ├── test_extract.py
   │   └── test_transform.py
   ├── README.md
   ├── requirements.txt      # Python packages
   └── config.yaml           # Settings (trust names, file paths, etc.)
   ```

2. **Choose your storage location**
   - **Local:** `/data/raw/scmd_*.csv` + SQLite database in `/data/processed/`
   - **Cloud:** If using BigQuery/S3/Blob, create a project ID / bucket name
   - **Hybrid:** Local CSV ingestion → Cloud warehouse (easier for scaling later)

3. **Initialize version control**
   ```bash
   git init
   git add .
   git commit -m "Initial project structure"
   ```

4. **Document your choices**
   - Create `docs/Architecture.md`:
     - Which tools will you use (Python, SQL, orchestration)?
     - Where will raw data live? Processed data?
     - Who can access it? (Privacy/security)

#### Deliverable:
- GitHub repo link (or folder structure)
- `docs/Architecture.md` (half-page overview)
- `requirements.txt` with placeholder packages (pandas, duckdb, etc.)

#### Success Criteria:
✅ Another intern can clone your repo and find raw data in the expected location  
✅ Folder structure matches the "standard" data eng layout  
✅ README explains the project in 5 sentences

---

### Task 1.3: Write & Test the Extract Function (2 hours)
**Goal:** Automate downloading SCMD data from the NHSBSA portal.

#### Steps:
1. **Write a download script** (`src/extract.py`)
   - Function: `download_scmd_data(month=5, year=2026, output_dir='data/raw/')`
   - **Input:** Month (1–12) and year
   - **Process:**
     - Build the download URL (hint: look at the Open Data Portal URLs; they follow a pattern)
     - Use Python's `requests` library to fetch the CSV
     - Save to `data/raw/scmd_YYYYMM.csv`
   - **Error handling:** Catch network errors, log what failed
   
   **Example skeleton:**
   ```python
   import requests
   import os
   from datetime import datetime
   
   def download_scmd_data(year, month, output_dir='data/raw/'):
       """Download SCMD data for a given month."""
       filename = f"scmd_{year}{month:02d}.csv"
       filepath = os.path.join(output_dir, filename)
       
       # Build URL (construct from NHSBSA pattern)
       url = f"https://opendata.nhsbsa.net/...{year}{month:02d}.csv"
       
       try:
           response = requests.get(url, timeout=30)
           response.raise_for_status()
           with open(filepath, 'wb') as f:
               f.write(response.content)
           print(f"✓ Downloaded {filename}")
           return filepath
       except Exception as e:
           print(f"✗ Failed to download: {e}")
           return None
   
   if __name__ == "__main__":
       download_scmd_data(year=2026, month=5)
   ```

2. **Test the download**
   - Run locally for May 2026 (or latest available)
   - Check that the file appeared in `data/raw/`
   - Verify file size is reasonable (typically 10–50 MB for one month)

3. **Handle historical downloads** (optional)
   - Add a loop to download 3–6 months of data (e.g., Feb–May 2026)
   - Log each success/failure

#### Deliverable:
- `src/extract.py` with `download_scmd_data()` function
- Evidence of successful download (e.g., screenshot or `ls -lh data/raw/`)
- Error handling for failed downloads documented in the code

#### Success Criteria:
✅ Script downloads and saves SCMD CSV to the correct location  
✅ File checksums match expected sizes from the portal  
✅ Script gracefully handles network errors (doesn't crash)  
✅ Code is readable and has docstrings

---

### Task 1.4: Initial Data Validation (2 hours)
**Goal:** Detect obvious data quality issues before transformation.

#### Steps:
1. **Load & inspect the CSV**
   ```python
   import pandas as pd
   
   df = pd.read_csv('data/raw/scmd_202605.csv')
   print(f"Shape: {df.shape}")
   print(f"Columns: {df.columns.tolist()}")
   print(df.head(10))
   print(df.info())
   ```

2. **Check for common issues**
   - **Nulls:** Which columns have missing values? How many?
     ```python
     print(df.isnull().sum())
     ```
   - **Duplicates:** Are there row duplicates? (By what key? Trust + Medicine + Month?)
     ```python
     print(f"Duplicates: {df.duplicated().sum()}")
     ```
   - **Data types:** Are numeric columns actually numeric? Dates formatted correctly?
   - **Ranges:** Do quantities and costs make sense? (e.g., no negative values)
     ```python
     print(df[['Quantity_Issued', 'Indicative_Cost']].describe())
     ```
   - **Unique values:** How many unique trusts? Medicines? 
     ```python
     print(f"Trusts: {df['Organisation_Name'].nunique()}")
     print(f"Medicines: {df['VMP_Product_Name'].nunique()}")
     ```

3. **Create a validation report** (`docs/Week1_DataQuality_Report.md`)
   - Summary statistics (rows, columns, memory size)
   - Null counts by column
   - Duplicate checks (how many, by which key)
   - Outliers (e.g., "Top 5 highest cost entries")
   - Any data type mismatches
   - Sample of problematic rows (if any)

4. **Document expectations** (`src/validate.py`)
   - Write assertions for "known good" data:
     ```python
     def validate_scmd_data(df):
         """Assert that SCMD data meets expected schema."""
         assert 'Organisation_Name' in df.columns
         assert 'VMP_Product_Name' in df.columns
         assert (df['Quantity_Issued'] >= 0).all(), "Negative quantities found"
         assert (df['Indicative_Cost'] >= 0).all(), "Negative costs found"
         print("✓ All validations passed")
     ```

#### Deliverable:
- `src/validate.py` with validation checks
- `docs/Week1_DataQuality_Report.md` (2–3 pages with findings)
- List of 5–10 data quality issues to address in Week 2–3

#### Success Criteria:
✅ Report identifies at least 3 real data quality issues  
✅ Validation script runs without errors  
✅ You know what "clean" data looks like for SCMD  
✅ Team can use this report to decide Week 2 transformation priorities

---

### Task 1.5: Create Data Lineage Documentation (1 hour)
**Goal:** Document the data flow from source to your system.

#### Steps:
1. **Draw a data lineage diagram** (text or Mermaid)
   ```
   NHSBSA Portal (CSVs)
        ↓
   src/extract.py (download)
        ↓
   data/raw/scmd_YYYYMM.csv (raw layer)
        ↓
   src/validate.py (quality checks)
        ↓
   docs/Week1_DataQuality_Report.md (findings)
   ```

2. **Document data transformations so far**
   - What happens to the data at each stage?
   - Who owns each stage?
   - How long does each stage take?
   - Where can it fail?

3. **Create a "data passport"** for SCMD
   - Source: NHSBSA Open Data Portal
   - Freshness: Monthly, 2-month delay
   - Ownership: NHS Business Services Authority
   - License: Open Government Licence 3.0
   - Known limitations: Indicative costs, confidential discounts not included
   - Access: Public, no authentication required

#### Deliverable:
- `docs/Data_Lineage.md` with diagram + narrative
- `docs/SCMD_Data_Passport.md` (reference card for the team)

#### Success Criteria:
✅ A new team member can follow the lineage from source to your system  
✅ Lineage diagram is readable (ASCII, Mermaid, or image)  
✅ Everyone knows the data is provisional and indicative

---

## Part D: Week 1 Checklist & Deliverables

### By end of Week 1, you have:

- [ ] **Task 1.1:** Data dictionary in `docs/SCMD_Data_Dictionary.md`
- [ ] **Task 1.2:** Folder structure + GitHub repo + `docs/Architecture.md`
- [ ] **Task 1.3:** Working `src/extract.py` that downloads CSVs
- [ ] **Task 1.4:** Validation script + `docs/Week1_DataQuality_Report.md`
- [ ] **Task 1.5:** Data lineage + passport docs
- [ ] **README.md:** Explains the project to a new person in 5 sentences
- [ ] **Code is version-controlled:** All code committed to Git with clear commit messages

### Estimated Time Investment:
- Task 1.1: 2 hours
- Task 1.2: 1 hour
- Task 1.3: 2 hours
- Task 1.4: 2 hours
- Task 1.5: 1 hour
- **Total: ~8 hours** (spread across the week)

---

## Part E: Week 1 Success Criteria (Final Rubric)

| Criterion | Expectation | Self-Check |
|-----------|-------------|-----------|
| **Data Understanding** | You can explain SCMD to a clinician in 2 min | ✓ |
| **Architecture Clarity** | Folder structure is logical & documented | ✓ |
| **Extract Reliability** | Download script runs without manual intervention | ✓ |
| **Data Quality** | You've found & documented at least 3 real issues | ✓ |
| **Documentation** | Docs are readable by someone who wasn't here | ✓ |
| **Version Control** | All code is in Git with meaningful commits | ✓ |

---

## Part F: Week 2 Preview (Context for Week 1 Work)

Next week, you'll use what you've built to:
1. **Transform:** Clean the raw data (handle nulls, deduplicate, type conversions)
2. **Enrich:** Add derived fields (cost per unit, therapeutic classifications)
3. **Load:** Move cleaned data into a warehouse or database
4. **Test:** Validate that transformed data matches business expectations

Your Week 1 foundation (understanding + validation rules) will make Week 2 much smoother.

---

## FAQ

**Q: Where do I get the download URL for SCMD files?**  
A: The NHSBSA portal lists resource URLs. Use `requests` to scrape the page or construct the URL pattern. (Hint: URLs follow a consistent naming scheme.)

**Q: Can I use Excel instead of Python?**  
A: For Week 1 exploration, yes. But starting in Week 2, you'll need Python/SQL to automate the pipeline. Start learning Python now if you haven't.

**Q: What if the CSV is huge and my laptop can't handle it?**  
A: Use `pandas.read_csv(..., chunksize=10000)` or `duckdb` for out-of-core processing. Or stream to cloud storage directly.

**Q: Do I need to download all historical data in Week 1?**  
A: No. Start with 1 month (May 2026). Build the pipeline to re-run monthly. Historical backfill can happen in Week 3 if time permits.

**Q: How do I prevent accidental uploads of raw data to Git?**  
A: Add `data/raw/*.csv` to `.gitignore`. Document how to re-download raw data instead.

---

## Support & Questions

- **Data issues?** → Contact NHSBSA at DataServicesSupport@nhsbsa.nhs.uk (reference the dataset name)
- **Technical blockers?** → Pair with another intern or ask your instructor
- **Git help?** → GitHub Docs: https://docs.github.com
- **Python help?** → Real Python, w3schools, or ChatGPT (but write your own code!)
