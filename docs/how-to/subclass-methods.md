# Add methods to a descriptor

Subclass `InstanceDescriptor[EnclosingType]` and add ordinary methods. Any method that needs to reach the object the descriptor was accessed from reads `self.enclosing` (or the lower-level `self.__self__`, which `enclosing` is built on).

## Add a method

```python
from boundinstance import InstanceDescriptor


class Plot(InstanceDescriptor["Potential"]):
    def contour(self) -> str:
        return f"contours of {self.enclosing.name}"

    def slice(self, axis: str) -> str:
        return f"{axis}-slice of {self.enclosing.name}"


class Potential:
    plot = Plot()

    def __init__(self, name: str) -> None:
        self.name = name
```

```python
nfw = Potential("hernquist")
assert nfw.plot.contour() == "contours of hernquist"
assert nfw.plot.slice("x") == "x-slice of hernquist"
```

Call these from a bound name, not a temporary — `Potential("hernquist").plot.contour()` would raise `ReferenceError`, because nothing keeps the temporary `Potential(...)` alive past the `.plot` lookup. See [the tutorial](../tutorials/bound-namespace.md) for why.

## Add fields alongside the methods

`InstanceDescriptor` is a `dataclass`; a subclass can add its own dataclass fields, and they survive the per-access copy:

```python
from dataclasses import dataclass


@dataclass
class Titled(InstanceDescriptor["Potential"]):
    title: str = "untitled"

    def caption(self) -> str:
        return f"{self.title}: {self.enclosing.name}"


class Figure:
    plot = Titled(title="figure 1")

    def __init__(self, name: str) -> None:
        self.name = name


fig = Figure("nfw")
assert fig.plot.caption() == "figure 1: nfw"
```

## Chain the subclass another level

Subclassing a subclass keeps the binding — useful for sharing a base set of methods across several descriptors:

```python
class Base[BndTo](InstanceDescriptor[BndTo]):
    def kind(self) -> str:
        return "base"


class Derived(Base["Potential"]):
    def describe(self) -> str:
        return f"{self.kind()} plot of {self.enclosing.name}"


class WithBase:
    plot = Derived()

    def __init__(self, name: str) -> None:
        self.name = name


wb = WithBase("nfw")
assert wb.plot.describe() == "base plot of nfw"
```

## Put more than one descriptor on a class

Each descriptor attribute is independent — `__set_name__` records its own attribute name, so two descriptors on the same class don't share state:

```python
class Plain[BndTo](InstanceDescriptor[BndTo]):
    pass


class TwoNamespaces:
    first = Plain["TwoNamespaces"]()
    second = Plain["TwoNamespaces"]()

    def __init__(self, name: str) -> None:
        self.name = name


two = TwoNamespaces("nfw")
assert two.first.enclosing is two
assert two.second.enclosing is two
assert two.first is not two.second
```
