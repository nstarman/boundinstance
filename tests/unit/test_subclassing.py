"""Subclassing, the supported way to extend the descriptor."""

from dataclasses import dataclass

from boundinstance import InstanceDescriptor


class Host:
    def __init__(self, name: str = "host") -> None:
        self.name = name


def test_interpreted_subclass_binds() -> None:
    """A plain-Python subclass of a (possibly compiled) class works."""

    class Plot[BndTo](InstanceDescriptor[BndTo]):
        def label(self) -> str:
            return f"plot of {self.enclosing.name}"

    class H(Host):
        plot = Plot["H"]()

    host = H("h")
    assert host.plot.label() == "plot of h"


def test_subclass_of_subclass() -> None:
    """Two levels of subclassing keep the binding."""

    class Base[BndTo](InstanceDescriptor[BndTo]):
        def base(self) -> str:
            return "base"

    class Derived[BndTo](Base[BndTo]):
        def derived(self) -> str:
            return f"{self.base()} of {self.enclosing.name}"

    class H(Host):
        d = Derived["H"]()

    host = H("h")
    assert host.d.derived() == "base of h"


def test_subclass_may_add_dataclass_fields() -> None:
    """A subclass's own fields survive the per-access copy."""

    @dataclass
    class Titled[BndTo](InstanceDescriptor[BndTo]):
        title: str = "untitled"

    class H(Host):
        d = Titled["H"](title="figure 1")

    host = H("h")
    bound = host.d
    assert bound.title == "figure 1"
    assert bound.enclosing.name == "h"


def test_two_descriptors_on_one_class_keep_separate_names() -> None:
    """Distinct instances do not share state."""

    class Plot[BndTo](InstanceDescriptor[BndTo]):
        pass

    class H(Host):
        first = Plot["H"]()
        second = Plot["H"]()

    h = H()
    assert h.first._enclosing_attr == "first"
    assert h.second._enclosing_attr == "second"
