# Using the Python Style Guide in Google Colab

**Quick Start for Interns**

---

## Option 1: Upload the Module (Easiest)

### Step 1: Upload the file
1. In Colab, click **Files** (left sidebar)
2. Click **Upload** 
3. Select `scmd_style_guide.py`

### Step 2: Import and use
```python
from scmd_style_guide import (
    StyleGuideChecker,
    CodeReviewChecklist,
    StyleTips,
    CodeSnippets,
    check_file,
    get_checklist,
    show_tips,
    show_examples
)

# ✅ All utilities now available in your notebook
```

---

## Option 2: Import from GitHub (Advanced)

If the file is in a GitHub repo:

```python
import subprocess
import sys

# Clone repo or download file
url = "https://raw.githubusercontent.com/potamv01/LSA_intern_Aug_2026/main/scmd_style_guide.py"
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "requests"])

import requests
response = requests.get(url)
with open('scmd_style_guide.py', 'w') as f:
    f.write(response.text)

# Now import
from scmd_style_guide import *
```

---

## Usage Examples

### Check Your Code File

```python
from scmd_style_guide import check_file

# Check your transform.py
issues = check_file('transform.py')

# Returns list of issues
for issue in issues:
    print(f"Line {issue['line']}: {issue['message']}")
```

### Get Code Review Checklist

```python
from scmd_style_guide import get_checklist

# Print full checklist
get_checklist()

# Or get checklist for specific category
from scmd_style_guide import CodeReviewChecklist
checklist = CodeReviewChecklist()
checklist.print_checklist(category='Testing')
```

### View Style Tips

```python
from scmd_style_guide import show_tips

# Print all 20 tips
show_tips()

# Or get one random tip
from scmd_style_guide import StyleTips
tip = StyleTips.get_random_tip()
print(f"💡 {tip}")
```

### See Good/Bad Code Examples

```python
from scmd_style_guide import show_examples

# Show all examples
show_examples()

# Or show specific example
from scmd_style_guide import CodeSnippets
CodeSnippets.print_example('naming')
CodeSnippets.print_example('testing')
CodeSnippets.print_example('null_handling')
```

---

## Workflow: Week 2 Code Review

Use this workflow to review your code before submitting:

```python
# 1. Check your style
from scmd_style_guide import check_file
check_file('src/transform.py')

# 2. Review the checklist
from scmd_style_guide import get_checklist
get_checklist()

# 3. Fix issues

# 4. Get random tips for ideas
from scmd_style_guide import StyleTips
for i in range(5):
    print(f"💡 Tip {i+1}: {StyleTips.get_random_tip()}")

# 5. Check again
check_file('src/transform.py')

# 6. Verify tests pass
import subprocess
subprocess.run(['pytest', 'tests/test_transform.py', '-v'])
```

---

## Example Notebook

Here's a complete Colab notebook workflow:

```python
# Cell 1: Setup
!pip install pandas pytest numpy

# Cell 2: Import utilities
from scmd_style_guide import (
    StyleGuideChecker,
    CodeReviewChecklist,
    show_tips,
    show_examples
)

# Cell 3: Show checklist
CodeReviewChecklist().print_checklist()

# Cell 4: Show some examples
CodeSnippets.print_example('naming')
CodeSnippets.print_example('testing')

# Cell 5: Check your code
check_file('transform.py')

# Cell 6: Run tests
import subprocess
result = subprocess.run(['pytest', 'tests/test_transform.py', '-v'])

# Cell 7: Final verification
if result.returncode == 0:
    print("✅ Ready to submit!")
else:
    print("❌ Fix the issues above")
```

---

## Troubleshooting

### "ImportError: No module named 'scmd_style_guide'"

**Solution:** Make sure you've uploaded the file or imported it correctly.

```python
# Check if file exists
import os
print(os.path.exists('scmd_style_guide.py'))

# If False, re-upload
```

### "SyntaxError when importing"

**Solution:** Make sure you're using Python 3.6+ (Colab uses 3.x by default).

```python
import sys
print(sys.version)  # Should show Python 3.x
```

### "AssertionError: File not found"

**Solution:** Provide full path to file.

```python
# Bad
check_file('transform.py')

# Good
check_file('/content/drive/MyDrive/scmd-bootcamp/src/transform.py')
# Or
check_file('./src/transform.py')
```

---

## Features Breakdown

### StyleGuideChecker
- ✅ Line length checks (<88 chars)
- ✅ Import organization checks
- ✅ Naming convention checks (snake_case, PascalCase)
- ✅ Docstring completeness checks
- ✅ Indentation checks (spaces vs. tabs)
- ✅ Whitespace checks (operators)
- ✅ Type hint checks
- ✅ Comment quality checks
- ✅ Bare except detection
- ✅ Mutable default detection

**Returns:** List of issues (errors + warnings)

### CodeReviewChecklist
- ✅ 8 categories
- ✅ 50+ checklist items
- ✅ Printable format
- ✅ Category filtering

**Use:** Before submitting code for review

### StyleTips
- ✅ 20 practical tips
- ✅ Random tip function
- ✅ All tips printable

**Use:** Learn best practices, get inspired

### CodeSnippets
- ✅ Good/bad examples for 5 topics
- ✅ Printable format
- ✅ Category-based viewing

**Use:** See what good code looks like

---

## Week 2 Submission Checklist

Before submitting your Week 2 code:

```python
# 1. Run style checker
from scmd_style_guide import check_file
issues = check_file('src/transform.py')
assert len([i for i in issues if i['severity'] == 'error']) == 0  # 0 errors

# 2. Run tests
import subprocess
result = subprocess.run(['pytest', 'tests/test_transform.py', '-v'])
assert result.returncode == 0  # All tests pass

# 3. Check coverage
result = subprocess.run(['pytest', '--cov=src', 'tests/'])
# Should show >80% coverage

# 4. Review checklist
from scmd_style_guide import CodeReviewChecklist
checklist = CodeReviewChecklist()
checklist.print_checklist()
# Go through manually; ensure you've addressed each item

# 5. Commit
import subprocess
subprocess.run(['git', 'add', 'src/transform.py', 'tests/test_transform.py'])
subprocess.run(['git', 'commit', '-m', 'Week 2: Transform + tests + docs'])

print("✅ Ready to submit!")
```

---

## Tips for Colab Users

1. **Upload multiple files at once** (Ctrl+click)
2. **Use shell commands** (`!pytest`, `!git status`)
3. **Display outputs nicely** with `print()` or `display()`
4. **Save to Drive** if you want to keep work:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   # Now access files at /content/drive/MyDrive/
   ```

5. **Install packages** as needed:
   ```python
   !pip install -q pandas pytest black flake8
   ```

---

## Next Steps

1. **Download** `scmd_style_guide.py`
2. **Upload** to your Colab notebook
3. **Import** and start using in Week 2
4. **Submit** your code with confidence

---

## Questions?

- Check the main guide: **PYTHON_STYLE_GUIDE.md**
- Ask your instructor for clarification
- Post issues in GitHub

---

**Created:** August 2026  
**For:** SCMD Data Engineering Bootcamp  
**Version:** 1.0
