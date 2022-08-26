import typing

from mcpython.world.AbstractDefinition import (
    AbstractChunk,
    AbstractSection,
    AbstractDimension,
)
from mcpython.world.block.BlockState import BlockState


class Chunk(AbstractChunk):
    def __init__(self, dimension: AbstractDimension, position: typing.Tuple[int, int]):
        super().__init__()
        self.dimension = dimension
        self.position = position
        bottom, top = dimension.get_height_range()
        self.sections: typing.List["Section"] = [None] * ((top - bottom + 1) // 16)

    async def clear(self):
        for section in self.sections:
            if section is not None:
                await section.clear()

        self.sections[:] = [None] * len(self.sections)

    async def generate(self):
        raise NotImplementedError

    async def get_dimension(self, name: str) -> AbstractDimension:
        return self.dimension

    async def get_position(self) -> typing.Tuple[int, int]:
        return self.position

    async def get_loaded_sections(self) -> typing.List["AbstractSection"]:
        return [e for e in self.sections if e is not None]

    async def get_section(self, y: int) -> "AbstractSection":
        section = self.sections[y]

        if section is None:
            section = await self.load_section_from_saves(y)

        return section

    async def load_section_from_saves(self, y: int):
        section = self.sections[y] = Section(self, y)
        # TODO: load
        return section


class Section(AbstractSection):
    def __init__(self, chunk: Chunk, y: int):
        super().__init__()
        self.chunk = chunk
        self.y = y
        self.blocks: typing.List[BlockState | None] = [None] * (16 * 16 * 16)

    async def clear(self):
        for block in self.blocks:
            if block is not None:
                await block.on_remove(force=True)

        self.blocks[:] = [None] * (16 * 16 * 16)

    async def get_chunk(self) -> AbstractChunk:
        return self.chunk

    async def get_y_level(self) -> int:
        return self.y

    async def get_block(self, x: int, y: int, z: int) -> BlockState | None:
        cx, cy, cz = (await self.get_range())[0]
        return self.blocks[(x - cx) + (y - cy) * 16 + (z - cz) * 256]

    async def get_block_relative(self, dx: int, dy: int, dz: int) -> BlockState | None:
        return self.blocks[dx + dy * 16 + dz * 256]

    async def set_block(self, x: int, y: int, z: int, blockstate: BlockState | None):
        cx, cy, cz = (await self.get_range())[0]
        await self.set_block_relative(
            x - cx, y - cy, z - cz, blockstate, real_pos=(x, y, z)
        )

    async def set_block_relative(
        self, dx: int, dy: int, dz: int, blockstate: BlockState | None, real_pos=None
    ):
        index = dx + dy * 16 + dz * 256
        previous_block = self.blocks[index]

        if previous_block is not None:
            await previous_block.on_remove()

        if blockstate is not None:
            blockstate.position = real_pos or (
                dx + self.chunk.position[0] * 16,
                dy + self.y * 16,
                dz * self.chunk.position[1] * 16,
            )
            await blockstate.on_addition()

        self.blocks[index] = blockstate
