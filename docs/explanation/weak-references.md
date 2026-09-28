# Why a weak reference

`InstanceDescriptor` binds to its enclosing object through a `weakref.ref`,
not a plain attribute holding the object itself. This page is the single
place that argument is made; the class docstring and the tutorial deliberately
don't repeat it, so it can't drift out of sync with the implementation.

## The descriptor must not extend its host's lifetime

A class attribute like `plot = Plot()` is shared across every instance of the
enclosing class — there is exactly one `Plot()` object, not one per instance.
If accessing `nfw.plot` bound `self.enclosing` by storing a **strong**
reference on that shared object, every instance that had ever accessed
`.plot` would keep that instance alive via the shared descriptor, and each
new access would silently overwrite the previous binding out from under
whichever object was using it. Two problems, from one mistake:

- **A reference cycle.** `nfw` reaches the shared `Plot` instance through
  `Plot.__get__`; if that access also stored a strong reference from `Plot`
  back to `nfw`, the two would reference each other. Such a cycle is only
  ever collected by the cycle collector, not by plain reference counting, and
  is exactly the kind of thing worth designing away rather than relying on
  the garbage collector to clean up later.
- **The lifetime inversion.** The whole point of `enclosing` is that `plot`
  is a small helper *for* `nfw` — `nfw` should be free to be garbage
  collected the moment nothing else references it, whether or not something
  once asked for `nfw.plot`. A strong reference makes the helper keep its
  host alive, backwards from how the two are meant to relate.

A weak reference avoids both: it doesn't count towards the referent's
reference count, doesn't participate in cycle detection the same way, and
correctly reports "gone" once the referent actually is.

## Why a fresh copy on every access

Because the descriptor object attached to the class is shared, it can't
itself hold the binding — only a **copy** of it can. `__get__` therefore
returns `replace(self)` with a fresh `weakref.ref` to the object being
accessed from, every time. This is also why `enclosing` documents that
"assign it to a local when using it repeatedly": each access on the copy
dereferences a `weakref.ref`, and each `__get__` call constructs a new copy —
neither is free, so a tight loop that repeatedly reads `x.plot.something` is
doing more work than binding `plot = x.plot` once and reusing it.

## Why `bound-class`'s `BoundClassRef` finalizer was removed

`boundinstance`'s predecessor, `bound-class`, wrapped the weak reference in a
`BoundClassRef` subclass of `weakref.ref` that registered a
`weakref.finalize` callback: when the enclosing object was collected, the
callback reached back into the bound copy and cleared its reference
eagerly, so that a subsequent access would see "no reference" rather than a
dead one.

That finalizer duplicates work `weakref.ref` already does on its own. A
`weakref.ref` whose referent has been collected doesn't raise or leave stale
data when you call it — dereferencing a dead weak reference simply returns
`None`:

```python
import gc
import weakref


class Referent:
    pass


obj = Referent()
ref = weakref.ref(obj)
del obj
gc.collect()

assert ref() is None
```

`InstanceDescriptor.__self__` checks exactly that — it dereferences its
`weakref.ref` and raises a clear `ReferenceError` when the result is `None`,
no finalizer involved:

```python
from boundinstance import InstanceDescriptor


class Host:
    d = InstanceDescriptor["Host"]()


host = Host()
bound = host.d
del host
gc.collect()
```

```python
>>> bound.enclosing
Traceback (most recent call last):
    ...
ReferenceError: weakly-referenced object no longer exists
```

There is no state for a finalizer to eagerly clear — `ref()` already reports
"gone" the moment the referent is, whether or not anything ran in response to
the collection. The finalizer in `bound-class` added a moving part (a
callback, a second weak reference back to the bound copy to reach it,
`object.__setattr__` to poke through the dataclass) that only ever recomputed
what a plain dereference already tells you. `boundinstance` uses a plain
`weakref.ref` and no finalizer.
