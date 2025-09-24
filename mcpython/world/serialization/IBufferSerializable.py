from __future__ import annotations

from abc import ABC

from mcpython.world.serialization.DataBuffer import (
    ReadBuffer,
    WriteBuffer,
    _UINT16,
)
from mcpython.world.serialization.DataFixer import (
    _BUFFER_SERIALIZABLE_ARRAY,
    AbstractDataFixer,
)


class IBufferSerializable(ABC):
    @classmethod
    def __init_subclass__(cls) -> None:
        if cls.decode != IBufferSerializable.decode:
            _BUFFER_SERIALIZABLE_ARRAY.append(cls)

    @classmethod
    def decode(cls, buffer: ReadBuffer):
        raise NotImplementedError

    def encode(self, buffer: WriteBuffer):
        raise NotImplementedError


class IBufferSerializableWithVersion(IBufferSerializable, ABC):
    VERSION = 0
    _VERSION_SIZE = _UINT16
    DATA_FIXERS: dict[int, AbstractDataFixer] = {}

    @classmethod
    def decode_datafixable(cls, read_buffer: ReadBuffer, context=None) -> ReadBuffer:
        version = read_buffer.read_singleton_struct(cls._VERSION_SIZE)

        while version < cls.VERSION:
            fixer = cls.DATA_FIXERS.get(version)
            if fixer is None:
                raise RuntimeError(
                    f"Cannot fix stream from {cls} in version {version} to the current version, {cls.VERSION},"
                    f" as no datafixer exists!"
                )
            target = WriteBuffer()
            version = fixer.apply(read_buffer, target, context=context)
            read_buffer = target.start_read()

        return read_buffer

    def encode_datafixable(self, write_buffer: WriteBuffer):
        write_buffer.write_singleton_struct(self._VERSION_SIZE, self.VERSION)
