# API

`boundinstance`'s public surface is exactly three names: `InstanceDescriptor`,
`COMPILED`, and `__version__`.

::: boundinstance.InstanceDescriptor

::: boundinstance.COMPILED

## Class access is a runtime error, not a static one

`Cls.attr` — accessing a descriptor from the class rather than an instance —
raises `AttributeError` at runtime, naming both the attribute and the class.
It is **not** rejected statically: `__get__`'s class-access overload is typed
to return `Never` (spelled `NoReturn` on the overload above), which shapes IDE
completions and unreachability analysis for that expression, but `mypy` does
not flag `Cls.attr` itself as an error at the call site. A `# type: ignore` on
that line is reported as *unused* by `mypy --warn-unused-ignores`. Whether
your type checker treats `Cls.attr` as unreachable code is orthogonal to
whether it flags the access as an error — check both if that distinction
matters to you.
