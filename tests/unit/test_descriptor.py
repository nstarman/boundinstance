"""Binding behaviour and the documented errors."""

import gc

import pytest

from boundinstance import InstanceDescriptor


class Plot(InstanceDescriptor["Potential"]):
    """A descriptor subclass, as a consumer would write it."""

    def label(self) -> str:
        return f"plot of {self.enclosing.name}"


class Potential:
    plot = Plot()

    def __init__(self, name: str) -> None:
        self.name = name


def test_set_name_records_the_attribute() -> None:
    assert Potential("x").plot._enclosing_attr == "plot"


def test_bound_access_reaches_the_enclosing_object() -> None:
    assert Potential("hernquist").plot.label() == "plot of hernquist"


def test_self_and_enclosing_agree() -> None:
    p = Potential("x")
    d = p.plot
    assert d.__self__ is p
    assert d.enclosing is p


def test_each_access_returns_a_fresh_copy() -> None:
    p = Potential("x")
    assert p.plot is not p.plot


def test_class_access_raises_naming_the_class() -> None:
    with pytest.raises(AttributeError, match=r"'plot'.*'Potential'"):
        Potential.plot


def test_assignment_raises() -> None:
    p = Potential("x")
    with pytest.raises(AttributeError, match=r"cannot set 'plot'"):
        p.plot = 1


def test_reference_error_after_the_referent_dies() -> None:
    p = Potential("x")
    d = p.plot
    del p
    gc.collect()
    with pytest.raises(ReferenceError, match="no longer exists"):
        d.enclosing


def test_reference_error_when_never_bound() -> None:
    with pytest.raises(ReferenceError, match="not bound"):
        Plot().enclosing
