# Migrate from bound-class

`boundinstance` is the successor to the descriptor in
[`bound-class`](https://github.com/nstarman/bound-class)
(`bound_class.core.descriptors.InstanceDescriptor`). Two things change.

## The import

<!-- skip: next -->

```python
from bound_class.core.descriptors import InstanceDescriptor
```

becomes:

```python
from boundinstance import InstanceDescriptor
```

## The type parameter

`bound-class` parameterises subclasses with a module-level `TypeVar`:

<!-- skip: next -->

```python
from typing import TypeVar

BndTo = TypeVar("BndTo")


class Plot(InstanceDescriptor[BndTo]):
    def label(self) -> str:
        return f"plot of {self.enclosing.name}"
```

`boundinstance` requires Python 3.12+, so subclasses use
[PEP 695](https://peps.python.org/pep-0695/) generic syntax instead — no
`TypeVar` import, and the type parameter is declared directly on the class:

```python
class Plot[BndTo](InstanceDescriptor[BndTo]):
    def label(self) -> str:
        return f"plot of {self.enclosing.name}"


class Potential:
    plot = Plot()

    def __init__(self, name: str) -> None:
        self.name = name


nfw = Potential("hernquist")
assert nfw.plot.label() == "plot of hernquist"
```

If a subclass is only ever bound to one concrete type, parameterise it
directly instead of staying generic — `class Plot(InstanceDescriptor["Potential"])`,
as in the [tutorial](../tutorials/bound-namespace.md) — rather than
`class Plot[BndTo](InstanceDescriptor[BndTo])`.

## `BoundClassRef` is gone

`bound-class` wraps the weak reference in a `BoundClassRef` subclass of
`weakref.ref` that adds a finalizer, clearing the bound copy's reference when
the enclosing object is collected. `boundinstance` uses a plain
`weakref.ref` and has no finalizer.

This isn't a missing feature: dereferencing a dead `weakref.ref` already
returns `None`, which `boundinstance` turns into a clear `ReferenceError`. The
finalizer in `bound-class` only ever duplicated that check earlier. See
[Why a weak reference](../explanation/weak-references.md) for the full
reasoning.

## Everything else is unchanged

`__set_name__`, `__get__`, `__set__`, `__self__`, and `enclosing` all behave
the same way. If your subclass methods already read `self.enclosing`, only
the import and the type-parameter syntax need to change.
