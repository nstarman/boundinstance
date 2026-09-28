"""The package's public surface."""

import boundinstance


def test_version() -> None:
    """The version is a non-empty string."""
    assert isinstance(boundinstance.__version__, str)
    assert boundinstance.__version__


def test_compiled_is_a_bool() -> None:
    """`COMPILED` reports whether the core module is a native extension."""
    assert isinstance(boundinstance.COMPILED, bool)


def test_public_surface() -> None:
    """`__all__` is exactly the documented names."""
    assert set(boundinstance.__all__) == {"COMPILED", "InstanceDescriptor", "__version__"}


def test_py_typed_ships() -> None:
    """The package advertises inline types."""
    from pathlib import Path

    assert (Path(boundinstance.__file__).parent / "py.typed").is_file()
