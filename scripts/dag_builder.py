"""DAG builder for js-super-subagent-driven-development wave scheduling.

Reads a plan's task list (with files + deps) and produces wave groupings
where tasks within a wave can run in parallel without file conflicts or
dependency violations. Post-hoc conflict detection compares per-task
manifests after wave execution to catch DAG inference errors.
"""
from dataclasses import dataclass, field


@dataclass
class Task:
    id: int
    name: str
    files: list[str]
    deps: list[int] = field(default_factory=list)
    model: str = "sonnet"


@dataclass
class Wave:
    index: int
    tasks: list[Task]


def build_waves(tasks: list[Task]) -> list[Wave]:
    """Kahn's algorithm + file-overlap secondary serialization.

    Within an indegree-zero candidate set, tasks that touch the same file
    are split: only one of them goes into the current wave (plan order
    earliest), others wait for next wave even though deps are satisfied.
    """
    by_id = {t.id: t for t in tasks}
    indeg = {t.id: len(t.deps) for t in tasks}
    waves: list[Wave] = []
    placed: set[int] = set()

    while len(placed) < len(tasks):
        candidates = [
            by_id[tid] for tid, deg in indeg.items()
            if deg == 0 and tid not in placed
        ]
        if not candidates:
            raise ValueError("Cyclic deps in tasks")

        candidates.sort(key=lambda t: t.id)

        wave_tasks: list[Task] = []
        used_files: set[str] = set()
        for cand in candidates:
            if any(f in used_files for f in cand.files):
                continue
            wave_tasks.append(cand)
            used_files.update(cand.files)

        if not wave_tasks:
            raise ValueError("Unable to place any task in wave (logic bug)")

        wave = Wave(index=len(waves) + 1, tasks=wave_tasks)
        waves.append(wave)

        for t in wave_tasks:
            placed.add(t.id)

        for tid, t in by_id.items():
            if tid in placed:
                continue
            for dep in t.deps:
                if dep in placed:
                    indeg[tid] -= 1
                    if indeg[tid] < 0:
                        indeg[tid] = 0

    return waves


def detect_conflicts(
    manifests: dict[int, list[str]],
) -> list[tuple[int, int, str]]:
    """Post-hoc file-conflict detection across same-wave manifests.

    Returns list of (task_id_a, task_id_b, shared_file) tuples for every
    pair of manifests that touched the same file. Empty list = no conflict.

    Caller (main agent at wave finalization) uses this to decide rollback
    of the later task (plan order). See tech-design D-T2.
    """
    conflicts: list[tuple[int, int, str]] = []
    ids = sorted(manifests.keys())
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            shared = set(manifests[a]) & set(manifests[b])
            for path in sorted(shared):
                conflicts.append((a, b, path))
    return conflicts
