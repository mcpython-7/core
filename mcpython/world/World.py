import os
import typing

from mcpython.world.AbstractDefinition import (
    AbstractWorld,
    DimensionFormatException,
    AbstractDimension,
)
from mcpython.world.Dimension import Dimension


local = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class World(AbstractWorld):
    DEFAULT_DIMENSION_CLASS = Dimension

    def __init__(self):
        super().__init__()
        self.arrival_dimensions: typing.Set[str] = set()
        self.dimensions: typing.Dict[str, Dimension] = {}

        self.current_dimension: Dimension = None
        self.current_render_position = [0, 10, 0]
        self.current_render_rotation = [0, -90]

    async def setup_default(self):
        await self.add_dimension(Dimension("minecraft:overworld", (0 - 64, 256 + 64)))
        self.current_dimension = overworld = await WORLD.get_dimension(
            "minecraft:overworld"
        )

    async def get_save_file_location(self) -> str:
        return local + "/home/saves/test"

    async def get_dimension(self, name: str) -> Dimension:
        if name not in self.arrival_dimensions:
            raise NameError(
                f"Dimension '{name}' is not arrival! You need to create it if you want it!"
            )

        if name not in self.dimensions:
            await self.load_dimension_from_save(name)

        return self.dimensions[name]

    async def load_dimension_from_save(self, name: str):
        raise NotImplementedError

    async def add_dimension(self, dimension: AbstractDimension):
        if not isinstance(dimension, Dimension):
            raise DimensionFormatException(type(dimension))

        self.dimensions[await dimension.get_name()] = dimension
        self.arrival_dimensions.add(dimension.name)

    async def get_loaded_dimensions(self) -> typing.List[Dimension]:
        return list(self.dimensions.values())


WORLD = World()
