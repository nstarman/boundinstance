# Migrate from `galax._boundinstance`

`galax` currently carries a private copy of this descriptor,
`galax._boundinstance.InstanceDescriptor`, used at two call sites:
`galax.potential._src.plot.PlotPotentialDescriptor` and
`galax.dynamics._src.orbit.plot_helper.PlotOrbitDescriptor`. Both will switch
to depending on `boundinstance` directly instead (tracked as its own change in
`GalacticDynamics/galax`, not in this repository).

The change at each call site is the same PEP 695 rewrite described in
[Migrate from bound-class](migrate-from-bound-class.md): `galax._boundinstance`
exposes its type parameter as a module-level `BndTo` `TypeVar`, imported
alongside `InstanceDescriptor`.

## `galax.potential._src.plot`

<!-- skip: next -->

```python
from galax._boundinstance import BndTo, InstanceDescriptor


class PlotPotentialDescriptor(InstanceDescriptor[BndTo]):
    def potential_contours(self, backend=MatplotlibBackend, **kwargs):
        return plot_potential_contours(self.enclosing, backend, **kwargs)

    def density_contours(self, backend=MatplotlibBackend, **kwargs):
        return plot_density_contours(self.enclosing, backend, **kwargs)
```

becomes:

<!-- skip: next -->

```python
from boundinstance import InstanceDescriptor


class PlotPotentialDescriptor[BndTo](InstanceDescriptor[BndTo]):
    def potential_contours(self, backend=MatplotlibBackend, **kwargs):
        return plot_potential_contours(self.enclosing, backend, **kwargs)

    def density_contours(self, backend=MatplotlibBackend, **kwargs):
        return plot_density_contours(self.enclosing, backend, **kwargs)
```

## `galax.dynamics._src.orbit.plot_helper`

<!-- skip: next -->

```python
from galax._boundinstance import BndTo, InstanceDescriptor


class PlotOrbitDescriptor(InstanceDescriptor[BndTo]):
    def plot(self, backend=MatplotlibBackend, **kwargs):
        return plot_components(self.enclosing, backend, **kwargs)

    __call__ = plot
```

becomes:

<!-- skip: next -->

```python
from boundinstance import InstanceDescriptor


class PlotOrbitDescriptor[BndTo](InstanceDescriptor[BndTo]):
    def plot(self, backend=MatplotlibBackend, **kwargs):
        return plot_components(self.enclosing, backend, **kwargs)

    __call__ = plot
```

Both examples above are shown for reference (they depend on `galax`'s own
plotting backend and aren't runnable here); the shape of the change is
exactly the live example in
[Migrate from bound-class](migrate-from-bound-class.md#the-type-parameter):
drop the `TypeVar` import, declare the type parameter with `[BndTo]` directly
on the class, and import `InstanceDescriptor` from `boundinstance`.

Once both call sites move, `galax._boundinstance` (including its
`BoundClassRef` weakref subclass — see
[Why a weak reference](../explanation/weak-references.md) for why it isn't
needed) can be deleted entirely, and `galax`'s dependency on `boundinstance`
becomes real rather than vendored.
