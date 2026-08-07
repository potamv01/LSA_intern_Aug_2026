# Free Tools for Data Engineering: Design, Architecture & Learning

This guide introduces free, open-source, and no-cost tools that will help you master data engineering concepts — from designing your pipelines to building and orchestrating them.

---

## 1. Architecture & Design: **draw.io** (diagrams.net)

**What it is:** A free, browser-based diagramming tool with no signup required.

**Why use it for your project:**
- Design your data pipeline architecture before you code it
- Map data lineage (where data comes from, what transformations it undergoes, where it goes)
- Document task dependencies and data flow
- Create flowcharts for ETL processes

**How it fits Week 1:**
- Create a diagram for your SCMD pipeline: **Download → Validate → Clean → Load**
- Show the data schema (inputs vs. outputs at each stage)
- Document what happens if validation fails (branching logic)

**Get started:**
- Go to [diagrams.net](https://diagrams.net)
- No signup needed; save locally or to Google Drive
- Look for built-in shape libraries: *Data*, *AWS*, *Flowchart*
- Export as PNG, PDF, or SVG for your deliverables

**Real-world relevance:** Data teams use architecture diagrams in design reviews, onboarding docs, and runbooks. This is a professional skill.

---

## 2. Hands-On Learning: SQL & Analytics

### **Option A: DuckDB** (Recommended for beginners)
**What it is:** A lightweight, zero-setup analytical database that runs on your laptop.

**Why use it:**
- No server setup — just `pip install duckdb`
- Loads CSV files directly: `SELECT * FROM 'medicines_data.csv'`
- Teaches SQL without needing Postgres
- Fast enough for learning; mature enough for real analysis

**How it fits Week 1:**
```python
import duckdb

# Load your downloaded SCMD CSV
result = duckdb.sql("SELECT * FROM 'scmd_data.csv' LIMIT 5")
print(result)

# Validate data quality
missing = duckdb.sql("SELECT COUNT(*) FROM 'scmd_data.csv' WHERE medicine_name IS NULL")
```

**Why this matters:** Most data engineering is SQL. Learning it early, on your own data, is essential.

---

### **Option B: Data Quality & Validation: Great Expectations (or Pandera)**

**What it is:** A Python library that tests data quality — checks schema, missing values, ranges, uniqueness.

**Why use it:**
- Automates the "validation" step of your pipeline
- Catches data issues *before* they corrupt your load
- Teaches the concept: **quality gates** (what you're already doing manually)

**How it fits Week 1:**
```python
from great_expectations.dataset import PandasDataset

# Load your data
df = pd.read_csv('scmd_data.csv')
data = PandasDataset(df)

# Validate: all medicines have a name
data.expect_column_values_to_not_be_null('medicine_name')

# Validate: cost is a positive number
data.expect_column_values_to_be_between('cost', min_value=0, max_value=100000)
```

**Why this matters:** Real pipelines can't trust data. This is how professionals ensure quality.

---

## 3. Transformation & Modeling: **dbt Core** (Data Build Tool)

**What it is:** A free, open-source tool that turns SQL into version-controlled, tested data transformations.

**Why use it:**
- Write transformations as SQL *files*, not Python scripts
- dbt runs them in dependency order (like a DAG, but simpler)
- Tracks lineage automatically
- Teaches best practices: modularity, testing, documentation

**How it fits Week 1 → Week 2:**
```sql
-- models/transform_medicines.sql
{{ config(materialized='table') }}

SELECT
    medicine_id,
    medicine_name,
    CAST(cost AS FLOAT) as cost_numeric,
    DATE(data_date) as date_loaded
FROM {{ source('raw', 'scmd_medicines') }}
WHERE cost IS NOT NULL
```

Then run: `dbt run` — dbt handles the orchestration.

**Why this matters:** If your interns want to work in data teams, they'll use dbt. It's industry standard.

---

## 4. Orchestration: **Apache Airflow** (For Week 2+)

**What it is:** A free, open-source platform for scheduling and monitoring workflows (DAGs).

**Why use it:**
- Orchestrates your pipeline: download → validate → clean → load
- Handles retries, error logging, and alerting
- Teaches idempotency and dependency management
- Used at 500+ organizations

**How it fits Week 2+:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

dag = DAG('scmd_pipeline', start_date=datetime(2024, 1, 1), schedule_daily=True)

download_task = PythonOperator(task_id='download', python_callable=download_scmd, dag=dag)
validate_task = PythonOperator(task_id='validate', python_callable=validate_data, dag=dag)
load_task = PythonOperator(task_id='load', python_callable=load_to_db, dag=dag)

download_task >> validate_task >> load_task
```

**Why this matters:** Orchestration is where data engineering meets production. Learning it opens doors to real DE roles.

---

## Tool Stack Summary: What to Learn When

| **Week** | **Focus** | **Tool** | **Why** |
|----------|---------|---------|--------|
| **Week 1** | Design + Manual Pipeline | draw.io + Python scripts | Understand the architecture & data flow by hand |
| **Week 1** | Data Quality | Great Expectations | Learn to codify validation rules |
| **Week 2** | SQL + Analytics | DuckDB | Master SQL on your own data |
| **Week 2–3** | Transformation | dbt Core | Teach modularity & testing |
| **Week 3+** | Orchestration | Airflow | Schedule & monitor the whole pipeline |

---

## Getting Started: Quick Reference

### Install locally (all free):
```bash
# DuckDB
pip install duckdb

# Great Expectations
pip install great_expectations

# dbt (requires a database connection, but DuckDB works)
pip install dbt-core dbt-duckdb

# Airflow
pip install apache-airflow
```

### First task for each:

**draw.io:** Create a diagram of your SCMD pipeline with 4 boxes (Download, Validate, Clean, Load) and arrows showing data flow.

**DuckDB:** Load your first SCMD CSV and count rows:
```python
import duckdb
result = duckdb.sql("SELECT COUNT(*) FROM 'medicines.csv'")
```

**Great Expectations:** Write one expectation (e.g., "medicine_id is not null"):
```python
data.expect_column_values_to_not_be_null('medicine_id')
```

---

## Why These Tools Matter

1. **They're free** — no budget needed, no licensing headaches.
2. **They're used in production** — learning them teaches real-world practices.
3. **They scale** — you'll outgrow them eventually, but they teach the concepts that apply everywhere.
4. **They're open-source** — you can read the code, contribute, and understand how they work under the hood.

---

## Recommended Reading

- [dbt Documentation](https://docs.getdbt.com/) — start with "Getting started"
- [DuckDB Introduction](https://duckdb.org/docs/guides/) — 5-minute setup
- [Great Expectations Tutorial](https://docs.greatexpectations.io/docs/guides/validation/getting_started/) — hands-on validation
- [Apache Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/concepts/) — understand DAGs before coding

---

## Questions to Ask Yourself

- **Can I draw my pipeline?** → Use draw.io
- **Can I query my data in SQL?** → Use DuckDB
- **Can I express data quality as rules?** → Use Great Expectations
- **Can I automate running my pipeline on a schedule?** → Use Airflow

Master these tools in order, and you'll have a solid foundation in data engineering.

---

**Last updated:** August 2026  
**Next review:** After Week 2 intern cohort feedback
