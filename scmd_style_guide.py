"""
SCMD Python Style Guide Checker & Utilities

This module provides embedded style guide checks, linting utilities, and checklist 
generation for the SCMD data engineering bootcamp.

Usage in Google Colab:
    # Upload this file or import from GitHub
    from scmd_style_guide import StyleGuideChecker, CodeReviewChecklist, StyleTips
    
    # Check your code
    checker = StyleGuideChecker("src/transform.py")
    issues = checker.check()
    
    # Get code review checklist
    checklist = CodeReviewChecklist()
    checklist.print_checklist()
    
    # Get style tips
    print(StyleTips.get_random_tip())

Author: Venkat Potamsetti
Created: August 2026
License: Educational Use
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import ast
from collections import defaultdict


class StyleGuideChecker:
    """Check Python code against style guide rules."""
    
    def __init__(self, filepath: str, verbose: bool = True):
        """
        Initialize style checker.
        
        Args:
            filepath: Path to Python file to check
            verbose: Print findings to stdout
        """
        self.filepath = filepath
        self.verbose = verbose
        self.issues = []
        self.warnings = []
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r') as f:
            self.content = f.read()
        
        self.lines = self.content.split('\n')
    
    def check(self) -> List[Dict]:
        """Run all style checks. Return list of issues."""
        self.issues = []
        self.warnings = []
        
        # Run individual checks
        self._check_line_length()
        self._check_imports()
        self._check_naming()
        self._check_docstrings()
        self._check_indentation()
        self._check_whitespace()
        self._check_type_hints()
        self._check_comments()
        self._check_bare_except()
        self._check_mutable_defaults()
        
        if self.verbose:
            self._print_results()
        
        return self.issues + self.warnings
    
    def _check_line_length(self) -> None:
        """Check for lines >88 characters."""
        max_length = 88
        for i, line in enumerate(self.lines, 1):
            if len(line) > max_length:
                self.warnings.append({
                    'line': i,
                    'type': 'LINE_TOO_LONG',
                    'message': f"Line {i}: {len(line)} chars (max {max_length})",
                    'severity': 'warning'
                })
    
    def _check_imports(self) -> None:
        """Check import organization (stdlib → third-party → local)."""
        import_lines = []
        for i, line in enumerate(self.lines, 1):
            if line.startswith('import ') or line.startswith('from '):
                import_lines.append((i, line))
        
        # Check for wildcard imports
        for i, line in import_lines:
            if 'import *' in line:
                self.issues.append({
                    'line': i,
                    'type': 'WILDCARD_IMPORT',
                    'message': f"Line {i}: Avoid wildcard imports (from X import *)",
                    'severity': 'error'
                })
        
        # Check for multiple imports on one line
        for i, line in import_lines:
            if line.startswith('import ') and ', ' in line:
                self.warnings.append({
                    'line': i,
                    'type': 'MULTIPLE_IMPORTS',
                    'message': f"Line {i}: Keep one import per line",
                    'severity': 'warning'
                })
    
    def _check_naming(self) -> None:
        """Check for snake_case variables, PascalCase classes."""
        try:
            tree = ast.parse(self.content)
        except SyntaxError:
            return  # Can't parse; skip
        
        for node in ast.walk(tree):
            # Check function names (should be snake_case)
            if isinstance(node, ast.FunctionDef):
                if not self._is_snake_case(node.name):
                    self.warnings.append({
                        'line': node.lineno,
                        'type': 'NAMING',
                        'message': f"Function '{node.name}' should be snake_case",
                        'severity': 'warning'
                    })
            
            # Check class names (should be PascalCase)
            if isinstance(node, ast.ClassDef):
                if not self._is_pascal_case(node.name):
                    self.warnings.append({
                        'line': node.lineno,
                        'type': 'NAMING',
                        'message': f"Class '{node.name}' should be PascalCase",
                        'severity': 'warning'
                    })
    
    def _check_docstrings(self) -> None:
        """Check for docstrings on public functions/classes."""
        try:
            tree = ast.parse(self.content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            # Check function docstrings
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):  # Public function
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        self.warnings.append({
                            'line': node.lineno,
                            'type': 'MISSING_DOCSTRING',
                            'message': f"Function '{node.name}' missing docstring",
                            'severity': 'warning'
                        })
            
            # Check class docstrings
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                if not docstring:
                    self.warnings.append({
                        'line': node.lineno,
                        'type': 'MISSING_DOCSTRING',
                        'message': f"Class '{node.name}' missing docstring",
                        'severity': 'warning'
                    })
    
    def _check_indentation(self) -> None:
        """Check for 4-space indentation (not tabs)."""
        for i, line in enumerate(self.lines, 1):
            if '\t' in line:
                self.issues.append({
                    'line': i,
                    'type': 'TABS_USED',
                    'message': f"Line {i}: Use spaces, not tabs",
                    'severity': 'error'
                })
    
    def _check_whitespace(self) -> None:
        """Check for proper spacing around operators."""
        for i, line in enumerate(self.lines, 1):
            # Skip comments and strings
            if '#' in line:
                line = line.split('#')[0]
            
            # Check spacing around =, ==, >, <, etc.
            if ' = ' not in line and '=' in line and '==' not in line:
                if re.search(r'\w=\w', line) and 'def ' not in line:
                    self.warnings.append({
                        'line': i,
                        'type': 'SPACING',
                        'message': f"Line {i}: Add spaces around operators",
                        'severity': 'warning'
                    })
    
    def _check_type_hints(self) -> None:
        """Check for type hints on public functions."""
        try:
            tree = ast.parse(self.content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):  # Public function
                    # Check if function has arguments and no type hints
                    has_args = len(node.args.args) > 0
                    has_type_hints = node.returns is not None or any(
                        arg.annotation for arg in node.args.args
                    )
                    
                    if has_args and not has_type_hints:
                        self.warnings.append({
                            'line': node.lineno,
                            'type': 'MISSING_TYPE_HINTS',
                            'message': f"Function '{node.name}' missing type hints",
                            'severity': 'warning'
                        })
    
    def _check_comments(self) -> None:
        """Check comment quality (WHY, not WHAT)."""
        bad_comments = [
            'Set',
            'Get',
            'Loop',
            'If',
            'Initialize',
            'TODO',  # Document TODOs
        ]
        
        for i, line in enumerate(self.lines, 1):
            if '#' in line:
                comment = line.split('#')[1].strip()
                for bad in bad_comments:
                    if comment.startswith(bad + ' '):
                        self.warnings.append({
                            'line': i,
                            'type': 'COMMENT_QUALITY',
                            'message': f"Line {i}: Comment should explain WHY, not WHAT",
                            'severity': 'warning'
                        })
    
    def _check_bare_except(self) -> None:
        """Check for bare except clauses."""
        for i, line in enumerate(self.lines, 1):
            if 'except:' in line:
                self.issues.append({
                    'line': i,
                    'type': 'BARE_EXCEPT',
                    'message': f"Line {i}: Use specific exception types, not bare except",
                    'severity': 'error'
                })
    
    def _check_mutable_defaults(self) -> None:
        """Check for mutable default arguments."""
        pattern = r'def\s+\w+\([^)]*=\s*(?:\[|\{)[^\]]*'
        for i, line in enumerate(self.lines, 1):
            if re.search(pattern, line):
                self.issues.append({
                    'line': i,
                    'type': 'MUTABLE_DEFAULT',
                    'message': f"Line {i}: Don't use mutable defaults (list, dict); use None",
                    'severity': 'error'
                })
    
    @staticmethod
    def _is_snake_case(name: str) -> bool:
        """Check if name is snake_case."""
        return name.islower() and '_' in name or name.islower()
    
    @staticmethod
    def _is_pascal_case(name: str) -> bool:
        """Check if name is PascalCase."""
        return name[0].isupper() and not '_' in name
    
    def _print_results(self) -> None:
        """Print results to stdout."""
        print("=" * 60)
        print(f"STYLE GUIDE CHECK: {self.filepath}")
        print("=" * 60)
        
        if not self.issues and not self.warnings:
            print("✅ No issues found!")
        else:
            if self.issues:
                print(f"\n❌ ERRORS ({len(self.issues)}):")
                for issue in self.issues:
                    print(f"  Line {issue['line']}: {issue['message']}")
            
            if self.warnings:
                print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
                for warning in self.warnings[:10]:  # Show first 10
                    print(f"  Line {warning['line']}: {warning['message']}")
                if len(self.warnings) > 10:
                    print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        print("\n" + "=" * 60)
        print(f"Summary: {len(self.issues)} errors, {len(self.warnings)} warnings")
        print("=" * 60)


class CodeReviewChecklist:
    """Generate code review checklist for Week 2 submissions."""
    
    CATEGORIES = {
        'Style': [
            'Lines <88 characters',
            '4-space indentation (no tabs)',
            'Proper whitespace (2 lines between functions, 1 between methods)',
            'snake_case for functions/variables, PascalCase for classes',
            'Meaningful names (not x, df1, temp)',
            'Imports organized (standard → third-party → local)',
            'No wildcard imports',
        ],
        'Documentation': [
            'Module docstring at top of file',
            'Docstring on every public function (Google-style)',
            'Type hints on all functions',
            'Inline comments explain WHY, not WHAT',
            'No dead code or TODOs',
        ],
        'Functions': [
            'Each function <50 lines',
            'Single responsibility principle',
            'Returns consistent type (always X or always None)',
            'Default arguments are immutable',
            'Proper error handling (specific exceptions, not bare except)',
        ],
        'Testing': [
            '10+ tests written',
            'Test names describe what they test',
            'Fixtures used for common data',
            'Edge cases covered (nulls, zero division, empty data)',
            '>80% coverage on critical functions',
            'All tests passing',
        ],
        'Data Pipeline': [
            'Null handling documented (why drop vs. fill vs. flag)',
            'Type conversions explicit (pd.to_numeric with errors=coerce)',
            'Duplicates removed with documented key',
            'Data loss tracked and logged (n_before vs. n_after)',
            'Validation checks in place',
            'Idempotent (safe to run multiple times)',
        ],
        'Code Quality': [
            'No hardcoded paths (use config or arguments)',
            'Logging instead of print()',
            'Pandas vectorized (no iterrows)',
            'Efficient (Parquet instead of CSV for large files)',
            'Reproducible (fixed random seeds if needed)',
        ],
        'Git': [
            'Meaningful commit messages (not "fix" or "update")',
            'Commits are logical (one feature per commit)',
            'No large files committed (data excluded via .gitignore)',
            'Clean branch history (no merge conflicts)',
        ],
    }
    
    def print_checklist(self, category: Optional[str] = None) -> None:
        """Print code review checklist."""
        print("\n" + "=" * 70)
        print("WEEK 2 CODE REVIEW CHECKLIST")
        print("=" * 70)
        
        categories = [category] if category else self.CATEGORIES.keys()
        total_items = 0
        
        for cat in categories:
            if cat not in self.CATEGORIES:
                continue
            
            items = self.CATEGORIES[cat]
            total_items += len(items)
            
            print(f"\n### {cat} ({len(items)} points)")
            for i, item in enumerate(items, 1):
                print(f"  [ ] {item}")
        
        print(f"\n{'=' * 70}")
        print(f"Total Items: {total_items} (Aim for >85% for 'passing' work)")
        print("=" * 70 + "\n")
    
    def get_score_breakdown(self) -> Dict[str, int]:
        """Get points per category."""
        return {cat: len(items) for cat, items in self.CATEGORIES.items()}


class StyleTips:
    """Random style tips for interns."""
    
    TIPS = [
        "Variables: use snake_case (my_variable, not myVariable or MyVariable)",
        "Classes: use PascalCase (MyClass, not my_class or my_Class)",
        "Functions: use snake_case and descriptive names (calculate_cost_per_unit, not cppu)",
        "Comments: explain WHY, not WHAT. Bad: '# Set x to 0'. Good: '# Fill missing costs with 0 (free medicines exist under NHS)'",
        "Docstrings: Include Args, Returns, Raises. Use Google-style format.",
        "Type hints: Add to all public functions. def my_func(x: int) -> str:",
        "Imports: Group into stdlib → third-party → local. Add blank lines between groups.",
        "Line length: Keep <88 characters. Helps readability across monitors.",
        "Functions: Keep <50 lines. If longer, break into smaller functions.",
        "Testing: 10+ tests, >80% coverage. Test edge cases (nulls, zero division).",
        "Null handling: Always LOG what you do (drop vs. fill). Track n_before vs. n_after.",
        "Pandas: Vectorize! df['col'] = operation, not df.apply() or iterrows().",
        "Errors: Use specific exceptions (ValueError, FileNotFoundError), not bare except:",
        "Defaults: Never use mutable defaults ([], {}). Use None; initialize in function.",
        "Logging: Use logging module, not print(). logger.info(), logger.error(), etc.",
        "Idempotency: Running twice should give same result. Delete then insert, or upsert.",
        "Data loss: Document why you removed rows/columns. Be transparent with numbers.",
        "Testing: Write tests first (red-green-refactor). Tests are proof your code works.",
        "Git: Meaningful commit messages. 'Add null-handling logic for Quantity_Issued' > 'fix'.",
        "Code reviews: Ask 'Could a new person read this and understand it?'",
    ]
    
    @classmethod
    def get_random_tip(cls) -> str:
        """Get a random style tip."""
        import random
        return random.choice(cls.TIPS)
    
    @classmethod
    def print_all_tips(cls) -> None:
        """Print all tips."""
        print("\n" + "=" * 70)
        print("PYTHON STYLE GUIDE TIPS FOR DATA ENGINEERING")
        print("=" * 70 + "\n")
        for i, tip in enumerate(cls.TIPS, 1):
            print(f"{i:2d}. {tip}")
        print("\n" + "=" * 70 + "\n")


class CodeSnippets:
    """Good/Bad code examples for learning."""
    
    EXAMPLES = {
        'naming': {
            'bad': '''def tf(d):
    q = d['QUANTITY']
    c = d['COST']
    return c / q''',
            'good': '''def calculate_cost_per_unit(df: pd.DataFrame) -> pd.Series:
    """Calculate cost per unit for medicines."""
    quantity = df['TOTAL_QUANTITY_IN_VMP_UNIT']
    cost = df['INDICATIVE_COST']
    return cost / quantity'''
        },
        'null_handling': {
            'bad': '''df = df.dropna()  # Drops too much data silently''',
            'good': '''n_before = len(df)
df = df.dropna(subset=['PRODUCT_NAME'])  # Remove only critical nulls
n_after = len(df)
logger.info(f"Dropped {n_before - n_after} rows with null product names")'''
        },
        'testing': {
            'bad': '''def test_data():
    df = transform_data(sample)
    assert len(df) > 0  # Vague''',
            'good': '''def test_transform_adds_cost_per_unit_column():
    """Transformation should add cost_per_unit derived column."""
    df = transform_data(sample)
    
    assert 'cost_per_unit' in df.columns
    assert df['cost_per_unit'].dtype in ['float64', 'float32']
    assert (df['cost_per_unit'] > 0).all()'''
        },
        'error_handling': {
            'bad': '''def load_csv(path):
    try:
        return pd.read_csv(path)
    except:  # Catches everything
        print("Error")''',
            'good': '''def load_csv(path: str) -> pd.DataFrame:
    """Load CSV file.
    
    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If file is empty.
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")
    
    if len(df) == 0:
        raise ValueError(f"CSV file is empty: {path}")
    
    return df'''
        },
    }
    
    @classmethod
    def print_example(cls, category: str) -> None:
        """Print good/bad example for a category."""
        if category not in cls.EXAMPLES:
            print(f"Category '{category}' not found.")
            return
        
        example = cls.EXAMPLES[category]
        print(f"\n{'=' * 70}")
        print(f"EXAMPLE: {category.upper()}")
        print("=" * 70)
        
        print("\n❌ BAD:")
        print(example['bad'])
        
        print("\n✅ GOOD:")
        print(example['good'])
        
        print("\n" + "=" * 70 + "\n")
    
    @classmethod
    def print_all_examples(cls) -> None:
        """Print all examples."""
        for category in cls.EXAMPLES.keys():
            cls.print_example(category)


# Quick utility functions for Colab usage
def check_file(filepath: str) -> List[Dict]:
    """Quick function to check a file. Returns list of issues."""
    checker = StyleGuideChecker(filepath, verbose=True)
    return checker.check()


def get_checklist() -> None:
    """Print code review checklist."""
    CodeReviewChecklist().print_checklist()


def show_tips() -> None:
    """Show all style tips."""
    StyleTips.print_all_tips()


def show_examples() -> None:
    """Show all code examples."""
    CodeSnippets.print_all_examples()


# Google Colab friendly usage
if __name__ == "__main__":
    print("""
SCMD Python Style Guide Utilities
==================================

Usage in Google Colab:

1. Check a file:
   from scmd_style_guide import check_file
   issues = check_file('transform.py')

2. Get review checklist:
   from scmd_style_guide import get_checklist
   get_checklist()

3. See style tips:
   from scmd_style_guide import show_tips
   show_tips()

4. See code examples:
   from scmd_style_guide import show_examples
   show_examples()

For more info, see PYTHON_STYLE_GUIDE.md
    """)
