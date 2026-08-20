# NHS Secondary Care Medicines Data (SCMD)
## Week 3: Load & Orchestrate — Bootcamp Project Spec

---

## Continuity Notice (Read First)

This spec assumes you completed Week 2 and produced `data/processed/scmd_202605_processed.parquet`
(311,072 rows, 11 columns, per `docs/Week2_Transformation_Report.md`). Week 3 does **not** re-clean
the data — it takes your Week 2 output as a trusted input and loads it into a real database.

**Known issue you must resolve before starting (Task 3.0 below):** the Week 2 spec's own code
samples (`src/transform.py`, Task 2.2) reference the column as `TOTAL_QUANITY_IN_VMP_UNIT`
(missing the "T" in "QUANTITY") in every function body, while the *actual* NHSBSA SCMD field —
and the Week 2 spec's own Part B description — spell it `TOTAL_QUANTITY_IN_VMP_UNIT` (correct).
If you copy-pasted the Task 2.2 code as written, one of two things happened: (a) your script
raised a `KeyError` against the real CSV and you already fixed the spelling, or (b) you renamed
the incoming column to match the typo so the script would run. Either is a plausible fix, but
they leave different column names in your Parquet file — and Week 3's schema below is written
against the **correct** spelling. Task 3.0 has you verify and reconcile this before building
anything else on top of it, so it doesn't become a silent, cohort-wide inconsistency.

*(Verified against an independent description of the SCMD schema; not verified directly against
the NHSBSA API response for this specific resource — confidence ~85%. If your raw CSV headers
say otherwise, trust your CSV over this note and document the discrepancy.)*

---

## Part A: Learning Objectives

By the end of Week 3, you will be able to:

### Knowledge
- ✅ Explain why analytical workloads use dimensional modeling (star schema: fact + dimension tables) instead of one wide flat table
- ✅ Define idempotency precisely: what "safe to run twice" means for a load step, and why it matters more than almost anything else in production pipelines
- ✅ Compare SQLite vs. PostgreSQL vs. a cloud warehouse (BigQuery) on setup cost, concurrency, and when each stops being "good enough"
- ✅ Explain what an orchestrator (cron, Airflow, Prefect) actually adds over a manual script — and when you don't need one yet
- ✅ Describe what a data quality "circuit breaker" is and why silently loading bad data is worse than a pipeline that stops

### Skills
- ✅ Design a star schema (grain, fact table, dimension tables, keys) from a flat Parquet file
- ✅ Write idempotent load logic in Python + SQL (upsert / delete-and-insert-by-partition), not naive `INSERT`
- ✅ Load data into SQLite using the standard library (`sqlite3`) or SQLAlchemy
- ✅ Extend `src/pipeline.py` with a fourth stage (Load) and prove the whole E-T-L-M flow reruns safely
- ✅ Write a data-quality gate that halts the pipeline (not just logs a warning) on row-count drift or broken referential integrity
- ✅ Schedule the pipeline with cron (or Task Scheduler on Windows) and produce evidence it ran unattended

### Mindset
- ✅ **Idempotency as a safety net:** what happens if this runs twice? At 3am? On a laptop that loses power mid-write?
- ✅ **Boring technology first:** earn the right to add Airflow — don't reach for it before cron has failed you
- ✅ **Referential integrity is a promise:** every downstream query trusts that a fact row's keys resolve to real dimension rows
- ✅ **Verify upstream assumptions:** Task 3.0 exists because "the Week 2 doc says X" is not the same as "my file actually has X"

---

## Part B: The Loading Challenge

### Week 2 Output → Week 3 Input

```
data/processed/scmd_202605_processed.parquet (311,072 rows, 11 columns)
├── Original columns (cleaned/typed): YEAR_MONTH, ODS_CODE, VMP_SNOMED_CODE,
│   VMP_PRODUCT_NAME, UNIT_OF_MEASURE_IDENTIFIER, UNIT_OF_MEASURE_NAME,
│   TOTAL_QUANTITY_IN_VMP_UNIT, INDICATIVE_COST
├── Derived columns (from Week 2): cost_per_unit, cost_category, year, month
├── Dedup key: YEAR_MONTH + ODS_CODE + VMP_SNOMED_CODE (one row per Trust per
│   Medicine per Month — this is your grain)
└── Quality gates already passed: no nulls, no negative cost/quantity, no
    duplicate keys (per Week 2 validation)
```

### Week 3 Output: An Operational, Queryable Database

```
data/warehouse/scmd.db (SQLite)
├── dim_trust        (ods_code PK, organisation_name, trust_region)
├── dim_medicine      (vmp_snomed_code PK, vmp_product_name, unit_of_measure_name)
├── dim_date          (year_month PK, year, month)
├── fact_medicines_issued (year_month FK, ods_code FK, vmp_snomed_code FK,
│                          total_quantity, indicative_cost, cost_per_unit,
│                          cost_category, PRIMARY KEY on the three FKs)
│
├── Loaded via idempotent logic — rerunning for the same month changes
│   nothing (upsert), rerunning for a new month adds rows only
├── Quality gate passed before commit: row counts reconcile against the
│   Parquet source, and every fact row's keys resolve to a dimension row
└── Reachable by SQL for Week 4 analysis
```

### Data Flow (Week 3 Focus)

```
Parquet (data/processed/scmd_202605_processed.parquet)
   ↓
[Task 3.0] Verify Week 2 → Week 3 continuity (schema check)
   ↓
[Task 3.1] Design the star schema (docs/Week3_Schema_Design.md)
   ↓
[Task 3.2] Build src/load.py — idempotent dimension + fact loads
   ↓
[Task 3.3] Extend src/pipeline.py with a Load stage; schedule via cron
   ↓
[Task 3.4] Add a quality gate that halts on drift or broken FKs
   ↓
[Task 3.5] Document: ERD, updated runbook, Week 3 report
   ↓
data/warehouse/scmd.db ✓ — ready for Week 4 SQL & reporting
```

---

## Required Viewing (Watch in This Order, Before Task 3.1)

Three videos have been assigned for Week 3. Watch them **in this sequence** — each one hands off
to the next, moving from broad context, to re-familiarizing yourself with the data, to the
architecture pattern you'll actually implement this week. You will present your key takeaways
from all three (tied to what you actually built) at the **Week 4** showcase — see Part F.

*(Titles and channel confirmed via YouTube; I was rate-limited fetching full descriptions, so the
sequencing below is reasoned from title and topic fit, not a verified watch-through — sanity-check
the order yourselves once you've seen them, and flag it if a video doesn't match its slot.)*

1. **[NHS SCMD Masterclass](https://youtu.be/SQFyvJVeHlI)** — start here. It's the broadest of the
   three and re-grounds you in the dataset and pipeline end to end before you narrow in on Week 3's
   slice of it (loading + orchestration). Treat it as a refresher, not new material — if something
   contradicts your Week 1/2 docs, that's worth raising, not silently adopting.

2. **[Explorer's Guide to SCMD Data — Best Practices: Reading & Exploring SCMD Datasets](https://youtu.be/BNUYEAspA4s)**
   — watch this before Task 3.1 (schema design). Re-examining how the data is shaped and read is
   the direct input to deciding your grain, your dimension tables, and your keys — don't design
   the star schema from memory of Week 1/2 alone.

3. **[Architecting Eventual Consistency: Ingesting the SCMD](https://youtu.be/1nAjxQC1lvc)** —
   watch this immediately before Task 3.2 (idempotent load logic). It's the most directly
   applicable of the three: "eventual consistency" and "ingestion architecture" are exactly the
   concepts behind idempotent loads and the delete-and-insert-by-partition pattern used below. As
   you build `src/load.py`, note anywhere the video's approach differs from this spec's (e.g. a
   different idempotency pattern, a different consistency model) — that's a legitimate design
   choice to compare in your Week 3 report, not something to treat as "the video is right."

---

## Part C: Week 3 Tasks (Step-by-Step)

### Task 3.0: Verify Week 2 → Week 3 Continuity (30 min)

**Goal:** Confirm your actual Week 2 output matches what Week 3 expects, before you build on it.

#### Steps:
1. **Reload your own Parquet file and print its real schema**
   ```python
   import pandas as pd
   df = pd.read_parquet('data/processed/scmd_202605_processed.parquet')
   print(df.columns.tolist())
   print(df.dtypes)
   print(len(df))
   ```
2. **Reconcile the `TOTAL_QUANTITY_IN_VMP_UNIT` naming**
   - Does your file have `TOTAL_QUANTITY_IN_VMP_UNIT` (correct) or `TOTAL_QUANITY_IN_VMP_UNIT`
     (the typo from the Week 2 Task 2.2 code sample)? Either is possible depending on how you
     resolved the original `KeyError`.
   - **Standardize on the correct spelling (`TOTAL_QUANTITY_IN_VMP_UNIT`) going forward.** If
     your file has the typo, rename the column (`df.rename(columns={...})`) and re-save the
     Parquet — don't carry a typo into your database schema.
   - Add one line to `docs/Week3_Schema_Design.md` (Task 3.1) noting which case you were in and
     what you changed. Future-you (and the instructor reviewing your PR) needs this documented.
3. **Confirm row count and key uniqueness still hold**
   ```python
   key = ['YEAR_MONTH', 'ODS_CODE', 'VMP_SNOMED_CODE']
   assert df.duplicated(subset=key).sum() == 0, "Dedup key is no longer unique"
   print(f"Rows: {len(df):,} — should match your Week 2 report's final count")
   ```
4. **If your numbers don't match your Week 2 report**, stop and figure out why before continuing
   — don't build a database on top of data you can't currently explain.

#### Deliverable:
- One paragraph at the top of `docs/Week3_Schema_Design.md` recording your actual column names,
  row count, and any renames you made.

#### Success Criteria:
✅ You know exactly what's in your Parquet file — not what a spec document says should be in it
✅ Any naming mismatch is fixed once, at the source, and documented — not patched around in every
   downstream script

---

### Task 3.1: Design Your Database Schema (1.5 hours)

**Goal:** Design a star schema before writing load code.

#### Steps:
1. **State the grain explicitly**
   - One row in the fact table = one Trust, one Medicine, one Month. Write this sentence down —
     every schema decision should be checked against it.

2. **Design your dimension tables**
   ```
   dim_trust
   ├── ods_code (PK, string)          -- from ODS_CODE
   ├── organisation_name (string)      -- if you have it; else defer to Week 4
   └── trust_region (string, nullable) -- carried over from Week 2 if you built it

   dim_medicine
   ├── vmp_snomed_code (PK, string)    -- from VMP_SNOMED_CODE
   ├── vmp_product_name (string)
   └── unit_of_measure_name (string)

   dim_date
   ├── year_month (PK, string, e.g. "202605")
   ├── year (int)
   └── month (int)
   ```

3. **Design your fact table**
   ```
   fact_medicines_issued
   ├── year_month (FK -> dim_date.year_month)
   ├── ods_code (FK -> dim_trust.ods_code)
   ├── vmp_snomed_code (FK -> dim_medicine.vmp_snomed_code)
   ├── total_quantity (float)          -- from TOTAL_QUANTITY_IN_VMP_UNIT
   ├── indicative_cost (float)
   ├── cost_per_unit (float)           -- carried from Week 2
   ├── cost_category (string)          -- carried from Week 2
   └── PRIMARY KEY (year_month, ods_code, vmp_snomed_code)
   ```

4. **Draw an ERD** (Mermaid, draw.io, or ASCII — see `data_engineering_tools_guide.md`)

5. **Choose your database engine and justify it**
   - **Default recommendation: SQLite.** Zero setup, single file, matches the README's "no heavy
     infrastructure needed" principle, and is enough for one laptop's worth of monthly data.
   - **PostgreSQL** is a reasonable stretch goal if you want shared/concurrent access (e.g. a
     teammate querying while you load), but adds a server to manage — don't take this on unless
     you have a concrete reason.
   - **BigQuery** is out of scope for Week 3 unless you specifically want cloud-warehouse
     experience; flag it to your instructor rather than defaulting to it silently.

#### Deliverable:
- `docs/Week3_Schema_Design.md`: grain statement, ERD, table definitions (column, type, key),
  and your engine choice with a one-paragraph justification

#### Success Criteria:
✅ Grain is stated in one sentence and every table respects it
✅ Every foreign key in the fact table has a corresponding dimension table
✅ A peer can read the ERD and know how to write a `JOIN` without asking you

---

### Task 3.2: Build Idempotent Load Logic (3 hours)

**Goal:** Write load code that is safe to run twice, ten times, or after a crash mid-write.

#### Steps:

1. **Create `src/load.py`**
   ```python
   import sqlite3
   import pandas as pd
   from pathlib import Path


   def get_connection(db_path: str = 'data/warehouse/scmd.db') -> sqlite3.Connection:
       """Open (and create, if needed) the SQLite warehouse."""
       Path(db_path).parent.mkdir(parents=True, exist_ok=True)
       conn = sqlite3.connect(db_path)
       conn.execute("PRAGMA foreign_keys = ON")
       return conn


   def create_schema(conn: sqlite3.Connection) -> None:
       """Create tables if they don't already exist (idempotent DDL)."""
       conn.executescript("""
           CREATE TABLE IF NOT EXISTS dim_trust (
               ods_code TEXT PRIMARY KEY,
               organisation_name TEXT,
               trust_region TEXT
           );

           CREATE TABLE IF NOT EXISTS dim_medicine (
               vmp_snomed_code TEXT PRIMARY KEY,
               vmp_product_name TEXT,
               unit_of_measure_name TEXT
           );

           CREATE TABLE IF NOT EXISTS dim_date (
               year_month TEXT PRIMARY KEY,
               year INTEGER,
               month INTEGER
           );

           CREATE TABLE IF NOT EXISTS fact_medicines_issued (
               year_month TEXT NOT NULL REFERENCES dim_date(year_month),
               ods_code TEXT NOT NULL REFERENCES dim_trust(ods_code),
               vmp_snomed_code TEXT NOT NULL REFERENCES dim_medicine(vmp_snomed_code),
               total_quantity REAL,
               indicative_cost REAL,
               cost_per_unit REAL,
               cost_category TEXT,
               PRIMARY KEY (year_month, ods_code, vmp_snomed_code)
           );
       """)
       conn.commit()


   def load_dimensions(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
       """Upsert dimension rows. Safe to call on every run."""
       trusts = df[['ODS_CODE']].drop_duplicates().rename(columns={'ODS_CODE': 'ods_code'})
       medicines = df[['VMP_SNOMED_CODE', 'VMP_PRODUCT_NAME', 'UNIT_OF_MEASURE_NAME']] \
           .drop_duplicates() \
           .rename(columns={
               'VMP_SNOMED_CODE': 'vmp_snomed_code',
               'VMP_PRODUCT_NAME': 'vmp_product_name',
               'UNIT_OF_MEASURE_NAME': 'unit_of_measure_name',
           })
       dates = df[['YEAR_MONTH', 'year', 'month']].drop_duplicates() \
           .rename(columns={'YEAR_MONTH': 'year_month'})

       cur = conn.cursor()
       cur.executemany(
           "INSERT INTO dim_trust (ods_code) VALUES (?) "
           "ON CONFLICT(ods_code) DO NOTHING",
           trusts[['ods_code']].values.tolist(),
       )
       cur.executemany(
           "INSERT INTO dim_medicine (vmp_snomed_code, vmp_product_name, unit_of_measure_name) "
           "VALUES (?, ?, ?) "
           "ON CONFLICT(vmp_snomed_code) DO UPDATE SET "
           "vmp_product_name = excluded.vmp_product_name, "
           "unit_of_measure_name = excluded.unit_of_measure_name",
           medicines.values.tolist(),
       )
       cur.executemany(
           "INSERT INTO dim_date (year_month, year, month) VALUES (?, ?, ?) "
           "ON CONFLICT(year_month) DO NOTHING",
           dates.values.tolist(),
       )
       conn.commit()


   def load_fact(conn: sqlite3.Connection, df: pd.DataFrame, year_month: str) -> int:
       """
       Idempotent fact load for one month: delete any existing rows for this
       year_month, then insert the current set. This is the "delete-and-insert
       by partition" pattern — simpler and safer than row-by-row upsert when
       the whole month is reloaded from a single Parquet file.
       """
       cur = conn.cursor()

       # Idempotency: clear this partition before reloading it, inside a transaction.
       cur.execute("DELETE FROM fact_medicines_issued WHERE year_month = ?", (year_month,))

       rows = df[[
           'YEAR_MONTH', 'ODS_CODE', 'VMP_SNOMED_CODE',
           'TOTAL_QUANTITY_IN_VMP_UNIT', 'INDICATIVE_COST',
           'cost_per_unit', 'cost_category',
       ]].values.tolist()

       cur.executemany(
           "INSERT INTO fact_medicines_issued "
           "(year_month, ods_code, vmp_snomed_code, total_quantity, "
           " indicative_cost, cost_per_unit, cost_category) "
           "VALUES (?, ?, ?, ?, ?, ?, ?)",
           rows,
       )
       conn.commit()
       return cur.rowcount


   def load_scmd_to_db(parquet_path: str, db_path: str = 'data/warehouse/scmd.db') -> int:
       """Orchestrate the full load: schema, dimensions, then fact (in that order)."""
       df = pd.read_parquet(parquet_path)
       year_month = str(df['YEAR_MONTH'].iloc[0])

       conn = get_connection(db_path)
       try:
           create_schema(conn)
           load_dimensions(conn, df)          # dimensions before fact — FK integrity
           n = load_fact(conn, df, year_month)
           print(f"Loaded {n:,} fact rows for {year_month}")
           return n
       finally:
           conn.close()


   if __name__ == "__main__":
       load_scmd_to_db("data/processed/scmd_202605_processed.parquet")
   ```

2. **Why delete-and-insert-by-partition, not row-by-row upsert, for the fact table?**
   Your fact grain is a full month's snapshot from a single Parquet file — there's no case where
   you'd want *some* of a month's rows from an old run mixed with *some* from a new run. Deleting
   the partition and reinserting it atomically (inside one transaction) is simpler to reason about
   than per-row `ON CONFLICT` logic, and just as idempotent. Document this choice — it's a real
   trade-off, not the only correct answer (a row-by-row upsert would also work and generalizes
   better if you ever load partial-month updates).

3. **Prove idempotency**
   ```python
   from src.load import load_scmd_to_db, get_connection

   n1 = load_scmd_to_db("data/processed/scmd_202605_processed.parquet")
   n2 = load_scmd_to_db("data/processed/scmd_202605_processed.parquet")
   assert n1 == n2, "Row count changed on rerun — load is not idempotent"

   conn = get_connection()
   total = conn.execute("SELECT COUNT(*) FROM fact_medicines_issued").fetchone()[0]
   assert total == n1, "Table has more rows than one load's worth — duplicates leaked in"
   print(f"✅ Idempotency confirmed: {total:,} rows after two runs")
   ```

#### Deliverable:
- `src/load.py` with `create_schema`, `load_dimensions`, `load_fact`, `load_scmd_to_db`
- `data/warehouse/scmd.db` populated from your Week 2 Parquet
- Console evidence (or a short test) that running the load twice does not change row counts

#### Success Criteria:
✅ Running the load script twice in a row produces identical row counts
✅ Dimensions are loaded before the fact table (no FK violations)
✅ You can explain, in one sentence, why your chosen pattern (delete-and-insert vs. per-row
   upsert) is idempotent
✅ `PRAGMA foreign_keys = ON` is set and a deliberately bad fact row (unknown `ods_code`) is
   rejected, not silently inserted

---

### Task 3.3: Extend the Pipeline & Schedule It (1.5 hours)

**Goal:** Add Load as a fourth stage to your existing `src/pipeline.py`, then prove it can run
unattended.

#### Steps:

1. **Add a Load step to `src/pipeline.py`** (built in Week 2 Task 2.5 — extend it, don't rewrite it)
   ```python
   from src.load import load_scmd_to_db

   # ... inside run_pipeline(), after the existing Transform + Validate steps:

   log.info("Step 4: Loading (into warehouse)...")
   n_loaded = load_scmd_to_db(str(output_file))
   log.info(f"✓ Loaded {n_loaded:,} rows into data/warehouse/scmd.db")
   ```

2. **Rerun the full pipeline twice and confirm idempotency end to end**
   ```bash
   python src/pipeline.py --year 2026 --month 5
   python src/pipeline.py --year 2026 --month 5
   # Row counts in scmd.db should be identical after both runs
   ```

3. **Schedule it — cron is the default, Airflow is optional**
   The README's tech-stack table recommends cron for Weeks 2–3, and the project's "no heavy
   infrastructure" principle still applies: don't reach for Airflow just because it's the
   "proper" orchestration tool. Earn that complexity only if cron becomes genuinely limiting
   (e.g. you need retries with backoff, cross-pipeline dependencies, or a UI for a non-technical
   stakeholder).

   **Baseline (required): cron**
   ```bash
   # Run on the 15th of each month at 2am, log output, alert on failure
   0 2 15 * * cd /path/to/repo && python src/pipeline.py --month $(date +%m) --year $(date +%Y) >> logs/pipeline.log 2>&1
   ```
   - Add this to your crontab (`crontab -e`) or, on Windows, a Task Scheduler task running the
     equivalent command.
   - **Evidence required:** either let it fire once and show the log, or run
     `python src/pipeline.py --month 5` manually and treat the log file + exit code as your proof
     the automation *would* work unattended.

   **Stretch (optional): a minimal Airflow DAG**, if you want the exposure:
   ```python
   from airflow import DAG
   from airflow.operators.python import PythonOperator
   from datetime import datetime
   from src.pipeline import run_pipeline

   dag = DAG('scmd_pipeline', start_date=datetime(2026, 1, 1), schedule='@monthly', catchup=False)

   run_task = PythonOperator(
       task_id='run_scmd_pipeline',
       python_callable=lambda: run_pipeline(year=2026, month=5),
       dag=dag,
   )
   ```
   Note in your report which path you took and why — "I used cron because a single monthly
   job doesn't need a scheduler with a UI" is a perfectly good, defensible answer.

#### Deliverable:
- Updated `src/pipeline.py` with a Load stage (4 stages: Extract → Transform → Validate → Load)
- A cron entry (or Task Scheduler equivalent) — pasted into your runbook, not just "set up locally"
- Evidence the pipeline can be rerun without manual cleanup first

#### Success Criteria:
✅ `python src/pipeline.py --month 5` run twice leaves the database in an identical state
✅ The schedule is documented precisely enough that someone else could recreate it
✅ You can justify cron-vs-Airflow in one sentence tied to your actual workload, not "because
   it's more advanced"

---

### Task 3.4: Add a Data Quality Gate (1 hour)

**Goal:** Make the pipeline refuse to load data it can't vouch for, instead of loading it anyway
and hoping someone notices later.

#### Steps:

1. **Add gate checks before the load commits** — extend `src/validate.py` (or create `src/monitor.py`)
   ```python
   def check_row_count_drift(parquet_path: str, expected_min: int = 280_000) -> bool:
       """Halt if the source file looks suspiciously small (silent data loss upstream)."""
       import pandas as pd
       n = len(pd.read_parquet(parquet_path))
       if n < expected_min:
           print(f"❌ Row count gate FAILED: {n:,} rows (expected >= {expected_min:,})")
           return False
       print(f"✅ Row count gate passed: {n:,} rows")
       return True


   def check_referential_integrity(conn) -> bool:
       """Halt if any fact row references a trust/medicine/date not in the dimensions."""
       orphans = conn.execute("""
           SELECT COUNT(*) FROM fact_medicines_issued f
           LEFT JOIN dim_trust t ON f.ods_code = t.ods_code
           LEFT JOIN dim_medicine m ON f.vmp_snomed_code = m.vmp_snomed_code
           LEFT JOIN dim_date d ON f.year_month = d.year_month
           WHERE t.ods_code IS NULL OR m.vmp_snomed_code IS NULL OR d.year_month IS NULL
       """).fetchone()[0]
       if orphans > 0:
           print(f"❌ Referential integrity gate FAILED: {orphans:,} orphaned fact rows")
           return False
       print("✅ Referential integrity gate passed")
       return True
   ```

2. **Wire the gates into `run_pipeline()` so a failure stops the run**
   ```python
   if not check_row_count_drift(str(output_file)):
       raise ValueError("Row count gate failed; aborting load")

   n_loaded = load_scmd_to_db(str(output_file))

   conn = get_connection()
   if not check_referential_integrity(conn):
       raise ValueError("Referential integrity gate failed after load")
   ```

3. **Decide (and document) what "alert" means at your current scale**
   You don't need Slack/PagerDuty integration for a monthly student pipeline. A non-zero exit
   code plus a clearly formatted log line, captured by cron's `>> logs/pipeline.log 2>&1`, is a
   legitimate answer for Week 3. Write one paragraph in your report describing how you'd upgrade
   this to a real alert (e.g. a webhook call in the `except` block) if this were a production
   system — you don't have to build it, just show you know the next step.

#### Deliverable:
- Quality gate functions wired into `run_pipeline()` so a failure halts before/after load
- One deliberately-broken test run (e.g. truncate a test Parquet to 10 rows) showing the gate
  actually stops the pipeline, with console output as evidence

#### Success Criteria:
✅ A bad run does not silently produce a bad database — it stops with a clear error
✅ At least one gate checks the *output* (referential integrity), not just the input
✅ You've documented, in words, how this would become a real alert at production scale

---

### Task 3.5: Document Everything (1 hour)

**Goal:** Leave the pipeline in a state where someone who wasn't here can run it, trust it, and
extend it.

#### Steps:

1. **Create `docs/Week3_Load_Report.md`**, mirroring the structure of `docs/Week2_Transformation_Report.md`:
   - Summary: rows loaded, engine chosen, idempotency test result
   - Schema: link to `docs/Week3_Schema_Design.md`
   - Key decisions & trade-offs (SQLite vs. Postgres; delete-and-insert vs. row upsert; cron vs.
     Airflow) — same "Question / Options / Choice / Reasoning / Impact" format used in Week 2
   - Quality gate results (before/after counts, what the referential integrity check caught, if
     anything)
   - Task 3.0 reconciliation note (what your actual Week 2 column names were, what you fixed)

2. **Update `docs/Pipeline_Runbook.md`** (from Week 2) to add:
   - The Load step (what it does, expected time, expected row counts)
   - The cron schedule (exact crontab line, log location)
   - A new "Common Issues" entry: *"Foreign key constraint failed"* → dimensions weren't loaded
     before the fact table, or a Week 2 rerun changed a dimension value without updating history

3. **Update `docs/Architecture.md`** (from Week 1) with one paragraph: the database now exists,
   here's where it lives, here's how it's reached.

#### Deliverable:
- `docs/Week3_Load_Report.md`
- Updated `docs/Pipeline_Runbook.md` and `docs/Architecture.md`

#### Success Criteria:
✅ Someone new to the project can read your Week 3 report and reconstruct your reasoning
✅ The runbook's troubleshooting section reflects real errors you actually hit, not hypothetical
   ones
✅ Trade-offs are stated as trade-offs — "I chose X, which costs us Y, because Z" — not presented
   as the only option

---

## Part D: Week 3 Checklist & Deliverables

### By end of Week 3, you have:

- [ ] **Required Viewing:** Watched all three assigned videos, in sequence, and taken notes tying
      each one to what you actually built (for your Week 4 presentation)
- [ ] **Task 3.0:** Verified your actual Week 2 Parquet schema and reconciled the
      `TOTAL_QUANTITY_IN_VMP_UNIT` naming, documented in `docs/Week3_Schema_Design.md`
- [ ] **Task 3.1:** `docs/Week3_Schema_Design.md` with grain statement, ERD, and engine choice
- [ ] **Task 3.2:** Working `src/load.py` with idempotent dimension + fact loads
- [ ] **Task 3.2:** `data/warehouse/scmd.db` populated, idempotency proven (rerun test)
- [ ] **Task 3.3:** `src/pipeline.py` extended with a Load stage (4-stage E-T-L-M pipeline)
- [ ] **Task 3.3:** A cron entry (or Task Scheduler task) documented in the runbook
- [ ] **Task 3.4:** Quality gates wired into the pipeline; failure demo shows they actually halt it
- [ ] **Task 3.5:** `docs/Week3_Load_Report.md`, updated `Pipeline_Runbook.md` and `Architecture.md`
- [ ] **Code:** All new code committed to Git with clear messages, on a branch, reviewed via PR
- [ ] **Continuity:** No column-naming inconsistency carried forward silently from Week 2

### Estimated Time Investment:
- Task 3.0: 0.5 hour
- Task 3.1: 1.5 hours
- Task 3.2: 3 hours
- Task 3.3: 1.5 hours
- Task 3.4: 1 hour
- Task 3.5: 1 hour
- **Total: ~8.5 hours** (spread across the week)

---

## Part E: Week 3 Success Criteria (Rubric)

| Criterion | Expectation | Self-Check |
|-----------|-------------|-----------|
| **Continuity** | Week 2 output is verified, not assumed; any naming issue is fixed once at the source and documented | ✓ |
| **Schema Design** | Star schema respects a clearly stated grain; every FK has a matching dimension | ✓ |
| **Idempotency** | Rerunning the load (or the whole pipeline) twice produces identical row counts | ✓ |
| **Pipeline** | Single command runs Extract → Transform → Validate → Load end to end | ✓ |
| **Scheduling** | A real, documented schedule (cron minimum) exists — not just "runs when I remember" | ✓ |
| **Quality Gates** | At least one gate checks output integrity and demonstrably halts on failure | ✓ |
| **Documentation** | Runbook and report reflect real decisions and real errors, not a hypothetical happy path | ✓ |
| **Version Control** | All code committed with meaningful messages; PR reviewed | ✓ |

Aim for **all criteria met** by end of Week 3.

---

## Part F: Week 4 Preview

Next week, you'll use your operational database to:

1. **Query:** Write SQL against your star schema to answer real business questions (top cost
   movers, trust benchmarking, utilization trends — see the example queries in the main README)
2. **Report:** Build 2–3 sample reports or a lightweight dashboard from those queries
3. **Present:** Communicate findings to a non-technical stakeholder — **including a short segment
   on the three Week 3 videos** (Required Viewing, above): what each one covered, where it agreed
   or disagreed with the approach in this spec, and how it shaped what you actually built. This
   isn't a book report — ground it in your own `src/load.py`, your schema decisions, and your
   idempotency test results.
4. **Reflect:** Document lessons learned across all four weeks

Your Week 3 foundation (a trustworthy, idempotent, documented database) is what makes Week 4
possible without spending the whole week fighting your own data.

---

## FAQ

**Q: My Week 2 Parquet file has `TOTAL_QUANITY_IN_VMP_UNIT` (the typo). Do I have to fix it?**
A: Yes — fix it at the source (rename the column, re-save the Parquet, or better, fix
`src/transform.py` and rerun Week 2's transform) rather than writing Week 3 code around the typo.
A misspelled column name that "works" because every downstream script also misspells it is a
trap for the next person (including future you) who writes correct code against it.

**Q: Why SQLite and not Postgres or BigQuery?**
A: SQLite needs zero setup and is more than enough for one laptop's worth of monthly SCMD data.
Move to Postgres when you have a concrete reason (concurrent writers, a shared server) — not by
default. This mirrors the README's "no heavy infrastructure needed" principle.

**Q: Why delete-and-insert instead of a row-by-row upsert for the fact table?**
A: Your fact table is loaded one full month at a time from a single Parquet snapshot — there's no
scenario where you want a mix of old and new rows for the same month. Delete-and-insert inside one
transaction is simpler to reason about and equally idempotent. A row-level upsert is the better
choice if you ever load partial updates within a month; document whichever you pick and why.

**Q: Do I need Airflow?**
A: Not for Week 3. Cron satisfies the orchestration requirement for a monthly batch job. Build
the Airflow DAG only as a stretch goal if you want the resume line and the learning — don't let it
eat the time budgeted for idempotency and quality gates, which matter more at this stage.

**Q: What counts as "monitoring" if I don't have Slack/PagerDuty set up?**
A: A pipeline that exits non-zero on failure, with a clear log line, captured by cron's output
redirection, is a legitimate monitoring baseline. Document in your report how you'd wire in a
real alert later — you don't need to build the integration this week.

**Q: What if my row counts don't match Week 2's report?**
A: Stop and investigate before loading. A quality gate that lets through data you can't currently
explain isn't a quality gate — it's a formality. This is exactly the failure mode Task 3.4 exists
to catch.

---

## Support & Questions

- **Schema design questions?** → Re-read your `docs/Week2_Transformation_Report.md`; your Week 2
  decisions (dedup key, derived fields) are the direct inputs to your Week 3 grain
- **Idempotency bugs?** → Check whether dimensions are loaded *before* the fact table, and whether
  your delete step and insert step are in the same transaction
- **Cron not firing?** → Check `crontab -l`, confirm the script's absolute paths (cron doesn't
  inherit your shell's working directory or virtualenv activation)
- **Foreign key errors?** → `PRAGMA foreign_keys = ON` must be set on every connection, and
  dimensions must exist before the fact row that references them is inserted
- **Confused about decisions?** → Re-read `docs/Week2_Transformation_Report.md` and this spec's
  Part B before asking — the answer is usually "what did Week 2 already decide?"

---

## Final Thought

> *"A pipeline that runs once by luck isn't a pipeline — it's a script. Idempotency is what turns
> a script into infrastructure."*

Build with that in mind. Your Week 4 self — and anyone who inherits this repo — will thank you.

---

**Last updated:** August 20, 2026
**Version:** 1.0
**Maintained by:** Venkat Potamsetti
