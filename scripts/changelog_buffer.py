"""Subagent changelog buffer helpers (v1.1.7).

Implementer subagents write Changes Manifest as YAML frontmatter to
.dj-superkit/changelog-buffer/<slug>/task-NN.md. The main agent reads
these at end-of-run to consolidate into a single 변경이력 entry.
"""
from pathlib import Path

import yaml


def write_manifest(target: Path, manifest: dict) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True)
    target.write_text(f"---\n{body}---\n", encoding="utf-8")


def read_manifest(target: Path) -> dict:
    text = target.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"missing YAML frontmatter: {target}")
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError(f"malformed manifest: {target}")
    return yaml.safe_load(parts[1])


def list_buffer_files(buffer_dir: Path) -> list[Path]:
    """Return task-*.md files sorted by numeric task id."""
    if not buffer_dir.exists():
        return []
    files = list(buffer_dir.glob("task-*.md"))
    return sorted(files, key=lambda p: int(p.stem.split("-")[1]))


def detect_stale_buffer(root: Path, slug: str) -> Path | None:
    """Return the slug subdir under root if it exists with manifests, else None."""
    candidate = root / slug
    if not candidate.exists():
        return None
    if not list_buffer_files(candidate):
        return None
    return candidate


def consolidate_to_entry(
    manifests_dir: Path,
    ch_id: str,
    timestamp: str,
) -> str:
    """Build a single git-fast slim [코드-수정] entry from buffer manifests.

    Code blocks are intentionally omitted — git show <SHA> is the source
    of truth in per-task commit_policy mode (AC-4).
    """
    manifests = [read_manifest(p) for p in list_buffer_files(manifests_dir)]
    if not manifests:
        raise ValueError("no manifests to consolidate")

    task_ids = [m["task_id"] for m in manifests]
    files = sorted({fc["path"] for m in manifests for fc in m.get("files_changed", [])})
    risks = sorted({r for m in manifests for fc in m.get("files_changed", [])
                     for r in fc.get("risk_hints", [])})
    all_shas = [c["sha"] for m in manifests for c in m.get("commits", [])]

    lines = [
        f"### [{timestamp}] [코드-수정] (batch: tasks {min(task_ids)}..{max(task_ids)})",
        f"- **id**: {ch_id}",
        "- **이유**: 서브에이전트 모드 task batch 종합 (end-of-run consolidation)",
        f"- **무엇이**: {', '.join(files)}",
        "- **영향범위**: 누적 (task별 세부 참조)",
        f"- **위험 카테고리**: {', '.join(risks) if risks else 'none'}",
        f"- **task별 세부 ({len(manifests)}건)**:",
    ]
    for m in manifests:
        for fc in m.get("files_changed", []):
            shas = ", ".join(f"`{c['sha']}`" for c in m.get("commits", []))
            lines.append(
                f"  - Task {m['task_id']}: `{fc['path']}:{fc['line_range']}`"
                f" — {fc['summary']} (`{','.join(fc.get('risk_hints', [])) or 'none'}`)"
                f" — commits: {shas}"
            )
    lines.append(f"- **연관 commits**: {', '.join(all_shas)}")
    lines.append("- **변경 전/후 코드**: 생략 — `git show <SHA>` 로 조회")
    return "\n".join(lines) + "\n"
