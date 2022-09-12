import typing
from abc import ABC
from mcpython.world.block.BlockState import BlockState


class DimensionFormatException(Exception):
    pass


class ChunkDoesNotExistException(Exception):
    pass


class AbstractWorld(ABC):
    DEFAULT_DIMENSION_CLASS: typing.Type["AbstractDimension"] = None

    async def get_save_file_location(self) -> str:
        raise NotImplementedError

    async def get_dimension(self, name: str) -> "AbstractDimension":
        raise NotImplementedError

    async def add_dimension(self, dimension: "AbstractDimension"):
        raise NotImplementedError

    async def get_loaded_dimensions(self) -> typing.List["AbstractDimension"]:
        raise NotImplementedError

    async def get_chunk(
        self, dimension: str, cx: typing.Tuple[int, int] | int, cz: int = None
    ):
        return await (await self.get_dimension(dimension)).get_chunk(cx, cz)

    async def get_chunk_for_position(
        self,
        dimension: str,
        x: typing.Tuple[int, int] | typing.Tuple[int, int, int] | int,
        y: int = None,
        z: int = None,
    ):
        return await (await self.get_dimension(dimension)).get_chunk_for_position(
            x, y, z
        )

    async def get_block(
        self, dimension: str, x: int, y: int, z: int
    ) -> BlockState | None:
        return await (await self.get_chunk_for_position(dimension, x, y, z)).get_block(
            x, y, z
        )

    async def set_block(
        self, dimension: str, x: int, y: int, z: int, blockstate: BlockState | None, force=False, player=None
    ):
        return await (await self.get_chunk_for_position(dimension, x, y, z)).set_block(
            x, y, z, blockstate, force=force, player=player
        )


class AbstractDimension(ABC):
    DEFAULT_CHUNK_TYPE: typing.Type["AbstractChunk"] = None

    async def get_world(self) -> "AbstractWorld":
        raise NotImplementedError

    async def get_chunk(
        self, cx: typing.Tuple[int, int] | int, cz: int = None
    ) -> "AbstractChunk":
        raise NotImplementedError

    async def create_chunk(
        self, cx: typing.Tuple[int, int] | int, cz: int = None
    ) -> "AbstractChunk":
        raise NotImplementedError

    async def get_name(self) -> str:
        raise NotImplementedError

    def get_height_range(self) -> typing.Tuple[int, int]:
        raise NotImplementedError

    async def get_loaded_chunks(self) -> typing.List["AbstractChunk"]:
        raise NotImplementedError

    async def get_chunk_for_position(
        self,
        x: typing.Tuple[int, int] | typing.Tuple[int, int, int] | int,
        y: int = None,
        z: int = None,
    ):
        if isinstance(x, tuple):
            return await self.get_chunk(x[0] // 16, x[-1] // 16)

        return await self.get_chunk(x // 16, (z or y) // 16)

    async def get_section_of_chunk(self, cx: int, cy: int, cz: int):
        return await (await self.get_chunk(cx, cz)).get_section(cy)

    async def get_section_for_position(
        self, x: typing.Tuple[int, int, int] | int, y: int = None, z: int = None
    ):
        if isinstance(x, tuple):
            return (await self.get_chunk_for_position(x)).get_section_for_position(x[1])

        return (await self.get_chunk_for_position(x, z)).get_section(y)

    async def get_block(self, x: int, y: int, z: int) -> BlockState | None:
        return await (await self.get_chunk_for_position(x, y, z)).get_block(x, y, z)

    async def set_block(self, x: int, y: int, z: int, blockstate: BlockState | None, force=False, player=None):
        await (await self.get_chunk_for_position(x, y, z)).set_block(
            x, y, z, blockstate, force=force, player=player,
        )

    async def block_update_neighbors(self, x: int, y: int, z: int, include_self=True):
        cause = (x, y, z)

        for dx, dy, dz in (
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1),
        ) + (((0, 0, 0),) if include_self else tuple()):
            try:
                block = await self.get_block(x + dx, y + dy, z + dz)
            except ChunkDoesNotExistException:
                continue  # todo: do we want to load the chunk?

            if block is not None:
                await block.on_block_update(cause)


class AbstractChunk(ABC):
    DEFAULT_SECTION_TYPE: typing.Type["AbstractSection"] = None

    async def clear(self):
        raise NotImplementedError

    async def generate(self):
        raise NotImplementedError

    async def get_dimension(self, name: str) -> AbstractDimension:
        raise NotImplementedError

    async def get_position(self) -> typing.Tuple[int, int]:
        raise NotImplementedError

    async def get_range(
        self,
    ) -> typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]:
        x, z = await self.get_position()
        return (x * 16, z * 16), (x * 16 + 15, z * 16 + 15)

    async def get_range_exclusive(
        self,
    ) -> typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]]:
        x, z = await self.get_position()
        return (x * 16, z * 16), (x * 16 + 16, z * 16 + 16)

    async def get_loaded_sections(self) -> typing.List["AbstractSection"]:
        raise NotImplementedError

    async def get_section(self, y: int) -> "AbstractSection":
        raise NotImplementedError

    async def get_section_for_position(
        self,
        x: typing.Tuple[int, int, int] | int,
        y: int = None,
        z: int = None,
    ):
        if isinstance(x, tuple):
            return await self.get_section(x[1])
        elif y is None:
            return await self.get_section(x)

        return await self.get_section(y)

    async def get_block(self, x: int, y: int, z: int) -> BlockState | None:
        return await (await self.get_section_for_position(y)).get_block(x, y, z)

    async def get_block_relative(self, dx: int, y: int, dz: int) -> BlockState | None:
        section = await self.get_section_for_position(y)
        return await section.get_block_relative(
            dx, y - await section.get_y_level() * 16, dz
        )

    async def set_block(self, x: int, y: int, z: int, blockstate: BlockState | None, force=False, player=None):
        await (await self.get_section_for_position(y)).set_block(x, y, z, blockstate, force=force, player=player)

    async def set_block_relative(
        self, dx: int, y: int, dz: int, blockstate: BlockState | None, force=False, player=None
    ):
        section = await self.get_section_for_position(y)
        await section.set_block_relative(dx, y - await section.get_y_level() * 16, dz, blockstate, force=force, player=player)


class AbstractSection(ABC):
    async def get_chunk(self) -> AbstractChunk:
        raise NotImplementedError

    async def get_y_level(self) -> int:
        raise NotImplementedError

    async def get_cxyz_position(self) -> typing.Tuple[int, int, int]:
        y = await self.get_y_level()
        x, z = await (await self.get_chunk()).get_position()
        return x, y, z

    async def get_range(
        self,
    ) -> typing.Tuple[typing.Tuple[int, int, int], typing.Tuple[int, int, int]]:
        x, y, z = await self.get_cxyz_position()
        return (x * 16, y * 16, z * 16), (x * 16 + 15, y * 16 + 15, z * 16 + 15)

    async def get_range_exclusive(
        self,
    ) -> typing.Tuple[typing.Tuple[int, int, int], typing.Tuple[int, int, int]]:
        x, y, z = await self.get_cxyz_position()
        return (x * 16, y * 16, z * 16), (x * 16 + 16, y * 16 + 16, z * 16 + 16)

    async def get_block(self, x: int, y: int, z: int) -> BlockState | None:
        raise NotImplementedError

    async def get_block_relative(self, dx: int, dy: int, dz: int) -> BlockState | None:
        raise NotImplementedError

    async def set_block(self, x: int, y: int, z: int, blockstate: BlockState | None, force=False, player=None):
        raise NotImplementedError

    async def set_block_relative(
        self, dx: int, dy: int, dz: int, blockstate: BlockState | None, force=False, player=None
    ):
        raise NotImplementedError
