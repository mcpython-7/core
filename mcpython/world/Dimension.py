import typing

from mcpython.world.AbstractDefinition import (
    AbstractDimension,
    AbstractWorld,
    ChunkDoesNotExistException,
)
from mcpython.world.Chunk import Chunk


class Dimension(AbstractDimension):
    DEFAULT_CHUNK_TYPE = Chunk

    def __init__(self, name: str, height_range=(0, 255)):
        super().__init__()
        self.world: AbstractWorld = None
        self.name = name
        self.height_range = height_range

        self.chunks: typing.Dict[typing.Tuple[int, int], Chunk] = {}
        self.arrival_chunks: typing.Set[typing.Tuple[int, int]] = set()

    async def get_world(self) -> AbstractWorld:
        return self.world

    async def get_chunk(
        self, cx: typing.Tuple[int, int] | int, cz: int = None
    ) -> Chunk:
        pos = (cx, cz) if cz is not None else cz

        if pos not in self.arrival_chunks:
            raise ChunkDoesNotExistException(pos)

        if pos not in self.chunks:
            await self.load_chunk_from_saves(pos)

        return self.chunks[pos]

    async def load_chunk_from_saves(
        self, cx: typing.Tuple[int, int] | int, cz: int = None
    ):
        pos = (cx, cz) if cz is not None else cz

        self.chunks[pos] = Chunk(self, pos)
        # TODO: load

    async def get_name(self) -> str:
        return self.name

    def get_height_range(self) -> typing.Tuple[int, int]:
        return self.height_range

    async def get_loaded_chunks(self) -> typing.List[Chunk]:
        return list(self.chunks.values())

    async def create_chunk(
        self, cx: typing.Tuple[int, int] | int, cz: int = None
    ) -> Chunk:
        pos = (cx, cz) if cz is not None else cz
        chunk = Chunk(self, pos)
        self.chunks[cx, cz] = chunk
        self.arrival_chunks.add(pos)
        return chunk

    async def update_neighbor_visuals(self, position: typing.Tuple[int, int, int]):
        x, y, z = position

        for dx, dy, dz in (
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1),
        ):
            try:
                block = await self.get_block(x + dx, y + dy, z + dz)
            except ChunkDoesNotExistException:
                continue

            if block is not None:
                await block.chunk_section.update_block_visual(block)
