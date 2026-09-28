"""The package's public surface."""

import os

import pytest

import boundinstance


def test_version() -> None:
    """The version is a non-empty string."""
    assert isinstance(boundinstance.__version__, str)
    assert boundinstance.__version__


def test_compiled_is_a_bool() -> None:
    """`COMPILED` reports whether the core module is a native extension."""
    assert isinstance(boundinstance.COMPILED, bool)


def test_compiled_matches_expectation() -> None:
    """`COMPILED` is `True` when the environment declares a compiled build.

    Whether *this* install is supposed to be compiled is not something the
    suite can infer from the install itself — that would just be checking
    `COMPILED` against another derivation of the same import, which can't
    fail when a compiled wheel is silently mispackaged as pure Python. The
    expectation has to come from outside, via `BOUNDINSTANCE_EXPECT_COMPILED`,
    set by the `wheel_compiled` nox session.
    """
    if os.environ.get("BOUNDINSTANCE_EXPECT_COMPILED") != "1":
        pytest.skip(
            "BOUNDINSTANCE_EXPECT_COMPILED not set; not asserting compiled-ness"
        )
    assert boundinstance.COMPILED is True


def test_public_surface() -> None:
    """`__all__` is exactly the documented names."""
    assert set(boundinstance.__all__) == {
        "COMPILED",
        "InstanceDescriptor",
        "__version__",
    }


def test_py_typed_ships() -> None:
    """The package advertises inline types."""
    from pathlib import Path

    assert (Path(boundinstance.__file__).parent / "py.typed").is_file()
