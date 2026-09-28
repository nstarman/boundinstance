# A bound namespace

This tutorial builds `Potential.plot` — a small namespace of plotting methods
attached to a `Potential` object — from nothing, using `InstanceDescriptor`.
Along the way it shows the one usage rule the library depends on.

## The goal

We want to write:

<!-- skip: next -->

```python
nfw.plot.label()
```

and have `label()` reach back into `nfw` to read its name, without `plot`
holding a strong reference to `nfw` (that would create a reference cycle, and
would keep `nfw` alive for as long as `plot` is reachable, not the other way
around).

## Step 1: subclass `InstanceDescriptor`

`InstanceDescriptor` is generic in the type it will be bound to. Since
`Potential` doesn't exist yet, refer to it by name in a string:

```python
from boundinstance import InstanceDescriptor


class Plot(InstanceDescriptor["Potential"]):
    def label(self) -> str:
        return f"plot of {self.enclosing.name}"
```

`self.enclosing` is how a method reaches back to the object `Plot` was
accessed from. It isn't set yet — that happens on access, in the next step.

## Step 2: attach it as a class attribute

```python
class Potential:
    plot = Plot()

    def __init__(self, name: str) -> None:
        self.name = name
```

`plot = Plot()` looks like a shared, mutable class attribute, but it isn't
used directly. `InstanceDescriptor` is a descriptor: accessing `.plot` from an
instance calls `Plot.__get__`, which returns a **fresh copy** bound to that
instance rather than the original.

## Step 3: bind the enclosing object to a name, then use it

```python
>>> nfw = Potential("hernquist")
>>> nfw.plot.label()
'plot of hernquist'
```

`nfw` is a name in this scope, so the object it refers to stays alive for as
long as the name is in scope. `nfw.plot` returns a copy of `Plot` holding a
weak reference to `nfw`; `.label()` dereferences that weak reference and finds
`nfw` still alive.

Every access returns a new copy — the enclosing object may have moved on, so
`InstanceDescriptor` never caches the last binding:

```python
>>> nfw.plot is nfw.plot
False
```

## The one rule: bind before you access

`nfw.plot` only works because `nfw` is a name that keeps the `Potential`
object alive. Watch what happens without one:

```python
>>> Potential("hernquist").plot.label()
Traceback (most recent call last):
    ...
ReferenceError: weakly-referenced object no longer exists
```

`Potential("hernquist")` here is a temporary — nothing holds a reference to
it once `.plot` has finished evaluating. CPython frees it immediately (its
refcount drops to zero the instant the attribute lookup completes), so by the
time `.label()` runs and tries to dereference the weak reference, the object
is already gone.

This is the one thing to internalize about `InstanceDescriptor`: **always
bind the enclosing object to a name before touching an attribute that reads
`enclosing`.**

```python
# Wrong: `Potential(...)` is a temporary; `.plot` outlives it.
# Potential("hernquist").plot.label()

# Right: bind it first.
nfw = Potential("hernquist")
nfw.plot.label()
```

It's easy to ship the wrong version by accident — under `pytest`'s default
assertion rewriting, a chained temporary like `assert Potential("x").plot.label() == ...`
often keeps working, because the rewritten assertion holds a synthetic
reference to the temporary for the duration of the statement. The bug only
surfaces once that safety net is gone: in a REPL, in production code, or
under `pytest --assert=plain`.

## Step 4: grow it

Real namespaces have more than one method. Nothing changes about the rule —
every method that reads `self.enclosing` needs the same bound-name discipline
from its *caller*, not from itself:

```python
>>> class Plot(InstanceDescriptor["Potential"]):
...     def label(self) -> str:
...         return f"plot of {self.enclosing.name}"
...     def save(self, path: str) -> str:
...         return f"saved {self.enclosing.name} to {path}"

>>> class Potential:
...     plot = Plot()
...     def __init__(self, name: str) -> None:
...         self.name = name

>>> nfw = Potential("hernquist")
>>> nfw.plot.save("out.png")
'saved hernquist to out.png'
```

## Accessing it on the class, not an instance

There's no instance to bind to, so this is a runtime error, naming both the
attribute and the class:

```python
>>> Potential.plot
Traceback (most recent call last):
    ...
AttributeError: 'plot' can only be accessed from a 'Potential' object
```

## Next

- [Add methods to a descriptor](../how-to/subclass-methods.md) for more
  subclassing recipes.
- [Why a weak reference](../explanation/weak-references.md) for the reasoning
  behind the design.
