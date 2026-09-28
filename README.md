# boundinstance

`boundinstance` provides `InstanceDescriptor`, a descriptor that binds weakly
to the instance it was accessed from, so a subclass can carry a reference back
to its enclosing object without creating a reference cycle.

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
```

## Compiled wheels

`boundinstance` ships mypyc-compiled wheels for supported platforms, plus a
pure-Python sdist that needs no compiler. `boundinstance.COMPILED` reports
whether the installed build is mypyc-compiled.
