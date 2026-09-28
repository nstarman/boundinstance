# What mypyc changes

`boundinstance` ships mypyc-compiled wheels alongside a pure-Python sdist (see
[Wheels and platforms](../reference/wheels.md)). Compilation is meant to be
invisible: `InstanceDescriptor` behaves the same way whether `descriptor.py`
is interpreted or a native extension. There is exactly one place that isn't
true, and it's a limitation users will actually run into, not a corner case.

## mypyc native classes can't be weakly referenced

`InstanceDescriptor` binds to its enclosing object with a `weakref.ref` (see
[Why a weak reference](weak-references.md)). `weakref.ref` requires the
referent to support weak references, which a plain Python class does by
default but a mypyc **native class** does not — mypyc native classes don't
get a `__weakref__` slot unless one is explicitly requested. If you try to
bind `InstanceDescriptor` to an instance of a class that doesn't support weak
references, `__get__` raises a `TypeError` naming the offending class:

```python
from boundinstance import InstanceDescriptor


class Plot(InstanceDescriptor["Native"]):
    def label(self) -> str:
        return f"plot of {self.enclosing.name}"


class Native:
    __slots__ = ("name",)  # no '__weakref__': the same failure mode as a
    # mypyc native class, without needing to compile anything to show it.
    plot = Plot()

    def __init__(self, name: str) -> None:
        self.name = name
```

```python
>>> Native("nfw").plot
Traceback (most recent call last):
    ...
TypeError: cannot bind 'plot' to a 'Native' object: it does not support
weak references. A class using __slots__ must include '__weakref__', and a
mypyc-compiled native class cannot be weakly referenced at all.
```

A plain `__slots__` class without `__weakref__` is used above because it hits
the exact same underlying restriction — no `tp_weaklistoffset`, so no
`weakref.ref` — without a compiled build in the loop. A mypyc-compiled native
class raises the identical `TypeError`, naming the compiled class instead.
(A subclass that doesn't itself declare `__slots__` would silently regain
`__weakref__` support from the implicit `__dict__` Python adds — the
restriction only holds if every class in the hierarchy opts into `__slots__`
and leaves `__weakref__` out.)

## Two ways out

**Add `__weakref__` to `__slots__`.** If the enclosing class defines
`__slots__` itself, list `__weakref__` alongside its other slots:

```python
class PlotForSlotted(InstanceDescriptor["Slotted"]):
    def label(self) -> str:
        return f"plot of {self.enclosing.name}"


class Slotted:
    __slots__ = ("__weakref__", "name")
    plot = PlotForSlotted()

    def __init__(self, name: str) -> None:
        self.name = name
```

```python
host = Slotted("nfw")
assert host.plot.label() == "plot of nfw"
```

**Or mark the enclosing class `@mypyc_attr(native_class=False)`.** If the
class being compiled needs to stay weakly-referenceable, `mypyc_attr` (from
`mypy_extensions`, the same package `boundinstance` itself depends on for
compilation) opts it out of mypyc's native-class representation:

<!-- skip: next -->

```python
from mypy_extensions import mypyc_attr

from boundinstance import InstanceDescriptor


class Plot(InstanceDescriptor["Potential"]):
    def label(self) -> str:
        return f"plot of {self.enclosing.name}"


@mypyc_attr(native_class=False)
class Potential:
    plot = Plot()

    def __init__(self, name: str) -> None:
        self.name = name
```

This only matters when compiling *your own* class with mypyc — it has no
effect in a pure-Python install (`mypyc_attr` decorates the class and returns
it unchanged when mypy isn't compiling), so the snippet above isn't executed
here; it's the shape of the fix to apply in your own compiled build.

`InstanceDescriptor` itself is unaffected either way — the limitation is
about what you bind it *to*, not about `InstanceDescriptor` needing to be
compiled or not.
