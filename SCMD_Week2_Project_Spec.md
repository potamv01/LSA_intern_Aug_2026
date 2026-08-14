# NHS Secondary Care Medicines Data (SCMD)
## Week 2: Data Transformation & Enrichment Bootcamp Project Spec

---

## Part A: Learning Objectives

By the end of Week 2, you will be able to:

### Knowledge
- ✅ Explain why data cleaning is non-negotiable in production pipelines
- ✅ Identify common data quality issues and their business impact
- ✅ Design a data transformation strategy (cleaning → enrichment → validation)
- ✅ Understand idempotency and why it matters for reliability

### Skills
- ✅ Write Python code to clean and transform data (handle nulls, duplicates, type conversions)
- ✅ Add derived/calculated fields to enrich raw data
- ✅ Write unit tests using pytest (test-driven development)
- ✅ Validate transformed data against business rules using assertions
- ✅ Store transformed data efficiently (Parquet or columnar format)
- ✅ Debug data transformation bugs using profiling and logging

### Mindset
- ✅ **Trust but verify:** Question every transformation, write tests
- ✅ **Fail fast:** Catch data issues early, before they reach downstream systems
- ✅ **Document decisions:** Explain why you're handling nulls one way vs. another
- ✅ **Iteration:** First pass gets it working; second pass gets it right

---

## Part B: The Transformation Challenge

### Week 1 Output → Week 2 Input

By now, you have:
```
data/raw/scmd_202605.csv (34 MB, 312k rows)
├── Columns: YEAR_MONTH, ODS_CODE, VMP_SNOMED_CODE, VMP_PRODUCT_NAME, 
│            UNIT_OF_MEASURE_IDENTIFIER, UNIT_OF_MEASURE_NAME, 
│            TOTAL_QUANTITY_IN_VMP_UNIT, INDICATIVE_COST
│
└── Known issues from Week 1 validation:
    ├── Null values in some columns
    ├── Potential duplicates
    ├── Cost anomalies (extreme values)
    ├── Type mismatches (strings vs. numbers)
    └── Missing or inconsistent SNOMED codes
```

### Week 2 Output: Clean, Enriched Data

Your goal: transform raw data into this:
```
data/processed/scmd_202605_processed.parquet
├── All nulls handled consistently
├── Duplicates removed (by Trust + Medicine + Month key)
├── Data types correct (costs are floats, quantities are ints, dates are dates)
├── New derived columns:
│   ├── cost_per_unit (Indicative_Cost / Quantity)
│   ├── cost_category (high/medium/low based on quartiles)
│   └── trust_region (mapped from ODS_CODE)
│
├── Quality gates passed:
│   ├── All required columns present
│   ├── No negative quantities or costs
│   ├── Row counts match expectations (no silent loss of data)
│   └── No duplicate rows by key
│
└── Ready for loading into a database or warehouse
```

### Data Transformation Pipeline (Week 2 Focus)

```
Raw CSV
   ↓
[Task 2.1] Extract & Load into Memory (pandas/duckdb)
   ↓
[Task 2.2] Clean & Normalize (nulls, types, ranges)
   ↓
[Task 2.3] Deduplicate & Validate
   ↓
[Task 2.4] Enrich (derive new columns, add business logic)
   ↓
[Task 2.5] Test & Store (unit tests + save to Parquet)
   ↓
data/processed/scmd_202605_processed.parquet ✓
```

---

## Part C: Week 2 Tasks (Step-by-Step)

### Task 2.1: Design Your Transformation Strategy (1 hour)

**Goal:** Before writing code, plan how you'll clean and enrich the data.

#### Steps:

1. **Review Week 1 findings**
   - Open `docs/Week1_DataQuality_Report.md`
   - List the top 5–10 data quality issues you found
   - For each issue, decide: **ignore, clean, or flag as error?**

   Example:
   ```
   Issue: 145 rows have null VMP_SNOMED_Code
   Decision: Remove these rows (can't identify medicine without SNOMED)
   Reason: SNOMED code is the unique identifier; nulls mean we don't know what drug it is
   Impact: Lose 0.05% of data, but maintain integrity
   
   Issue: Some costs are 0.00
   Decision: Keep (valid — some medicines are free under NHS)
   Reason: Not an error; reflects pricing reality
   Impact: Won't filter; will handle in analysis
   
   Issue: Quantity_Issued has decimal places (e.g., 2.5)
   Decision: Keep as float (some medicines dispensed in fractional units)
   Reason: Can't round without losing data
   Impact: Store as float, document in data dictionary
   ```

2. **Document your cleaning strategy**
   - Create `docs/Week2_Transformation_Strategy.md`
   - For each column, specify:
     - **Input type** (what Week 1 found it as)
     - **Output type** (what you'll convert it to)
     - **Cleaning rules** (how to handle nulls, outliers, etc.)
     - **Validation checks** (what "good" looks like)

   Example template:
   ```markdown
   ## Column: INDICATIVE_COST
   
   **Input:** String or float, range $0–$50,000+, some nulls
   **Output:** Float, range $0–$10,000 (outliers reviewed)
   **Cleaning:** 
     - Remove rows where cost is null AND quantity is also null (can't compute)
     - Keep rows where cost is null BUT quantity exists (will set cost=0)
     - Flag costs >$10,000 for manual review (potential data entry errors)
   **Validation:**
     - No negative costs
     - Cost per unit makes sense (not >$100 for aspirin)
     - Cost correlates with quantity (more units, higher total cost)
   ```

3. **Decide on derived fields**
   - What new columns will help analysts?
   - What can you compute from raw data?

   Ideas:
   - `cost_per_unit = INDICATIVE_COST / TOTAL_QUANTITY_IN_VMP_UNIT` (signal unusual pricing)
   - `cost_category = 'high'/'medium'/'low'` (quartile-based buckets)
   - `month_year = YEAR_MONTH` (easier to filter)
   - `trust_region` (if you can map ODS_CODE to NHS region)

#### Deliverable:
- `docs/Week2_Transformation_Strategy.md` (1–2 pages)
  - Cleaning decisions for each column
  - List of derived fields + formulas
  - Assumptions & trade-offs documented

#### Success Criteria:
✅ Another intern can read your strategy and understand why you're handling data the way you are  
✅ You've made explicit decisions (not just "clean everything")  
✅ Trade-offs are documented (e.g., "removing nulls loses 0.5% of data but maintains integrity")

---

### Task 2.2: Build Your Transformation Function (3 hours)

**Goal:** Write reusable, testable Python code to clean the data.

#### Steps:

1. **Create `src/transform.py`**
   ```python
   import pandas as pd
   import numpy as np
   from typing import Tuple
   
   def load_raw_scmd(filepath: str) -> pd.DataFrame:
       """Load raw SCMD CSV into memory."""
       df = pd.read_csv(filepath)
       print(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
       return df
   
   
   def clean_nulls(df: pd.DataFrame) -> pd.DataFrame:
       """Handle null values according to strategy."""
       # Document which nulls matter and which don't
       print(f"Nulls before cleaning:\n{df.isnull().sum()}")
       
       # Decision: Remove rows where BOTH cost AND quantity are null
       df = df.dropna(subset=['INDICATIVE_COST', 'TOTAL_QUANITY_IN_VMP_UNIT'], how='all')
       
       # Decision: Fill missing costs with 0 (if quantity exists)
       df['INDICATIVE_COST'] = df['INDICATIVE_COST'].fillna(0.0)
       
       # Decision: Remove rows with null VMP_PRODUCT_NAME (can't identify medicine)
       df = df.dropna(subset=['VMP_PRODUCT_NAME'])
       
       print(f"Nulls after cleaning:\n{df.isnull().sum()}")
       print(f"Rows after null handling: {len(df):,}")
       
       return df
   
   
   def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
       """Convert columns to correct types."""
       # Ensure numeric columns are truly numeric
       df['TOTAL_QUANITY_IN_VMP_UNIT'] = pd.to_numeric(
           df['TOTAL_QUANITY_IN_VMP_UNIT'], errors='coerce'
       )
       df['INDICATIVE_COST'] = pd.to_numeric(
           df['INDICATIVE_COST'], errors='coerce'
       )
       
       # Keep ODS_CODE as string (it's an identifier, not a number)
       df['ODS_CODE'] = df['ODS_CODE'].astype(str)
       
       print(f"Data types:\n{df.dtypes}")
       return df
   
   
   def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
       """Remove duplicate rows (by Trust + Medicine + Month key)."""
       key_cols = ['YEAR_MONTH', 'ODS_CODE', 'VMP_SNOMED_CODE']
       
       n_before = len(df)
       # Keep first occurrence of each key
       df = df.drop_duplicates(subset=key_cols, keep='first')
       n_after = len(df)
       
       print(f"Removed {n_before - n_after:,} duplicate rows ({100*(n_before-n_after)/n_before:.2f}%)")
       
       return df
   
   
   def add_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
       """Enrich data with calculated columns."""
       # Cost per unit (handles divide by zero)
       df['cost_per_unit'] = np.where(
           df['TOTAL_QUANITY_IN_VMP_UNIT'] > 0,
           df['INDICATIVE_COST'] / df['TOTAL_QUANITY_IN_VMP_UNIT'],
           0
       )
       
       # Cost category based on quartiles
       quartiles = df['INDICATIVE_COST'].quantile([0.25, 0.5, 0.75])
       df['cost_category'] = pd.cut(
           df['INDICATIVE_COST'],
           bins=[0, quartiles[0.25], quartiles[0.5], quartiles[0.75], float('inf')],
           labels=['low', 'medium', 'high', 'premium']
       )
       
       # Parse YEAR_MONTH into date columns (easier to filter)
       df['year'] = df['YEAR_MONTH'].astype(str).str[:4].astype(int)
       df['month'] = df['YEAR_MONTH'].astype(str).str[-2:].astype(int)
       
       return df
   
   
   def validate_transformed_data(df: pd.DataFrame) -> bool:
       """Quality checks on transformed data."""
       errors = []
       
       # Check 1: No negative values
       if (df['INDICATIVE_COST'] < 0).any():
           errors.append("Found negative costs")
       if (df['TOTAL_QUANITY_IN_VMP_UNIT'] < 0).any():
           errors.append("Found negative quantities")
       
       # Check 2: Required columns present
       required = ['ODS_CODE', 'VMP_PRODUCT_NAME', 'INDICATIVE_COST', 'TOTAL_QUANITY_IN_VMP_UNIT']
       missing = [col for col in required if col not in df.columns]
       if missing:
           errors.append(f"Missing columns: {missing}")
       
       # Check 3: No complete rows are missing
       if df.isnull().any().any():
           errors.append("Found null values after transformation")
       
       # Check 4: Row counts reasonable (no >50% data loss)
       if len(df) < 150000:  # Started with 312k, 150k is 50% threshold
           errors.append("Possible data loss (row count too low)")
       
       if errors:
           print("❌ Validation FAILED:")
           for error in errors:
               print(f"  - {error}")
           return False
       else:
           print("✅ All validation checks passed")
           return True
   
   
   def transform_scmd(input_path: str, output_path: str) -> pd.DataFrame:
       """Orchestrate the full transformation pipeline."""
       print("=" * 60)
       print("SCMD TRANSFORMATION PIPELINE")
       print("=" * 60)
       
       # Extract
       df = load_raw_scmd(input_path)
       print(f"\n1. Initial shape: {df.shape}")
       
       # Transform
       df = clean_nulls(df)
       df = fix_data_types(df)
       df = remove_duplicates(df)
       df = add_derived_fields(df)
       print(f"\n2. After transformation: {df.shape}")
       
       # Validate
       print("\n3. Running validation checks...")
       if not validate_transformed_data(df):
           raise ValueError("Validation failed; aborting save")
       
       # Save
       df.to_parquet(output_path, compression='snappy', index=False)
       print(f"\n4. Saved to {output_path}")
       
       return df
   
   
   if __name__ == "__main__":
       # Test with May 2026 data
       input_file = "data/raw/scmd_provisional_202605.csv"
       output_file = "data/processed/scmd_202605_processed.parquet"
       
       df = transform_scmd(input_file, output_file)
       print(f"\n✅ Transformation complete. Final shape: {df.shape}")
   ```

2. **Test it manually first**
   ```bash
   python src/transform.py
   # Watch for warnings/errors
   # Check output file was created
   ls -lh data/processed/scmd_202605_processed.parquet
   ```

3. **Explore the output**
   ```python
   import pandas as pd
   df = pd.read_parquet('data/processed/scmd_202605_processed.parquet')
   print(df.head(10))
   print(df.info())
   print(df['cost_per_unit'].describe())
   ```

#### Deliverable:
- `src/transform.py` with working `transform_scmd()` function
- `data/processed/scmd_202605_processed.parquet` (cleaned data)
- Console output showing step-by-step transformation (rows before/after, nulls, etc.)

#### Success Criteria:
✅ Script runs without errors  
✅ Output file is smaller/more efficient than raw CSV (Parquet compression)  
✅ Data types are correct (no strings where numbers should be)  
✅ Validation checks pass  
✅ You can explain every transformation decision to a peer

---

### Task 2.3: Write Unit Tests (2 hours)

**Goal:** Test that your transformations work correctly (test-driven development).

#### Steps:

1. **Create `tests/test_transform.py`**
   ```python
   import pytest
   import pandas as pd
   import numpy as np
   from src.transform import (
       clean_nulls, fix_data_types, remove_duplicates,
       add_derived_fields, validate_transformed_data
   )
   
   
   @pytest.fixture
   def sample_scmd_data():
       """Create a small sample of SCMD data for testing."""
       return pd.DataFrame({
           'YEAR_MONTH': ['202605', '202605', '202605'],
           'ODS_CODE': ['RA2', 'RA2', 'RTH'],
           'VMP_SNOMED_CODE': ['123', '123', '456'],
           'VMP_PRODUCT_NAME': ['Paracetamol 500mg', 'Paracetamol 500mg', 'Aspirin 100mg'],
           'UNIT_OF_MEASURE_IDENTIFIER': [428673006, 428673006, 428673006],
           'UNIT_OF_MEASURE_NAME': ['TABLET', 'TABLET', 'TABLET'],
           'TOTAL_QUANITY_IN_VMP_UNIT': [100.0, 50.0, 200.0],
           'INDICATIVE_COST': [10.0, 5.0, 15.0]
       })
   
   
   class TestCleanNulls:
       """Test null-handling logic."""
       
       def test_drops_rows_with_both_cost_and_quantity_null(self):
           """Rows where both cost AND quantity are null should be removed."""
           df = pd.DataFrame({
               'TOTAL_QUANITY_IN_VMP_UNIT': [100.0, np.nan, 50.0],
               'INDICATIVE_COST': [10.0, np.nan, 5.0],
               'VMP_PRODUCT_NAME': ['A', 'B', 'C']
           })
           
           result = clean_nulls(df)
           
           # Should have 2 rows (row 1 dropped)
           assert len(result) == 2
           assert result['VMP_PRODUCT_NAME'].tolist() == ['A', 'C']
       
       def test_keeps_rows_with_null_cost_but_valid_quantity(self):
           """Keep rows where quantity exists but cost is null (will fill with 0)."""
           df = pd.DataFrame({
               'TOTAL_QUANITY_IN_VMP_UNIT': [100.0, 50.0],
               'INDICATIVE_COST': [np.nan, 5.0],
               'VMP_PRODUCT_NAME': ['A', 'B']
           })
           
           result = clean_nulls(df)
           
           assert len(result) == 2
           assert result.iloc[0]['INDICATIVE_COST'] == 0.0
       
       def test_drops_rows_with_null_product_name(self):
           """Can't identify medicine without a name."""
           df = pd.DataFrame({
               'TOTAL_QUANITY_IN_VMP_UNIT': [100.0, 50.0],
               'INDICATIVE_COST': [10.0, 5.0],
               'VMP_PRODUCT_NAME': ['Paracetamol', np.nan]
           })
           
           result = clean_nulls(df)
           
           assert len(result) == 1
   
   
   class TestFixDataTypes:
       """Test type conversions."""
       
       def test_converts_quantity_to_numeric(self):
           """Quantity should be numeric, not string."""
           df = pd.DataFrame({
               'TOTAL_QUANITY_IN_VMP_UNIT': ['100', '50', '200']
           })
           
           result = fix_data_types(df)
           
           assert result['TOTAL_QUANITY_IN_VMP_UNIT'].dtype in ['int64', 'float64']
       
       def test_coerces_invalid_numbers_to_nan(self):
           """Invalid numbers should become NaN (not crash)."""
           df = pd.DataFrame({
               'TOTAL_QUANITY_IN_VMP_UNIT': ['100', 'invalid', '200']
           })
           
           result = fix_data_types(df)
           
           # Should have 2 valid + 1 NaN
           assert pd.isna(result.iloc[1]['TOTAL_QUANITY_IN_VMP_UNIT'])
   
   
   class TestRemoveDuplicates:
       """Test deduplication logic."""
       
       def test_removes_exact_duplicates(self):
           """Identical rows should be removed."""
           df = pd.DataFrame({
               'YEAR_MONTH': ['202605', '202605'],
               'ODS_CODE': ['RA2', 'RA2'],
               'VMP_SNOMED_CODE': ['123', '123'],
               'quantity': [100, 100],
               'cost': [10, 10]
           })
           
           result = remove_duplicates(df)
           
           assert len(result) == 1
       
       def test_keeps_rows_with_same_key_different_cost(self):
           """Different cost/quantity for same Trust+Medicine+Month = data issue, but keep first."""
           df = pd.DataFrame({
               'YEAR_MONTH': ['202605', '202605'],
               'ODS_CODE': ['RA2', 'RA2'],
               'VMP_SNOMED_CODE': ['123', '123'],
               'quantity': [100, 150],  # Different
               'cost': [10, 15]  # Different
           })
           
           result = remove_duplicates(df)
           
           # Keep first occurrence
           assert len(result) == 1
           assert result.iloc[0]['quantity'] == 100
   
   
   class TestAddDerivedFields:
       """Test derived column creation."""
       
       def test_calculates_cost_per_unit(self, sample_scmd_data):
           """Cost per unit = total cost / total quantity."""
           result = add_derived_fields(sample_scmd_data)
           
           # First row: 10 / 100 = 0.1
           assert result.iloc[0]['cost_per_unit'] == pytest.approx(0.1)
       
       def test_handles_divide_by_zero(self):
           """Cost per unit when quantity is 0 should be 0, not inf."""
           df = pd.DataFrame({
               'TOTAL_QUANITY_IN_VMP_UNIT': [0, 100],
               'INDICATIVE_COST': [10, 10]
           })
           
           result = add_derived_fields(df)
           
           assert result.iloc[0]['cost_per_unit'] == 0  # Not inf
           assert result.iloc[1]['cost_per_unit'] == pytest.approx(0.1)
       
       def test_creates_cost_category(self, sample_scmd_data):
           """Cost should be bucketed into categories."""
           result = add_derived_fields(sample_scmd_data)
           
           assert 'cost_category' in result.columns
           assert result['cost_category'].isnull().sum() == 0  # No nulls
   
   
   class TestValidation:
       """Test data quality checks."""
       
       def test_validation_fails_on_negative_cost(self):
           """Negative costs should fail validation."""
           df = pd.DataFrame({
               'INDICATIVE_COST': [-1.0, 10.0],
               'TOTAL_QUANITY_IN_VMP_UNIT': [100, 50],
               'ODS_CODE': ['A', 'B'],
               'VMP_PRODUCT_NAME': ['X', 'Y']
           })
           
           assert not validate_transformed_data(df)
       
       def test_validation_passes_on_clean_data(self, sample_scmd_data):
           """Clean data should pass all checks."""
           df = sample_scmd_data.copy()
           df = fix_data_types(df)
           
           assert validate_transformed_data(df)
   
   
   class TestEndToEnd:
       """Test the full pipeline with real data."""
       
       @pytest.mark.slow  # This test is slow (real file I/O)
       def test_full_transformation_pipeline(self):
           """Full pipeline should produce valid Parquet file."""
           from src.transform import transform_scmd
           import tempfile
           import os
           
           # Only run if sample data exists
           if not os.path.exists("data/raw/scmd_provisional_202605.csv"):
               pytest.skip("Sample data not available")
           
           with tempfile.NamedTemporaryFile(suffix='.parquet') as tmp:
               result = transform_scmd(
                   "data/raw/scmd_provisional_202605.csv",
                   tmp.name
               )
               
               # Checks
               assert len(result) > 100000  # Shouldn't lose >90% of data
               assert result.isnull().sum().sum() == 0  # No nulls
               assert (result['INDICATIVE_COST'] >= 0).all()  # No negatives
   ```

2. **Run the tests**
   ```bash
   pytest tests/test_transform.py -v
   
   # Expected output:
   # test_drops_rows_with_both_cost_and_quantity_null PASSED
   # test_keeps_rows_with_null_cost_but_valid_quantity PASSED
   # ... (more passing tests)
   ```

3. **Check test coverage**
   ```bash
   pytest tests/test_transform.py --cov=src --cov-report=term-missing
   
   # Aim for >80% coverage on critical functions
   ```

#### Deliverable:
- `tests/test_transform.py` with 10+ test cases
- All tests passing (`pytest tests/test_transform.py -v`)
- Coverage report showing >80% on `src/transform.py`

#### Success Criteria:
✅ All tests pass  
✅ Tests cover edge cases (nulls, zero division, type conversions)  
✅ You can add a new transformation, write tests first, then implement ("red-green-refactor")  
✅ Test names are descriptive (someone can read them and understand what's being tested)

---

### Task 2.4: Document Transformations & Trade-offs (1 hour)

**Goal:** Help future readers (and yourself in 3 months) understand what you did and why.

#### Steps:

1. **Create `docs/Week2_Transformation_Report.md`**
   ```markdown
   # Week 2: Transformation & Enrichment Report
   
   ## Summary
   
   Transformed 312,458 raw SCMD rows into 305,623 clean, enriched rows (2.2% data loss).
   All validation checks passed.
   
   ## Data Quality Improvements
   
   | Issue | Before | After | Action |
   |-------|--------|-------|--------|
   | Null values | 1,235 | 0 | Dropped rows with critical nulls; filled costs with 0 |
   | Duplicates | 1,105 | 0 | Removed 1,105 duplicate rows by key |
   | Negative costs | 12 | 0 | Removed (data entry errors) |
   | Type mismatches | 500+ | 0 | Converted strings to numbers; coerced errors to NaN |
   
   ## Transformation Pipeline
   
   ### Step 1: Clean Nulls (312,458 → 312,200 rows)
   - **Removed:** Rows where both cost AND quantity were null (258 rows)
   - **Filled:** Cost values where quantity existed (0 cost = no charge)
   - **Removed:** VMP_PRODUCT_NAME nulls (can't identify medicine) (0 rows; already caught)
   
   ### Step 2: Fix Data Types (312,200 → 312,200 rows)
   - TOTAL_QUANTITY_IN_VMP_UNIT: string → float
   - INDICATIVE_COST: string → float
   - ODS_CODE: kept as string (it's an identifier)
   - Coerced 23 invalid numbers to NaN (then dropped)
   
   ### Step 3: Remove Duplicates (312,177 → 311,072 rows)
   - Key: YEAR_MONTH + ODS_CODE + VMP_SNOMED_CODE
   - Removed 1,105 exact duplicates (kept first occurrence)
   - Reason: Same trust, same medicine, same month should appear once
   
   ### Step 4: Add Derived Fields (311,072 → 311,072 rows, +3 columns)
   - `cost_per_unit`: Indicative_Cost / Quantity (signal unusual pricing)
   - `cost_category`: Bucketed by quartiles (low/medium/high/premium)
   - `year`, `month`: Parsed from YEAR_MONTH (easier to filter)
   
   ### Step 5: Validate (311,072 rows)
   - ✅ No negative costs
   - ✅ No negative quantities
   - ✅ All required columns present
   - ✅ No remaining nulls
   - ✅ Row count reasonable (not >50% loss)
   
   ## Key Decisions & Trade-offs
   
   ### Decision 1: Null Handling
   **Question:** What do we do with rows missing cost or quantity?
   **Options:**
   - A) Drop all rows with any null
   - B) Fill nulls with 0 (assume no cost/quantity)
   - C) Drop only critical fields (product name, date)
   
   **Choice:** C (drop critical fields only; fill costs with 0)
   **Reasoning:** 
   - Dropping all nulls = lose too much data
   - Filling all nulls = assume no cost when data might be missing; risky
   - Selective dropping = keep data when we're confident; fill only costs (safe assumption)
   **Impact:** Lose <0.1% of rows; maintain data integrity
   
   ### Decision 2: Deduplication Key
   **Question:** What uniquely identifies a row?
   **Options:**
   - A) Each row is unique (no dedup)
   - B) Trust + Medicine + Month (one entry per trust per medicine per month)
   - C) Trust + Medicine + Unit Type (one entry per trust per medicine per unit)
   
   **Choice:** B
   **Reasoning:**
   - SCMD publishes data at Trust + Medicine + Month granularity
   - Duplicates at this level = data error or ETL bug
   - Deduping removes invalid data, keeps valid (first occurrence)
   **Impact:** Remove 0.35% of rows (1,105 duplicates); data now trustworthy
   
   ### Decision 3: Cost Anomalies
   **Question:** What about costs >$50,000 or <$0.01?
   **Options:**
   - A) Remove (might be errors)
   - B) Keep (might be legitimate outliers)
   - C) Flag & investigate (manual review)
   
   **Choice:** B (keep; document in metadata)
   **Reasoning:**
   - Biologics, gene therapies can cost >$50k per dose
   - NHS negotiates volume discounts; extreme values are possible
   - Removing "outliers" risks losing real data
   **Impact:** Keep 12 high-cost rows; future analysis can filter if needed
   
   ## Test Coverage
   
   - 15 unit tests covering transformation logic
   - 100% coverage on null-handling
   - 95% coverage on type conversion
   - 1 end-to-end test with real data
   - All tests passing ✅
   
   ## Output Files
   
   - `data/processed/scmd_202605_processed.parquet` (115 MB Parquet, down from 34 MB CSV)
   - Compression: Snappy (good balance of speed & size)
   - Rows: 311,072
   - Columns: 11 (original 8 + 3 derived)
   
   ## Next Steps (Week 3)
   
   - Load this Parquet into database (PostgreSQL or BigQuery)
   - Create fact tables (trusts, medicines, dates as separate tables)
   - Build materialized views for common queries
   - Add monitoring to alert on unexpected data changes
   ```

2. **Update `src/transform.py` with documentation**
   - Add comments explaining WHY, not WHAT
   - Example:
     ```python
     # Decision: Fill missing costs with 0 (not NaN, not -1)
     # Reasoning: Some NHS medicines are free; 0 cost is valid
     # Risk: Can't distinguish between "no cost" and "cost unknown"
     # Mitigation: Log warning when filling; flag rows in audit trail
     df['INDICATIVE_COST'] = df['INDICATIVE_COST'].fillna(0.0)
     ```

3. **Create a "Transformation Decision Log"**
   - Document every non-obvious choice
   - Future you will thank present you

#### Deliverable:
- `docs/Week2_Transformation_Report.md` (2–3 pages)
- Updated docstrings in `src/transform.py` (document the "why")
- Clear comments in code explaining decisions

#### Success Criteria:
✅ Report explains what was transformed and why  
✅ Trade-offs are documented (what we lost, what we gained)  
✅ Someone new to the project can read this and make decisions in Week 3/4  
✅ Code comments explain reasoning, not just functionality

---

### Task 2.5: Create a Transformation Runbook (1 hour)

**Goal:** Make it easy to re-run the transformation for new months of data.

#### Steps:

1. **Update `src/pipeline.py`** to call your transform
   ```python
   #!/usr/bin/env python3
   """
   Orchestrate the full SCMD ETL pipeline.
   
   Usage:
       python src/pipeline.py --month 202605
       python src/pipeline.py --month 202606 --input data/raw/ --output data/processed/
   """
   
   import argparse
   import logging
   from pathlib import Path
   from src.extract import download_scmd_data
   from src.transform import transform_scmd
   from src.validate import validate_scmd_data
   
   # Setup logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )
   log = logging.getLogger(__name__)
   
   
   def run_pipeline(year: int, month: int, input_dir: str = 'data/raw/', output_dir: str = 'data/processed/') -> bool:
       """Run the full E-T-L pipeline for a given month."""
       
       log.info(f"Starting pipeline for {year}-{month:02d}")
       
       try:
           # Extract
           log.info("Step 1: Extracting (downloading CSV)...")
           input_file = Path(input_dir) / f"scmd_{year}{month:02d}.csv"
           download_scmd_data(year=year, month=month, output_dir=input_dir)
           
           if not input_file.exists():
               raise FileNotFoundError(f"Download failed; file not found: {input_file}")
           log.info(f"✓ Downloaded {input_file.name}")
           
           # Transform
           log.info("Step 2: Transforming (cleaning & enriching)...")
           output_file = Path(output_dir) / f"scmd_{year}{month:02d}_processed.parquet"
           transform_scmd(str(input_file), str(output_file))
           log.info(f"✓ Transformed to {output_file.name}")
           
           # Validate
           log.info("Step 3: Validating (quality checks)...")
           if not validate_scmd_data(str(output_file)):
               raise ValueError("Validation failed")
           log.info("✓ Validation passed")
           
           log.info(f"✅ Pipeline complete for {year}-{month:02d}")
           return True
           
       except Exception as e:
           log.error(f"❌ Pipeline failed: {e}")
           return False
   
   
   if __name__ == "__main__":
       parser = argparse.ArgumentParser(description="Run SCMD ETL pipeline")
       parser.add_argument("--year", type=int, default=2026, help="Year (default: 2026)")
       parser.add_argument("--month", type=int, required=True, help="Month (1-12)")
       parser.add_argument("--input", default="data/raw/", help="Input directory")
       parser.add_argument("--output", default="data/processed/", help="Output directory")
       
       args = parser.parse_args()
       
       success = run_pipeline(args.year, args.month, args.input, args.output)
       exit(0 if success else 1)
   ```

2. **Test the pipeline**
   ```bash
   python src/pipeline.py --year 2026 --month 5
   # Should show: Step 1 → Step 2 → Step 3 → ✅ complete
   ```

3. **Create `docs/Pipeline_Runbook.md`**
   ```markdown
   # Pipeline Runbook
   
   ## Quick Start
   
   ```bash
   # Download + transform + validate SCMD May 2026
   python src/pipeline.py --year 2026 --month 5
   ```
   
   Output: `data/processed/scmd_202605_processed.parquet`
   
   ## Step-by-Step
   
   ### Step 1: Extract
   `src/extract.py --year 2026 --month 5`
   - Downloads CSV from NHSBSA portal
   - Saves to `data/raw/scmd_202605.csv`
   - **Expected time:** 30 sec – 2 min
   - **Expected file size:** 30–40 MB
   
   ### Step 2: Transform
   `src/transform.py data/raw/scmd_202605.csv data/processed/scmd_202605_processed.parquet`
   - Cleans nulls, fixes types, removes duplicates
   - Adds derived fields (cost_per_unit, cost_category, etc.)
   - Saves as Parquet
   - **Expected time:** 10–30 sec
   - **Expected output size:** 100–150 MB (compressed)
   
   ### Step 3: Validate
   `src/validate.py data/processed/scmd_202605_processed.parquet`
   - Runs quality checks
   - **Expected output:** "✅ All validations passed"
   
   ## Common Issues
   
   ### "Download failed: 404"
   - NHSBSA API might be down
   - Check: https://opendata.nhsbsa.net/
   - Solution: Try again in 5 min; manually download if needed
   
   ### "No space left on device"
   - Parquet file is large
   - Solution: `du -sh data/` to check disk usage; delete old months if needed
   
   ### "Validation failed: Missing column X"
   - SCMD schema changed (unlikely but possible)
   - Solution: Check NHSBSA docs; update column names
   
   ## Monitoring
   
   Each run logs to console. For automated runs (cron, Airflow):
   - Capture stdout/stderr
   - Alert on exit code != 0
   - Example cron:
     ```bash
     0 2 15 * * cd /app && python src/pipeline.py --month $(date +%m) --year $(date +%Y) 2>&1 | mail -s "SCMD Pipeline" admin@example.com
     ```
   
   ## Testing
   
   ```bash
   # Run all tests
   pytest tests/ -v
   
   # Run only transform tests
   pytest tests/test_transform.py -v
   
   # Run with coverage
   pytest --cov=src --cov-report=html
   ```
   ```

#### Deliverable:
- `src/pipeline.py` (orchestrates full E-T-L)
- `docs/Pipeline_Runbook.md` (how to run + troubleshoot)
- Tested end-to-end (pipeline runs successfully)

#### Success Criteria:
✅ Single command runs entire pipeline: `python src/pipeline.py --month 5`  
✅ Runbook explains each step and common issues  
✅ New team member can run the pipeline without asking for help  
✅ Logging is clear (shows progress + any warnings)

---

## Part D: Week 2 Checklist & Deliverables

### By end of Week 2, you have:

- [ ] **Task 2.1:** `docs/Week2_Transformation_Strategy.md` (cleaning decisions documented)
- [ ] **Task 2.2:** Working `src/transform.py` with all functions
- [ ] **Task 2.2:** `data/processed/scmd_202605_processed.parquet` (cleaned data file)
- [ ] **Task 2.3:** `tests/test_transform.py` with 10+ passing tests
- [ ] **Task 2.3:** >80% test coverage on `src/transform.py`
- [ ] **Task 2.4:** `docs/Week2_Transformation_Report.md` (what changed & why)
- [ ] **Task 2.5:** Updated `src/pipeline.py` (orchestrates E-T-L)
- [ ] **Task 2.5:** `docs/Pipeline_Runbook.md` (how to run)
- [ ] **Code:** All new code committed to Git with clear messages
- [ ] **Code review:** Peer reviewed by another intern (or instructor)

### Estimated Time Investment:
- Task 2.1: 1 hour
- Task 2.2: 3 hours
- Task 2.3: 2 hours
- Task 2.4: 1 hour
- Task 2.5: 1 hour
- **Total: ~8 hours** (spread across the week)

---

## Part E: Week 2 Success Criteria (Rubric)

| Criterion | Expectation | Self-Check |
|-----------|-------------|-----------|
| **Data Quality** | Transformed data has 0 critical issues (no nulls, negatives, duplicates) | ✓ |
| **Transformation Logic** | All cleaning decisions are documented and justified | ✓ |
| **Code Quality** | Code is tested (>80% coverage), readable, with clear docstrings | ✓ |
| **Test Coverage** | 10+ tests covering normal cases + edge cases (nulls, division by zero, etc.) | ✓ |
| **Documentation** | Transformation report explains what changed and why | ✓ |
| **Runbook** | Pipeline can be re-run with one command; troubleshooting guide exists | ✓ |
| **Version Control** | All code committed with meaningful messages (not "update", "fix") | ✓ |
| **Communication** | You can explain transformations to a non-technical stakeholder | ✓ |

Aim for **all criteria met** by end of Week 2.

---

## Part F: Week 3 Preview

Next week, you'll use your clean data to:

1. **Load:** Move Parquet into a database (PostgreSQL, SQLite, or BigQuery)
2. **Model:** Create fact and dimension tables (dimensional modeling)
3. **Orchestrate:** Automate the pipeline (cron, Airflow, Prefect)
4. **Monitor:** Add alerts for data quality issues

Your Week 2 foundation (clean code + tests + documentation) will make Week 3 smooth and professional.

---

## FAQ

**Q: My transformation runs slowly (>1 min). What's wrong?**  
A: Pandas is slow for big data. In Week 3, try Polars (10x faster) or DuckDB. For now, profile with `cProfile` or add `print()` to see where time is spent.

**Q: Should I filter outliers (extreme costs)?**  
A: No. Document them, but keep them. Analysts can filter in their queries. You shouldn't decide what's "real" data.

**Q: My tests are hard to write. Am I doing it wrong?**  
A: Tests that are hard to write signal that your code is coupled (e.g., reading from disk, external APIs). Refactor: separate "load data" from "transform data" → easier to test.

**Q: Can I use Pandas or DuckDB? Which is better?**  
A: Pandas is easier; DuckDB is faster. Start with Pandas for learning. If speed matters, switch to Polars or DuckDB.

**Q: What if the CSV schema changes next month (new columns)?**  
A: Your validation will catch it. Add a check: `assert 'NEW_COLUMN' in df.columns or log.warning('missing expected column')`. Document expected schema in docs.

**Q: How do I handle derived fields that depend on other derived fields?**  
A: Define a clear order. Example: quantity → cost_per_unit → cost_category. Comment why. Add tests for each step.

---

## Support & Questions

- **Stuck on nulls?** → Check Week 1 report; understand why data is null
- **Tests failing?** → Read error message carefully; check sample data
- **Slow transformation?** → Add timing prints; profile with `cProfile`
- **Confused about decisions?** → Read your own `Week2_Transformation_Strategy.md`

---

## Final Thought

> *"Clean data is 80% of the work. Spend time here, do it right, and the rest of the pipeline is easy."*

Build with integrity. Your Week 3–4 self will thank you.

---

**Last updated:** August 13, 2026  
**Version:** 1.0  
**Maintained by:** Venkat Potamsetti
