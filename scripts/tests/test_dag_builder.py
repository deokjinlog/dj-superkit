"""Unit tests for scripts.dag_builder (v1.1.14)."""
from scripts.dag_builder import Task, Wave, build_waves, detect_conflicts


def test_task_dataclass_default_model_sonnet():
    t = Task(id=1, name="Foo", files=["a.py"], deps=[])
    assert t.model == "sonnet"


def test_wave_dataclass_holds_tasks():
    t1 = Task(id=1, name="Foo", files=["a.py"], deps=[])
    t2 = Task(id=2, name="Bar", files=["b.py"], deps=[])
    w = Wave(index=1, tasks=[t1, t2])
    assert len(w.tasks) == 2
    assert w.index == 1


def test_build_waves_linear_deps():
    """Task 2 depends on Task 1 → 2 waves of 1 task each."""
    t1 = Task(id=1, name="A", files=["a.py"], deps=[])
    t2 = Task(id=2, name="B", files=["b.py"], deps=[1])
    waves = build_waves([t1, t2])
    assert len(waves) == 2
    assert [t.id for t in waves[0].tasks] == [1]
    assert [t.id for t in waves[1].tasks] == [2]


def test_build_waves_independent_files():
    """3 tasks no deps, no file overlap → 1 wave with all 3."""
    tasks = [
        Task(id=1, name="A", files=["a.py"]),
        Task(id=2, name="B", files=["b.py"]),
        Task(id=3, name="C", files=["c.py"]),
    ]
    waves = build_waves(tasks)
    assert len(waves) == 1
    assert {t.id for t in waves[0].tasks} == {1, 2, 3}


def test_build_waves_file_conflict_serializes():
    """Tasks 2 and 3 both touch foo.py → DAG forces serialize."""
    tasks = [
        Task(id=1, name="A", files=["a.py"]),
        Task(id=2, name="B", files=["foo.py"]),
        Task(id=3, name="C", files=["foo.py"]),
    ]
    waves = build_waves(tasks)
    assert len(waves) >= 2
    for wave in waves:
        ids = {t.id for t in wave.tasks}
        assert not (2 in ids and 3 in ids)


def test_detect_conflicts_disjoint_returns_empty():
    """Two manifests touching different files → no conflicts."""
    manifests = {
        1: ["a.py", "b.py"],
        2: ["c.py", "d.py"],
    }
    assert detect_conflicts(manifests) == []


def test_detect_conflicts_shared_file_returns_pair():
    """Two manifests overlap on b.py → conflict pair (1, 2, 'b.py')."""
    manifests = {
        1: ["a.py", "b.py"],
        2: ["b.py", "c.py"],
    }
    conflicts = detect_conflicts(manifests)
    assert (1, 2, "b.py") in conflicts


def test_detect_conflicts_three_way_overlap():
    """Three manifests share x.py → 3 pairwise conflicts."""
    manifests = {
        1: ["x.py"],
        2: ["x.py"],
        3: ["x.py"],
    }
    conflicts = detect_conflicts(manifests)
    assert len(conflicts) == 3
