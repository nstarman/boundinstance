# boundinstance

`boundinstance` provides `InstanceDescriptor`, a descriptor that binds weakly to the instance it was accessed from, so a subclass can carry a reference back to its enclosing object without creating a reference cycle.

## Install

```bash
pip install boundinstance
```

## Usage

```python
from boundinstance import InstanceDescriptor


class Plot(InstanceDescriptor["Potential"]):
    def label(self) -> str:
        return f"plot of {self.enclosing.name}"


class Potential:
    plot = Plot()

    def __init__(self, name: str) -> None:
        self.name = name


hernquist = Potential("hernquist")
assert hernquist.plot.label() == "plot of hernquist"
```

The reference back to the enclosing object is weak, so it doesn't outlive a temporary: bind the enclosing object to a name before reading `enclosing` from it, or you'll hit a `ReferenceError` (`Potential("hernquist").plot.label()` fails; `hernquist.plot.label()` works because `hernquist` keeps the object alive).

## Compiled wheels

`boundinstance` ships mypyc-compiled wheels for supported platforms, plus a pure-Python sdist that needs no compiler. `boundinstance.COMPILED` reports whether the installed build is mypyc-compiled.
