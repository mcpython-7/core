import typing
from abc import ABC


class IRegistryEntry(ABC):
    NAME: str = None
    REGISTRY: typing.Union[str, "Registry"] = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls.REGISTRY in REGISTRIES:
            cls.REGISTRY = REGISTRIES[cls.REGISTRY]
        elif isinstance(cls.REGISTRY, str):
            _SCHEDULE_REGISTRY_UPDATE.append(cls)

    def set_registry_name(self, name: str):
        self.NAME = name
        return self

    def get_registry_name(self) -> str:
        return self.NAME

    async def register(self, name: str = None):
        if not isinstance(self.REGISTRY, Registry):
            raise RuntimeError(f"Registry on object {self} not set!")

        await self.REGISTRY.register(name, self)

    async def on_register(self):
        pass


class RegistryObject:
    def __init__(self, getter: typing.Callable[[], IRegistryEntry]):
        self.getter = getter

    def get(self):
        return self.getter()


class Registry:
    def __init__(
        self,
        name: str,
        obj_type: typing.Type[IRegistryEntry],
        registration_phase: str = None,
    ):
        self.__name = name
        self._obj_type = obj_type
        self.registration_phase = registration_phase
        self._entries: typing.Dict[str, obj_type] = {}
        self._entries_without_namespace: typing.Dict[str, typing.List[obj_type]] = {}

        REGISTRIES[name] = self
        self._lazy_inits: typing.List[
            typing.Callable[[], typing.Awaitable[IRegistryEntry]]
        ] = []

    def get_name(self):
        return self.__name

    name = property(get_name)

    async def register(self, name: str | None, obj) -> RegistryObject:
        if not isinstance(obj, self._obj_type):
            raise ValueError(
                f"Cannot register {obj} (named {name}) into registry '{self.name}': The registry expects the type {self._obj_type}, but got {type(obj)}"
            )

        if name is not None:
            obj.NAME = name

        if obj.NAME is None:
            raise ValueError(
                f"Cannot register {obj} (named {name}) into registry '{self.name}': 'NAME' is not set"
            )

        if ":" not in obj.NAME:
            raise ValueError(
                f"Cannot register {obj} into registry '{self.name}': 'NAME' ({obj.NAME}) has no namespace set"
            )

        self._entries[obj.NAME] = obj
        self._entries_without_namespace.setdefault(obj.NAME.split(":")[-1], []).append(
            obj
        )

        await obj.on_register()

        return RegistryObject(lambda: obj)

    def register_lazy(
        self,
        name: str | None,
        lazy: typing.Callable[[], typing.Awaitable[IRegistryEntry] | IRegistryEntry],
    ) -> RegistryObject:
        async def register():
            nonlocal name

            obj = lazy()
            if isinstance(obj, typing.Awaitable):
                obj = await obj
            await self.register(name, obj)

            name = obj.NAME

        self._lazy_inits.append(register)
        return RegistryObject(lambda: self._entries[name])

    async def init(self):
        for entry in self._lazy_inits:
            await entry()

        self._lazy_inits.clear()

    def lookup(self, obj: str | IRegistryEntry | RegistryObject) -> IRegistryEntry:
        if isinstance(obj, IRegistryEntry):
            return obj
        elif isinstance(obj, str):
            if obj in self._entries:
                return self._entries[obj]
            elif obj in self._entries_without_namespace:
                return self._entries_without_namespace[obj][-1]
            raise ValueError(obj)

        elif isinstance(obj, RegistryObject):
            return obj.get()

        raise ValueError(obj)

    def lookup_optional(self, obj: str | IRegistryEntry | RegistryObject) -> IRegistryEntry | None:
        try:
            return self.lookup(obj)
        except ValueError:
            pass


REGISTRIES: typing.Dict[str, Registry] = {}
_SCHEDULE_REGISTRY_UPDATE: typing.List[typing.Type[IRegistryEntry]] = []


async def init():
    from mcpython.world.block.BlockManagement import BLOCK_REGISTRY
    from mcpython.world.item.ItemManager import ITEM_REGISTRY

    for entry in _SCHEDULE_REGISTRY_UPDATE:
        entry.__init_subclass__()

    _SCHEDULE_REGISTRY_UPDATE.clear()

    for registry in REGISTRIES.values():
        await registry.init()
