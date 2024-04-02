from __future__ import annotations

import os
import pathlib
import typing

from mcpython.world.serialization.DataBuffer import ReadBuffer, WriteBuffer


if typing.TYPE_CHECKING:
    from mcpython.world.World import Chunk


class WorldStorage:
    def __init__(self):
        self.folder: pathlib.Path = None
        self.saved_chunks: set[tuple[int, int]] = set()

    def load_world(self, folder: pathlib.Path):
        self.folder = folder

        if folder.exists():
            for file in os.listdir(folder / "chunks"):
                self.saved_chunks.add(
                    typing.cast(
                        tuple[int, int],
                        tuple(map(int, file.removesuffix(".chunk").split("_"))),
                    )
                )

    def load_chunk(self, chunk: Chunk):
        if chunk.position not in self.saved_chunks:
            return

        file = self.folder / "chunks" / "{}_{}.chunk".format(*chunk.position)
        data = file.read_bytes()
        chunk.decode_instance(ReadBuffer(data))

    def save_chunk(self, chunk: Chunk):
        self.saved_chunks.add(chunk.position)
        file = self.folder / "chunks" / "{}_{}.chunk".format(*chunk.position)
        file.parent.mkdir(exist_ok=True, parents=True)
        writer = WriteBuffer()
        chunk.encode(writer)
        file.write_bytes(writer.get_data())
