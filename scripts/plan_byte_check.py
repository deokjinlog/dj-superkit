"""Plan byte-equal verifier (v2.0.0+).

Checks every `**원본**` code block in an implementation plan against the
actual repo file at the specified line range. Used by writing-plans and
auto-writing-plans during Self-Review to enforce byte-equal precondition
for the v2.0.0 byte-copy implementer.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class Mismatch:
    plan_path: Path
    block_index: int
    file_path: Path
    expected: str
    actual: str
    reason: str


_BLOCK_RE = re.compile(
    r"\*\*원본\*\*\s*\(\s*`([^`:]+)(?::([\d-]+))?`\s*\)\s*:\s*\n"
    r"```[a-zA-Z0-9_+-]*\n(.*?)```",
    re.DOTALL,
)


def _parse_line_range(spec: Optional[str]) -> Optional[tuple[int, int]]:
    if not spec:
        return None
    if "-" in spec:
        a, b = spec.split("-", 1)
        return int(a), int(b)
    n = int(spec)
    return n, n


def verify_plan_block_byte_equal(
    plan_path: Path,
    repo_root: Path,
) -> List[Mismatch]:
    """Verify every `**원본**` block in plan_path matches actual file content.

    Returns empty list if all match. Each Mismatch carries enough context
    for plan author to fix (which block, which file, expected vs actual,
    reason).
    """
    text = plan_path.read_text(encoding="utf-8")
    mismatches: List[Mismatch] = []
    for idx, match in enumerate(_BLOCK_RE.finditer(text)):
        rel_path = match.group(1).strip()
        line_spec = match.group(2)
        expected = match.group(3)
        if expected.endswith("\n"):
            expected_no_trail = expected[:-1]
        else:
            expected_no_trail = expected

        file_path = (repo_root / rel_path).resolve()
        if not file_path.exists():
            mismatches.append(Mismatch(
                plan_path=plan_path,
                block_index=idx,
                file_path=file_path,
                expected=expected,
                actual="",
                reason=f"file not found: {rel_path}",
            ))
            continue

        file_text = file_path.read_text(encoding="utf-8")
        file_lines = file_text.splitlines(keepends=True)

        rng = _parse_line_range(line_spec)
        if rng is not None:
            start, end = rng
            if start < 1 or end > len(file_lines):
                mismatches.append(Mismatch(
                    plan_path=plan_path,
                    block_index=idx,
                    file_path=file_path,
                    expected=expected,
                    actual="",
                    reason=f"line range {start}-{end} out of bounds (file has {len(file_lines)} lines)",
                ))
                continue
            actual = "".join(file_lines[start - 1:end])
        else:
            # RISK: breaking — v2.0.1+ enforces (file:line-range) annotation
            # for Modify tasks. Pre-v2.0.1 plans without line range previously
            # silently fell through to whole-file compare; they now fail here.
            mismatches.append(Mismatch(
                plan_path=plan_path,
                block_index=idx,
                file_path=file_path,
                expected=expected,
                actual=file_text,
                reason=f"line range missing — Modify task **원본** block at {rel_path} requires `(file:line-range)` annotation (v2.0.1+)",
            ))
            continue

        if actual.endswith("\n"):
            actual_no_trail = actual[:-1]
        else:
            actual_no_trail = actual

        if expected_no_trail != actual_no_trail:
            mismatches.append(Mismatch(
                plan_path=plan_path,
                block_index=idx,
                file_path=file_path,
                expected=expected,
                actual=actual,
                reason=f"byte mismatch at {rel_path}:{line_spec or 'whole-file'}",
            ))

    return mismatches
