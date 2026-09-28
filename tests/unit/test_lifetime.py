"""Reference lifetime, and inputs the spec does not specify."""

import copy
import gc
import pickle
import weakref

import pytest

from boundinstance import InstanceDescriptor


class Host:
    d = InstanceDescriptor["Host"]()

    def __init__(self, name: str = "host") -> None:
        self.name = name


def test_holding_a_bound_copy_does_not_keep_the_host_alive() -> None:
    """The descriptor must not extend the enclosing object's lifetime."""
    host = Host()
    bound = host.d                      # a live bound copy, deliberately retained
    witness = weakref.ref(host)

    del host
    gc.collect()

    assert witness() is None, "the descriptor kept the enclosing object alive"
    with pytest.raises(ReferenceError):
        bound.enclosing


# --- Review Focus 1: an enclosing object that cannot be weakly referenced ---


def test_slots_host_without_weakref_gives_a_usable_error() -> None:
    class Slotted:
        __slots__ = ("name",)
        d = InstanceDescriptor["Slotted"]()

        def __init__(self) -> None:
            self.name = "s"

    with pytest.raises(TypeError, match="Slotted.*weak references"):
        Slotted().d


def test_slots_host_with_weakref_works() -> None:
    class Slotted:
        __slots__ = ("__weakref__", "name")
        d = InstanceDescriptor["Slotted"]()

        def __init__(self) -> None:
            self.name = "s"

    host = Slotted()
    assert host.d.enclosing.name == "s"


# --- Review Focus 2: `__set_name__` never ran ---


def test_dynamically_attached_descriptor_describes_itself() -> None:
    """Attached via setattr, so `__set_name__` never fired."""
    class Bare:
        pass

    Bare.d = InstanceDescriptor["Bare"]()          # type: ignore[attr-defined]
    with pytest.raises(AttributeError, match="this descriptor"):
        Bare.d                                      # type: ignore[attr-defined]


# --- Review Focus 3: a subclass that skips field initialisation ---


def test_subclass_with_its_own_init_reports_unbound_not_attribute_error() -> None:
    class Sub(InstanceDescriptor["Host"]):
        def __init__(self) -> None:                 # deliberately no super() call
            pass

    with pytest.raises(ReferenceError, match="not bound"):
        Sub().enclosing


# --- Review Focus 4: one instance shared across attributes ---


def test_one_instance_on_two_attributes_takes_the_last_name() -> None:
    """Documented behaviour, not endorsed: share instances and names blur."""
    shared = InstanceDescriptor["Two"]()

    class Two:
        a = shared
        b = shared

    # `__set_name__` fired twice; the later assignment won.
    assert Two().a._enclosing_attr == "b"  # pyright: ignore[reportPrivateUsage]


# --- Review Focus 5: pickling and copying ---


def test_the_host_stays_picklable() -> None:
    """The descriptor is a class attribute, so it is not in instance state."""
    assert pickle.loads(pickle.dumps(Host("h"))).name == "h"


def test_a_bound_copy_is_not_picklable() -> None:
    """Weak references cannot be pickled; the error must be comprehensible."""
    with pytest.raises((TypeError, pickle.PicklingError), match="(?i)weakref"):
        pickle.dumps(Host().d)


def test_deepcopying_the_host_rebinds_on_next_access() -> None:
    original = Host("original")
    clone = copy.deepcopy(original)
    assert clone.d.enclosing is clone
    assert original.d.enclosing is original
