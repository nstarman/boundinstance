# Wheels and platforms

`boundinstance` ships two kinds of build:

- A **pure-Python sdist**, which needs no compiler and works everywhere
  `requires-python` allows.
- **mypyc-compiled wheels**, built for the platforms below. `descriptor.py` —
  the only module that defines `InstanceDescriptor` — is compiled to a native
  extension; everything else in the package stays interpreted Python.

```python
import boundinstance

assert isinstance(boundinstance.COMPILED, bool)
```

`boundinstance.COMPILED` reports which kind of build is installed. It is
`True` only on an install of one of the compiled wheels below; the sdist and
an editable/development install both report `False`. See
[What mypyc changes](../explanation/mypyc.md) for the one behavioural
difference a compiled build introduces.

## Build matrix

| | CPython 3.12 | CPython 3.13 | CPython 3.14 |
| --- | :-: | :-: | :-: |
| Linux (manylinux_2_28), x86_64 | ✓ | ✓ | ✓ |
| Linux (manylinux_2_28), aarch64 | ✓ | ✓ | ✓ |
| macOS, arm64 | ✓ | ✓ | ✓ |
| Windows, x86_64 | ✓ | ✓ | ✓ |

Not built: PyPy, 32-bit Windows, musllinux, and free-threaded (`*t`) builds —
none are excluded for a technical reason specific to `boundinstance`; they're
simply outside the platforms this project tests against.

## Installing a particular build

`pip install boundinstance` picks whichever wheel matches your platform and
interpreter automatically; there is no separate package name or extra for the
compiled build. To force the pure-Python sdist instead (for example, to build
from source on an unsupported platform), use:

```bash
pip install boundinstance --no-binary boundinstance
```
