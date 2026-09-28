# API

`boundinstance`'s public surface is exactly three names: `InstanceDescriptor`, `COMPILED`, and `__version__`.

::: boundinstance.InstanceDescriptor

::: boundinstance.COMPILED

<!-- prettier-ignore -->
::: boundinstance.__version__

## The enclosing object must support weak references

`InstanceDescriptor` binds with a `weakref.ref`, so the object it is accessed from has to be weakly referenceable. Ordinary Python classes are. Two kinds are not, and both raise `TypeError` from `__get__`, naming the offending class:

- a class defining `__slots__` without listing `__weakref__` — add it to the slots;
- a **mypyc-compiled native class**, which has no weak-reference support at all — decorate it `@mypyc_attr(native_class=False)` to opt it out of mypyc's native representation.

The restriction only holds when every class in the hierarchy declares `__slots__` and omits `__weakref__`; a subclass that declares no `__slots__` regains support from the `__dict__` Python adds for it.

## Class access is a runtime error, not a static one

`Cls.attr` — accessing a descriptor from the class rather than an instance — raises `AttributeError` at runtime, naming both the attribute and the class. It is **not** rejected statically: `__get__`'s class-access overload (not shown above, since overloads aren't rendered) is typed to return `Never`, spelled `NoReturn` in the source, which shapes IDE completions and unreachability analysis for that expression, but `mypy` does not flag `Cls.attr` itself as an error at the call site. A `# type: ignore` on that line is reported as _unused_ by `mypy --warn-unused-ignores`. Whether your type checker treats `Cls.attr` as unreachable code is orthogonal to whether it flags the access as an error — check both if that distinction matters to you.
