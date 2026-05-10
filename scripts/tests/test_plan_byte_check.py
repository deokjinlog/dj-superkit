"""Unit tests for scripts.plan_byte_check."""
from pathlib import Path
from scripts.plan_byte_check import verify_plan_block_byte_equal, Mismatch


def _write(p: Path, content: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_byte_equal_pass(tmp_path):
    src = _write(tmp_path / "src" / "foo.py", "def hello():\n    return 'hi'\n")
    plan = _write(tmp_path / "plan.md", f"""# Plan
### Task 1
**원본** (`src/foo.py:1-2`):
```python
def hello():
    return 'hi'
```
**수정 후**:
```python
def hello():
    return 'hello'
```
""")
    mismatches = verify_plan_block_byte_equal(plan, tmp_path)
    assert mismatches == []


def test_byte_equal_fail_one_char_different(tmp_path):
    _write(tmp_path / "src" / "foo.py", "def hello():\n    return 'hi'\n")
    plan = _write(tmp_path / "plan.md", """# Plan
### Task 1
**원본** (`src/foo.py:1-2`):
```python
def hello():
    return 'HI'
```
**수정 후**:
```python
def hello():
    return 'hello'
```
""")
    mismatches = verify_plan_block_byte_equal(plan, tmp_path)
    assert len(mismatches) == 1
    assert mismatches[0].file_path.name == "foo.py"


def test_byte_equal_multiple_mismatches(tmp_path):
    _write(tmp_path / "a.py", "x = 1\n")
    _write(tmp_path / "b.py", "y = 2\n")
    plan = _write(tmp_path / "plan.md", """# Plan
### Task 1
**원본** (`a.py:1`):
```python
x = 999
```
**수정 후**:
```python
x = 0
```
### Task 2
**원본** (`b.py:1`):
```python
y = 888
```
**수정 후**:
```python
y = 0
```
""")
    mismatches = verify_plan_block_byte_equal(plan, tmp_path)
    assert len(mismatches) == 2


def test_byte_equal_file_not_found(tmp_path):
    plan = _write(tmp_path / "plan.md", """# Plan
### Task 1
**원본** (`missing.py:1`):
```python
x = 1
```
""")
    mismatches = verify_plan_block_byte_equal(plan, tmp_path)
    assert len(mismatches) == 1
    assert "not found" in mismatches[0].reason.lower()


def test_byte_equal_create_task_no_원본_block(tmp_path):
    """Create task — no `**원본**` block, only `**수정 후**`. Should skip (no Mismatch)."""
    plan = _write(tmp_path / "plan.md", """# Plan
### Task 1
**수정 후** (new file: `new.py`):
```python
print("hi")
```
""")
    mismatches = verify_plan_block_byte_equal(plan, tmp_path)
    assert mismatches == []


def test_byte_equal_line_range_out_of_bounds(tmp_path):
    _write(tmp_path / "src.py", "line1\nline2\n")
    plan = _write(tmp_path / "plan.md", """# Plan
### Task 1
**원본** (`src.py:5-10`):
```
line1
line2
```
""")
    mismatches = verify_plan_block_byte_equal(plan, tmp_path)
    assert len(mismatches) == 1
    assert "out of bounds" in mismatches[0].reason.lower() or "range" in mismatches[0].reason.lower()
