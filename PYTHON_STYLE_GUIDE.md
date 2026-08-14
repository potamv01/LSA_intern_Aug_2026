# Python Style Guide for SCMD Data Engineering
## Based on Google Python Style Guide + Data Engineering Best Practices

**For:** August 2026 LSA Intern Bootcamp  
**Focus:** Production-quality code for data pipelines  
**Target:** Week 2+ (Transform, Load, Test phases)

---

## Table of Contents

1. [Style Essentials](#style-essentials)
2. [Naming Conventions](#naming-conventions)
3. [Imports](#imports)
4. [Documentation & Docstrings](#documentation--docstrings)
5. [Functions & Methods](#functions--methods)
6. [Classes](#classes)
7. [Error Handling](#error-handling)
8. [Testing Patterns](#testing-patterns)
9. [Data Engineering Specifics](#data-engineering-specifics)
10. [Code Review Checklist](#code-review-checklist)

---

## Style Essentials

### Line Length
- **Maximum: 88 characters** (allows readable code on standard monitors)
- Use Black formatter (enforces this automatically)
- Don't sacrifice readability for length limits

**❌ Bad:**
```python
result = df[df['INDICATIVE_COST'] > 1000]['VMP_PRODUCT_NAME'].unique()
```

**✅ Good:**
```python
high_cost_medicines = df[df['INDICATIVE_COST'] > 1000]
unique_medicines = high_cost_medicines['VMP_PRODUCT_NAME'].unique()
```

### Indentation
- **4 spaces per indentation level** (never tabs)
- Continuation lines should align or use hanging indent

**❌ Bad:**
```python
def transform_data(input_path, output_path,
  data_type='parquet'):  # Misaligned
    return df
```

**✅ Good:**
```python
def transform_data(
    input_path,
    output_path,
    data_type='parquet'
):
    return df
```

### Whitespace
- 2 blank lines between top-level definitions (functions, classes)
- 1 blank line between methods in a class
- Use spaces around operators

**❌ Bad:**
```python
def load_scmd(path):
    df=pd.read_csv(path)
    return df
def validate_scmd(df):
    return df.isnull().sum()==0
```

**✅ Good:**
```python
def load_scmd(path):
    df = pd.read_csv(path)
    return df


def validate_scmd(df):
    return df.isnull().sum() == 0
```

---

## Naming Conventions

### Variables & Functions
- **snake_case** for variables and functions
- **Descriptive names** (what it is, not cryptic abbreviations)
- **Avoid single letters** except in loops or math

**❌ Bad:**
```python
def tf(d):  # What does tf mean? What does d do?
    q = d['TOTAL_QUANTITY']
    c = d['COST']
    return c / q
```

**✅ Good:**
```python
def calculate_cost_per_unit(df):
    """Calculate cost per unit for medicines."""
    quantity = df['TOTAL_QUANTITY_IN_VMP_UNIT']
    cost = df['INDICATIVE_COST']
    return cost / quantity
```

### Classes
- **PascalCase** for class names
- **Nouns** (what it is, not verbs)

**❌ Bad:**
```python
class scmd_transformer:  # snake_case for class
    pass

class TransformData:  # Generic action verb
    pass
```

**✅ Good:**
```python
class SCMDTransformer:
    """Transforms raw SCMD data into clean format."""
    pass

class DataValidator:
    """Validates SCMD data against business rules."""
    pass
```

### Constants
- **UPPER_SNAKE_CASE** for constants
- **Module-level only** (not in functions)

**❌ Bad:**
```python
def clean_data(df):
    max_cost = 50000  # Should be a constant
    min_cost = 0
    return df[(df['COST'] >= min_cost) & (df['COST'] <= max_cost)]
```

**✅ Good:**
```python
MAX_INDICATIVE_COST = 50000
MIN_INDICATIVE_COST = 0

def clean_data(df):
    """Remove cost outliers."""
    return df[
        (df['INDICATIVE_COST'] >= MIN_INDICATIVE_COST) &
        (df['INDICATIVE_COST'] <= MAX_INDICATIVE_COST)
    ]
```

### Private Functions/Variables
- **Prefix with underscore** for internal/private items
- **Double underscore only for name mangling** (rare)

**❌ Bad:**
```python
def clean_nulls(df):  # Public-looking, but used only internally
    return df.fillna(0)

def transform_scmd(input_path):
    df = load(input_path)
    df = clean_nulls(df)  # Which clean_nulls? Confusing
```

**✅ Good:**
```python
def _clean_nulls_internal(df):
    """Internal function for null handling."""
    return df.fillna(0)

def transform_scmd(input_path):
    """Public API for transforming SCMD data."""
    df = load(input_path)
    df = _clean_nulls_internal(df)
```

---

## Imports

### Organization
1. **Standard library imports** (os, sys, datetime)
2. **Third-party imports** (pandas, numpy, pytest)
3. **Local application/module imports** (src.transform, src.validate)

**Blank line between each group.**

**❌ Bad:**
```python
import os
import pandas as pd
from src.transform import clean_data
import sys
from datetime import datetime
import numpy as np
from src.validate import validate_data
```

**✅ Good:**
```python
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

from src.transform import clean_data
from src.validate import validate_data
```

### Import Style
- **Absolute imports** (not relative)
- **One import per line** (except `from X import a, b, c` for related items)
- **Avoid wildcard imports** (`from X import *`)

**❌ Bad:**
```python
from src.transform import *  # What did we import?
from src import transform, validate, load  # Should be separate imports

import pandas as pd, numpy as np  # Multiple on one line
```

**✅ Good:**
```python
from src.transform import clean_data, add_derived_fields
from src.validate import validate_scmd
from src.load import load_to_database

import pandas as pd
import numpy as np
```

### Aliasing
- **Only for well-known abbreviations** (pd, np)
- **Be consistent** across the codebase

**❌ Bad:**
```python
import pandas  # Should use alias
df = pandas.read_csv('data.csv')

import numpy as n  # Non-standard alias
```

**✅ Good:**
```python
import pandas as pd
df = pd.read_csv('data.csv')

import numpy as np
```

---

## Documentation & Docstrings

### Module Docstring
- First thing in the file
- One-line summary, blank line, then detailed description

**❌ Bad:**
```python
"""Transform module."""
import pandas as pd
```

**✅ Good:**
```python
"""
Transform raw SCMD data into clean, validated format.

This module handles the ETL transformation pipeline:
  - Cleaning nulls
  - Fixing data types
  - Removing duplicates
  - Enriching with derived fields
  - Validating output

Example:
    df = transform_scmd('data/raw/scmd_202605.csv')
"""
import pandas as pd
```

### Function/Method Docstrings
- **Google-style or NumPy-style** (be consistent)
- One-line summary + blank line + detailed description
- Document Args, Returns, Raises

**Google Style:**
```python
def calculate_cost_per_unit(df, quantity_col, cost_col):
    """
    Calculate cost per unit for medicines.

    Args:
        df: DataFrame containing medicine data.
        quantity_col: Column name for quantity.
        cost_col: Column name for cost.

    Returns:
        Series: Cost per unit (cost / quantity).

    Raises:
        ValueError: If columns not found in DataFrame.
        ZeroDivisionError: If any quantity is zero.
    """
    if quantity_col not in df.columns:
        raise ValueError(f"Column {quantity_col} not found")
    
    if (df[quantity_col] == 0).any():
        raise ZeroDivisionError("Found zero quantities")
    
    return df[cost_col] / df[quantity_col]
```

### Inline Comments
- Explain **WHY**, not WHAT
- Keep them close to code they explain
- Start with `#` + space

**❌ Bad:**
```python
# Set cost to 0 if null
df['INDICATIVE_COST'] = df['INDICATIVE_COST'].fillna(0)

# Loop through rows
for idx, row in df.iterrows():
    pass
```

**✅ Good:**
```python
# Fill missing costs with 0 (some medicines are free under NHS)
df['INDICATIVE_COST'] = df['INDICATIVE_COST'].fillna(0)

# Avoid iterrows (slow); use apply or vectorized ops instead
# But if necessary, document the business logic:
for idx, row in df.iterrows():
    # Check if cost is anomalously high (>$10k) for this medicine
    pass
```

### Type Hints
- **Use for all public functions** (optional for private)
- Helps catch bugs early; improves readability

**❌ Bad:**
```python
def transform_scmd(input_path, output_path):
    df = pd.read_csv(input_path)
    return df
```

**✅ Good:**
```python
from pathlib import Path
from typing import Optional

def transform_scmd(
    input_path: str,
    output_path: str,
    compression: Optional[str] = 'snappy'
) -> pd.DataFrame:
    """Transform raw SCMD CSV to clean Parquet."""
    df = pd.read_csv(input_path)
    df.to_parquet(output_path, compression=compression)
    return df
```

---

## Functions & Methods

### Function Length
- **Keep functions small** (<50 lines is a good target)
- **Single responsibility principle**: One function, one job
- If it's hard to name, it's probably doing too much

**❌ Bad (90 lines, multiple responsibilities):**
```python
def process_data(input_file, output_file):
    # Load
    df = pd.read_csv(input_file)
    
    # Clean
    df = df.dropna()
    df['COST'] = pd.to_numeric(df['COST'], errors='coerce')
    
    # Deduplicate
    df = df.drop_duplicates()
    
    # Enrich
    df['cost_per_unit'] = df['COST'] / df['QUANTITY']
    df['category'] = pd.cut(df['COST'], bins=4)
    
    # Validate
    assert (df['QUANTITY'] >= 0).all()
    assert (df['COST'] >= 0).all()
    
    # Save
    df.to_parquet(output_file)
```

**✅ Good (modular, testable):**
```python
def load_raw_scmd(filepath: str) -> pd.DataFrame:
    """Load raw SCMD CSV."""
    return pd.read_csv(filepath)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean nulls and fix types."""
    df = df.dropna()
    df['INDICATIVE_COST'] = pd.to_numeric(df['INDICATIVE_COST'], errors='coerce')
    return df


def deduplicate(df: pd.DataFrame, key_cols: list) -> pd.DataFrame:
    """Remove duplicate rows by key."""
    return df.drop_duplicates(subset=key_cols, keep='first')


def add_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich with calculated columns."""
    df['cost_per_unit'] = df['INDICATIVE_COST'] / df['QUANTITY']
    df['category'] = pd.cut(df['INDICATIVE_COST'], bins=4)
    return df


def validate_scmd(df: pd.DataFrame) -> bool:
    """Validate data quality."""
    assert (df['QUANTITY'] >= 0).all(), "Negative quantities found"
    assert (df['INDICATIVE_COST'] >= 0).all(), "Negative costs found"
    return True


def transform_scmd(input_path: str, output_path: str) -> None:
    """Orchestrate full transformation pipeline."""
    df = load_raw_scmd(input_path)
    df = clean_data(df)
    df = deduplicate(df, key_cols=['YEAR_MONTH', 'ODS_CODE', 'VMP_SNOMED_CODE'])
    df = add_derived_fields(df)
    validate_scmd(df)
    df.to_parquet(output_path)
```

### Return Values
- **Return early** to reduce nesting
- **Be consistent** (always return something or always None)

**❌ Bad:**
```python
def validate_data(df):
    if df is None:
        if len(df) == 0:
            print("Empty DataFrame")
        else:
            print("OK")
            return True
```

**✅ Good:**
```python
def validate_data(df: pd.DataFrame) -> bool:
    """Validate DataFrame. Raise exception if invalid."""
    if df is None:
        raise ValueError("DataFrame is None")
    if len(df) == 0:
        raise ValueError("DataFrame is empty")
    return True
```

### Default Arguments
- **Use immutable defaults** (None, numbers, strings)
- **Never use mutable defaults** (lists, dicts)

**❌ Bad:**
```python
def append_column(df, new_values=[]):  # DANGER: Shared across calls
    new_values.append(999)
    df['new'] = new_values
    return df
```

**✅ Good:**
```python
def append_column(df: pd.DataFrame, new_values: Optional[list] = None) -> pd.DataFrame:
    """Append column to DataFrame."""
    if new_values is None:
        new_values = []
    new_values.append(999)
    df['new'] = new_values
    return df
```

---

## Classes

### Class Structure
- **One class per file** (unless tightly related)
- **Organize methods**: `__init__`, public methods, private methods
- **Use type hints** for init parameters

**✅ Good:**
```python
class SCMDTransformer:
    """Transform raw SCMD data into clean format.
    
    Attributes:
        input_path: Path to raw CSV file.
        output_path: Path to save processed Parquet.
        compression: Compression algorithm for Parquet.
    """
    
    def __init__(
        self,
        input_path: str,
        output_path: str,
        compression: str = 'snappy'
    ):
        """Initialize transformer."""
        self.input_path = input_path
        self.output_path = output_path
        self.compression = compression
    
    def run(self) -> pd.DataFrame:
        """Execute full transformation pipeline."""
        df = self._load()
        df = self._clean()
        df = self._enrich()
        self._validate(df)
        self._save(df)
        return df
    
    def _load(self) -> pd.DataFrame:
        """Load raw CSV (private method)."""
        return pd.read_csv(self.input_path)
    
    def _clean(self) -> pd.DataFrame:
        """Clean data (private method)."""
        pass
    
    def _enrich(self) -> pd.DataFrame:
        """Add derived fields (private method)."""
        pass
    
    def _validate(self, df: pd.DataFrame) -> bool:
        """Validate output (private method)."""
        return True
    
    def _save(self, df: pd.DataFrame) -> None:
        """Save to Parquet (private method)."""
        df.to_parquet(self.output_path, compression=self.compression)
```

### Special Methods
- Implement `__str__()` for readable string representation
- Implement `__repr__()` for unambiguous representation

**✅ Good:**
```python
class SCMDTransformer:
    def __repr__(self) -> str:
        """Unambiguous representation for debugging."""
        return f"SCMDTransformer(input={self.input_path}, output={self.output_path})"
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"SCMD Transformer: {self.input_path} → {self.output_path}"
```

---

## Error Handling

### Use Specific Exceptions
- **Catch specific exceptions**, never bare `except:`
- **Raise meaningful exceptions** with context

**❌ Bad:**
```python
def transform_scmd(path):
    try:
        df = pd.read_csv(path)
        return df
    except:  # Catches everything; masks bugs
        print("Error")
```

**✅ Good:**
```python
def transform_scmd(path: str) -> pd.DataFrame:
    """Transform SCMD data.
    
    Raises:
        FileNotFoundError: If CSV file doesn't exist.
        ValueError: If CSV is empty or malformed.
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"SCMD file not found: {path}")
    
    if len(df) == 0:
        raise ValueError(f"SCMD file is empty: {path}")
    
    return df
```

### Context Managers
- **Use `with` statements** for file I/O, database connections

**❌ Bad:**
```python
f = open('data.csv', 'r')
df = pd.read_csv(f)
f.close()  # Might not run if error occurs
```

**✅ Good:**
```python
with open('data.csv', 'r') as f:
    df = pd.read_csv(f)  # File automatically closed
```

### Logging
- **Use logging, not print()** for production code
- **Log at appropriate levels**: DEBUG, INFO, WARNING, ERROR

**❌ Bad:**
```python
def transform_data(df):
    print("Starting transformation")
    df = df.dropna()
    print("Dropped nulls")
    return df
```

**✅ Good:**
```python
import logging

logger = logging.getLogger(__name__)

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform data with logging."""
    logger.info(f"Starting transformation ({len(df)} rows)")
    
    n_before = len(df)
    df = df.dropna()
    n_after = len(df)
    
    logger.info(f"Dropped {n_before - n_after} null rows ({100*(n_before-n_after)/n_before:.1f}%)")
    
    return df
```

---

## Testing Patterns

### Test File Organization
```
tests/
├── test_transform.py      # Tests for src/transform.py
├── test_validate.py       # Tests for src/validate.py
├── conftest.py            # Shared fixtures
└── fixtures/              # Test data
    └── sample_scmd.csv
```

### Test Naming
- **test_WHAT_CONDITION_EXPECTED_RESULT**
- Make test names descriptive (readable = maintainable)

**❌ Bad:**
```python
def test_1():
    pass

def test_cleaning():
    pass

def test_null_handling_ok():
    pass
```

**✅ Good:**
```python
def test_clean_nulls_drops_rows_with_missing_key_fields():
    """Nulls in product name should be dropped (can't identify medicine)."""
    pass

def test_clean_nulls_fills_missing_costs_with_zero():
    """Nulls in cost should be filled with 0 (free medicines exist)."""
    pass

def test_calculate_cost_per_unit_handles_zero_quantity():
    """Division by zero should be handled gracefully."""
    pass
```

### Fixtures
- **Reusable test data** shared across tests
- **Defined in conftest.py** (top-level tests/ directory)

**✅ Good (conftest.py):**
```python
import pytest
import pandas as pd

@pytest.fixture
def sample_scmd_data():
    """Create minimal SCMD sample for testing."""
    return pd.DataFrame({
        'YEAR_MONTH': ['202605', '202605'],
        'ODS_CODE': ['RA2', 'RTH'],
        'VMP_PRODUCT_NAME': ['Paracetamol 500mg', 'Aspirin 100mg'],
        'TOTAL_QUANTITY_IN_VMP_UNIT': [100.0, 50.0],
        'INDICATIVE_COST': [10.0, 5.0]
    })

@pytest.fixture
def sample_scmd_with_nulls():
    """Create SCMD sample with nulls for null-handling tests."""
    return pd.DataFrame({
        'YEAR_MONTH': ['202605', '202605', '202605'],
        'ODS_CODE': ['RA2', 'RA2', 'RTH'],
        'VMP_PRODUCT_NAME': ['Paracetamol 500mg', None, 'Aspirin 100mg'],
        'TOTAL_QUANTITY_IN_VMP_UNIT': [100.0, None, 50.0],
        'INDICATIVE_COST': [10.0, 5.0, None]
    })
```

**Using fixtures in tests:**
```python
def test_clean_nulls_removes_null_product_names(sample_scmd_with_nulls):
    """Null product names can't be identified; should be dropped."""
    result = clean_nulls(sample_scmd_with_nulls)
    
    assert len(result) == 2  # One row dropped
    assert result['VMP_PRODUCT_NAME'].isnull().sum() == 0  # No nulls remain
```

### Assertions
- **One assertion per test** (or related assertions)
- **Use pytest's assertion helpers** (assert, not unittest.assertEqual)

**❌ Bad:**
```python
def test_transform():
    df = transform_data(sample_data)
    assert len(df) > 0  # Vague
    assert df is not None  # Vague
    assert 'cost' in df.columns  # Vague
```

**✅ Good:**
```python
def test_transform_produces_expected_columns():
    """Transformation should add derived columns."""
    df = transform_data(sample_data)
    
    expected_cols = ['cost_per_unit', 'cost_category']
    assert all(col in df.columns for col in expected_cols)
    assert df['cost_per_unit'].dtype in ['float64', 'float32']
```

### Mocking
- **Mock external dependencies** (file I/O, APIs, databases)
- **Use unittest.mock** or pytest-mock

**✅ Good:**
```python
from unittest.mock import patch, MagicMock

def test_download_scmd_calls_correct_url(mocker):
    """Download should call NHSBSA API with correct URL."""
    mock_urlopen = mocker.patch('urllib.request.urlopen')
    
    download_scmd(year=2026, month=5)
    
    # Verify URL was called
    mock_urlopen.assert_called_once()
    call_args = mock_urlopen.call_args[0][0]
    assert '202605' in call_args  # Correct month
```

---

## Data Engineering Specifics

### Pandas Best Practices

**❌ Bad (slow, memory-intensive):**
```python
for idx, row in df.iterrows():  # 1000x slower than vectorized
    df.at[idx, 'cost_per_unit'] = row['cost'] / row['quantity']
```

**✅ Good (vectorized):**
```python
df['cost_per_unit'] = df['INDICATIVE_COST'] / df['TOTAL_QUANTITY_IN_VMP_UNIT']
```

### Null Handling in Data Pipelines

**Always log what you do:**
```python
def clean_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Clean nulls with explicit logging."""
    n_before = len(df)
    
    # Decision: Remove product name nulls (can't identify medicine)
    nulls_in_name = df['VMP_PRODUCT_NAME'].isnull().sum()
    df = df.dropna(subset=['VMP_PRODUCT_NAME'])
    
    # Decision: Fill cost nulls with 0 (some medicines are free)
    nulls_in_cost = df['INDICATIVE_COST'].isnull().sum()
    df['INDICATIVE_COST'] = df['INDICATIVE_COST'].fillna(0)
    
    n_after = len(df)
    
    logger.info(f"Null handling: {n_before} → {n_after} rows")
    logger.info(f"  Dropped for null product name: {nulls_in_name}")
    logger.info(f"  Filled nulls in cost: {nulls_in_cost}")
    
    return df
```

### Data Type Consistency

**Explicit type conversion:**
```python
def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert to expected types."""
    df['INDICATIVE_COST'] = pd.to_numeric(
        df['INDICATIVE_COST'],
        errors='coerce'  # Invalid values → NaN
    )
    df['ODS_CODE'] = df['ODS_CODE'].astype(str)  # Keep as string (identifier)
    df['YEAR_MONTH'] = df['YEAR_MONTH'].astype(int)  # Year-month as integer
    
    return df
```

### Idempotency (Key for Pipelines)

**Running twice should give same result:**
```python
def load_to_database(df: pd.DataFrame, table_name: str) -> None:
    """Load data idempotently (safe to run multiple times)."""
    # Option 1: Delete then insert
    db.execute(f"DELETE FROM {table_name} WHERE year_month = {df['YEAR_MONTH'].iloc[0]}")
    df.to_sql(table_name, db, if_exists='append')
    
    # Option 2: Merge (upsert)
    df.to_sql(table_name, db, if_exists='replace')
    
    # Document what happened
    logger.info(f"Loaded {len(df)} rows to {table_name} (idempotent)")
```

---

## Code Review Checklist

Use this when reviewing intern Week 2 submissions:

### Style (10 points)
- [ ] Lines <88 characters
- [ ] 4-space indentation (no tabs)
- [ ] Proper whitespace (2 lines between functions, 1 between methods)
- [ ] snake_case for functions/variables, PascalCase for classes
- [ ] Meaningful names (not `x`, `df1`, `temp`)
- [ ] Imports organized (standard → third-party → local)
- [ ] No wildcard imports

### Documentation (10 points)
- [ ] Module docstring at top of file
- [ ] Docstring on every public function (Google-style)
- [ ] Type hints on all functions
- [ ] Inline comments explain WHY, not WHAT
- [ ] No dead code or TODOs

### Functions (10 points)
- [ ] Each function <50 lines
- [ ] Single responsibility principle
- [ ] Returns consistent type (always X or always None)
- [ ] Default arguments are immutable
- [ ] Proper error handling (specific exceptions, not bare except)

### Testing (15 points)
- [ ] 10+ tests written
- [ ] Test names describe what they test
- [ ] Fixtures used for common data
- [ ] Edge cases covered (nulls, zero division, empty data)
- [ ] >80% coverage on critical functions
- [ ] All tests passing

### Data Pipeline (15 points)
- [ ] Null handling documented (why drop vs. fill vs. flag)
- [ ] Type conversions explicit (pd.to_numeric with errors='coerce')
- [ ] Duplicates removed with documented key
- [ ] Data loss tracked and logged (n_before vs. n_after)
- [ ] Validation checks in place
- [ ] Idempotent (safe to run multiple times)

### Code Quality (15 points)
- [ ] No hardcoded paths (use config or arguments)
- [ ] Logging instead of print()
- [ ] Pandas vectorized (no iterrows)
- [ ] Efficient (Parquet instead of CSV for large files)
- [ ] Reproducible (fixed random seeds if needed)

### Git (10 points)
- [ ] Meaningful commit messages (not "fix" or "update")
- [ ] Commits are logical (one feature per commit)
- [ ] No large files committed (data excluded via .gitignore)
- [ ] Clean branch history (no merge conflicts)

**Total: 100 points. Aim for >85 for "passing" work.**

---

## Bonus: Quick Reference

### Top 10 Most Common Mistakes

1. **iterrows() instead of vectorized ops** → Use `.apply()` or vectorized operations
2. **Bare except clauses** → Catch specific exceptions
3. **Print() instead of logging** → Use logging module
4. **Mutable default arguments** → Use None; initialize in function
5. **No docstrings** → Document every public function
6. **Cryptic variable names** → Be descriptive
7. **100-line functions** → Break into smaller functions
8. **No type hints** → Add type hints to public functions
9. **Silent data loss** → Log what you drop/change
10. **No tests** → Write tests first

---

## Resources

- **Google Python Style Guide:** https://google.github.io/styleguide/pyguide.html
- **PEP 8:** https://pep8.org/
- **Black Code Formatter:** https://black.readthedocs.io/
- **Type Hints:** https://docs.python.org/3/library/typing.html
- **Pytest Docs:** https://docs.pytest.org/
- **Pandas Best Practices:** https://pandas.pydata.org/docs/development/policies/policies.html

---

## Summary

**Good code:**
- Is readable (clear names, proper formatting)
- Is documented (docstrings, comments, type hints)
- Is tested (unit tests, >80% coverage)
- Is maintainable (DRY, single responsibility, no hacks)
- Is logged (track what happens, not just print)
- Is data-aware (handle nulls, track loss, be idempotent)

**Apply these principles to Week 2+, and your pipeline will be professional-grade.**

---

**Last updated:** August 13, 2026  
**Version:** 1.0  
**For:** SCMD Data Engineering Bootcamp (August 2026 LSA Cohort)
