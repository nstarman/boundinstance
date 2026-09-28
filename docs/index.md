# boundinstance

`boundinstance` provides `InstanceDescriptor`, a descriptor that binds **weakly** to the instance it was accessed from. Assign an instance to a class attribute and subclass `InstanceDescriptor` to add methods; every access from an instance returns a fresh copy holding a weak reference back to that instance, reachable as `enclosing`. The instance never gains a strong reference back to itself, so no reference cycle, and nothing keeps it alive past its natural lifetime.

## Install

```bash
pip install boundinstance
```

No runtime dependencies. Wheels are mypyc-compiled where available, with a pure-Python sdist as the fallback — see [Wheels and platforms](reference/wheels.md).

## A first example

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

That's the whole surface: subclass `InstanceDescriptor[EnclosingType]`, add methods that read `self.enclosing`, and attach an instance of the subclass as a class attribute.

## Where to go next

- New to the library? Start with the tutorial, [A bound namespace](tutorials/bound-namespace.md).
- Already know the shape of it? Jump to [Add methods to a descriptor](how-to/subclass-methods.md).
- Migrating from `bound-class` or `galax._boundinstance`? See the how-to guides for [bound-class](how-to/migrate-from-bound-class.md) and [galax](how-to/migrate-from-galax.md).
- Curious why the reference is weak, or what changes under mypyc? See [Explanation](explanation/weak-references.md).
