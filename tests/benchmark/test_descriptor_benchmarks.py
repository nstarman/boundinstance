"""Benchmarks for the access path.

`InstanceDescriptor.__get__` returns a fresh copy of itself on every access
(`dataclasses.replace` plus a new weak reference) rather than caching. Spec
§ 12.4 makes that the thing to measure before anyone optimises it away, so
these are the baseline.

Every host is bound to a name that outlives its loop. This library holds only
a *weak* reference to the enclosing object: a temporary like ``Host().d`` is
freed the instant the statement finishes, and dereferencing it afterwards
raises `ReferenceError` instead of measuring anything.

Caution: a local `pytest --codspeed` run (walltime mode) has a known
pytest-codspeed 5.0.3 double-division bug (`BenchmarkStats.from_list` divides
by the round's `iter_per_round`, then `_print_benchmark_table` divides by it
again) that rescales the displayed "Time (best)" by however hard that
benchmark got batched. Batching differs per benchmark, so the two figures in a
local run are not comparable to each other and neither is a trustworthy
absolute per-access cost. Only CI's instrumentation mode (Valgrind
instruction counting — a different code path, unaffected by this bug) should
inform a copy-versus-cache decision.
"""

import pytest

from boundinstance import InstanceDescriptor


class Host:
    d = InstanceDescriptor["Host"]()

    def __init__(self) -> None:
        self.name = "host"


@pytest.mark.benchmark(group="access")
def test_bound_access() -> None:
    """`__get__` plus the copy it makes: the hot path."""
    host = Host()
    for _ in range(1000):
        _ = host.d


@pytest.mark.benchmark(group="access")
def test_dereference() -> None:
    """Dereferencing the weak reference, apart from the `__get__` copy."""
    host = Host()
    bound = host.d
    for _ in range(1000):
        _ = bound.enclosing
