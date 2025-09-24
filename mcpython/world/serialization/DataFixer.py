from __future__ import annotations

import typing
from abc import ABC

from mcpython.world.serialization.DataBuffer import ReadBuffer, WriteBuffer


if typing.TYPE_CHECKING:
    from mcpython.world.serialization.IBufferSerializable import (
        IBufferSerializable,
        IBufferSerializableWithVersion,
    )

# Internal array for storing what classes can be serialized in what way
_BUFFER_SERIALIZABLE_ARRAY: list[type[IBufferSerializable]] = []


class AbstractDataFixer(ABC):
    @classmethod
    def register(
        cls, serialize_target: type[IBufferSerializableWithVersion], src_version: int
    ):
        serialize_target.DATA_FIXERS[src_version] = cls()

    def apply(
        self, read_buffer: ReadBuffer, write_buffer: WriteBuffer, context=None
    ) -> int:
        """
        Applies this datafixer on the read_buffer and writes into the write_buffer instance.
        'context' is the optional context object the data belongs to

        Must return the new 'version' of the data
        """
        raise NotImplementedError
