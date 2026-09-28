"""Weakref-based instance descriptors."""

import importlib.util

from boundinstance._src.descriptor import InstanceDescriptor
from boundinstance._version import __version__

__all__ = ["COMPILED", "InstanceDescriptor", "__version__"]

# If mypyc-compiled, the core module is a native extension rather than a `.py`.
_spec = importlib.util.find_spec("boundinstance._src.descriptor")
COMPILED: bool = (
    _spec is not None
    and _spec.origin is not None
    and _spec.origin.endswith((".so", ".pyd", ".dylib"))
)
