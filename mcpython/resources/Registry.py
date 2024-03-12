from __future__ import annotations

import typing
from abc import ABC


class IRegisterAble(ABC):
    NAME: str = None


class Registry:
    def __init__(self, name: str, data_type: type[IRegisterAble]):
        self.name = name
        self.data_type = data_type
        self._registry: dict[str, type[IRegisterAble]] = {}
        self._namespace_free_registry: dict[str, tuple[type[IRegisterAble], ...]] = {}
        self._on_registration_period: list[typing.Callable] = []

    def on_registration_period(
        self, target: typing.Callable[[Registry], None]
    ) -> typing.Callable[[Registry], None]:
        self._on_registration_period.append(target)
        return target

    def run_registrations(self):
        for item in self._on_registration_period:
            item(self)

        self._on_registration_period.clear()

    def register(self, obj: type[IRegisterAble]) -> type[IRegisterAble]:
        if not isinstance(obj, type):
            raise ValueError(
                f"{self.name}: Registered objects should be classes, not instances, got {obj}"
            )

        if not issubclass(obj, self.data_type):
            raise ValueError(
                f"{self.name}: Registered object {obj} must be subclass of {self.data_type}"
            )

        if obj.NAME is None:
            raise ValueError(
                f"{self.name}: Registered object {obj} must set the 'NAME' attribute on the class"
            )

        if ":" not in obj.NAME:
            raise ValueError(
                f"{self.name}: Registered object {obj} named '{obj.NAME}' must be namespaced"
            )

        self._registry[obj.NAME] = obj
        base = self._namespace_free_registry.get(obj.NAME.split(":")[-1], ())
        self._namespace_free_registry[obj.NAME.split(":")[-1]] = base + (obj,)

        return obj

    def lookup(
        self,
        name: str,
        allow_namespace_free=True,
        must_be_unique=False,
        raise_on_error=False,
    ) -> type[IRegisterAble] | None:
        if name in self._registry:
            return self._registry[name]

        if not allow_namespace_free or name not in self._namespace_free_registry:
            if raise_on_error:
                raise KeyError(f"'{name}' is not a member of registry {self.name}")
            return

        free = self._namespace_free_registry[name]

        if len(free) > 1 and must_be_unique:
            if raise_on_error:
                raise KeyError(
                    f"'{name}' is not a unique member of the registry {self.name} "
                    f"(registered variants are: {', '.join(str(e) for e in free)})"
                )
            return

        return free[0]
