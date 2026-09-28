"""Static behaviour of the descriptor's type parameter.

Note on class access: `__get__`'s `NoReturn` overload for class access
(`enclosing=None`) compiles fine under mypyc (see Task 2), but mypy does not
use it to flag `Host.d` as a static error — `uv run mypy --warn-unused-ignores`
on a `# type: ignore[misc]` at that call site reports the ignore as unused.
So class access is a runtime-only `AttributeError`, not a static error; no
test asserts it as one here.
"""

from typing import assert_type

from boundinstance import InstanceDescriptor


class Host:
    d = InstanceDescriptor["Host"]()


def test_enclosing_is_the_type_parameter() -> None:
    """Accessing from an instance yields a descriptor bound to `Host`."""
    host = Host()
    bound = host.d
    assert_type(bound, InstanceDescriptor[Host])
    assert_type(bound.enclosing, Host)
    assert_type(bound.__self__, Host)


class Plot(InstanceDescriptor["Host"]):
    def label(self) -> str:
        return repr(self.enclosing)


class HasPlot(Host):
    plot = Plot()


def test_subclass_keeps_its_own_methods() -> None:
    """A subclass's inherited `enclosing` keeps the parameterised type."""
    host = HasPlot()
    plot = host.plot
    assert_type(plot.enclosing, Host)
    assert_type(plot.label(), str)
