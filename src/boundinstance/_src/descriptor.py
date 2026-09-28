"""The instance descriptor. Private module; import from `boundinstance`."""

__all__ = ["InstanceDescriptor"]

import weakref
from dataclasses import dataclass, replace
from typing import Any, NoReturn, Self, cast, overload

from boundinstance._src.mypyc import mypyc_attr


@mypyc_attr(allow_interpreted_subclasses=True)
@dataclass
class InstanceDescriptor[BndTo]:
    """A descriptor that binds weakly to the instance it is accessed from.

    Assign an instance to a class attribute and every access from an instance
    returns a fresh copy holding a weak reference to that instance, reachable as
    `enclosing` (or `__self__`, mirroring bound methods).

    Examples
    --------
    >>> from boundinstance import InstanceDescriptor

    >>> class Plot(InstanceDescriptor["Potential"]):
    ...     def label(self) -> str:
    ...         return f"plot of {self.enclosing.name}"

    >>> class Potential:
    ...     plot = Plot()
    ...     def __init__(self, name: str) -> None:
    ...         self.name = name

    >>> hernquist = Potential("hernquist")
    >>> hernquist.plot.label()
    'plot of hernquist'

    Accessing it on the class is an error, since there is no instance to bind:

    >>> Potential.plot
    Traceback (most recent call last):
        ...
    AttributeError: 'plot' can only be accessed from a 'Potential' object

    """

    _enclosing_attr: str = ""
    _selfref: "weakref.ReferenceType[Any] | None" = None

    # ---------------------------------------------------------------- helpers

    def _describe(self) -> str:
        """Name this descriptor for an error message.

        `__set_name__` has not run when the descriptor was attached after class
        creation, so the attribute name can be missing.
        """
        name = getattr(self, "_enclosing_attr", "")
        return repr(name) if name else "this descriptor"

    # ------------------------------------------------------------- descriptor

    def __set_name__(self, owner: type, name: str) -> None:
        """Record the attribute name on the enclosing class."""
        self._enclosing_attr = name

    @overload
    def __get__(self, enclosing: None, enclosing_cls: type) -> NoReturn: ...
    @overload
    def __get__(self, enclosing: "BndTo", enclosing_cls: "type | None") -> Self: ...
    def __get__(
        self, enclosing: "BndTo | None", enclosing_cls: "type[BndTo] | None"
    ) -> Self:
        """Return a copy of this descriptor bound to `enclosing`."""
        if enclosing is None:
            owner = (
                "its enclosing object"
                if enclosing_cls is None
                else f"a {enclosing_cls.__name__!r} object"
            )
            msg = f"{self._describe()} can only be accessed from {owner}"
            raise AttributeError(msg)

        try:
            ref = weakref.ref(enclosing)
        except TypeError as e:
            msg = (
                f"cannot bind {self._describe()} to a "
                f"{type(enclosing).__name__!r} object: it does not support weak "
                "references. A class using __slots__ must include '__weakref__', "
                "and a mypyc-compiled native class cannot be weakly referenced "
                "at all."
            )
            raise TypeError(msg) from e

        # A fresh copy per access: the descriptor must not outlive its binding,
        # and the enclosing object may itself have been copied.
        dsc = replace(self)
        dsc._selfref = ref
        return dsc

    def __set__(self, obj: Any, value: object) -> NoReturn:
        """Reject assignment to the attribute."""
        msg = f"cannot set {self._describe()}"
        raise AttributeError(msg)

    # -------------------------------------------------------------- referent

    @property
    def __self__(self) -> BndTo:
        """The object this descriptor is bound to.

        Raises
        ------
        ReferenceError
            If this descriptor was never bound, or its referent has been
            collected.

        """
        ref = getattr(self, "_selfref", None)
        if ref is None:
            msg = (
                f"{self._describe()} is not bound to an object; access it from "
                "an instance rather than constructing it directly"
            )
            raise ReferenceError(msg)
        obj = ref()
        if obj is None:
            msg = (
                f"{self._describe()} is bound to an object that no longer "
                "exists; bind the enclosing object to a name before using it, "
                "rather than dereferencing a temporary"
            )
            raise ReferenceError(msg)
        return cast("BndTo", obj)

    @property
    def enclosing(self) -> BndTo:
        """The object this descriptor is bound to.

        Each access dereferences a weak reference, so assign it to a local when
        using it repeatedly.

        Raises
        ------
        ReferenceError
            If this descriptor was never bound, or its referent has been
            collected.

        """
        return self.__self__
