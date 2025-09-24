from unittest import TestCase

from mcpython.world.serialization.DataFixer import AbstractDataFixer
from mcpython.world.serialization.DataBuffer import (
    ReadBuffer,
    WriteBuffer,
)
from mcpython.world.serialization.IBufferSerializable import (
    IBufferSerializableWithVersion,
)


class TestDatafixerInterface(TestCase):
    def test_simple(self):
        class V1(IBufferSerializableWithVersion):
            VERSION = 1

            def encode(self, buffer: WriteBuffer):
                self.encode_datafixable(buffer)
                buffer.write_int8(self.VERSION)

        class V2(IBufferSerializableWithVersion):
            VERSION = 2

            @classmethod
            def decode(cls, buffer: ReadBuffer):
                buffer = cls.decode_datafixable(buffer)
                obj = cls()
                obj.version = buffer.read_int8()
                return obj

        class DatafixerV1to2(AbstractDataFixer):
            @classmethod
            def apply(
                self, read_buffer: ReadBuffer, write_buffer: WriteBuffer, context=None
            ) -> int:
                assert read_buffer.read_int8() == 1
                write_buffer.write_int8(2)
                return 2

        DatafixerV1to2.register(V2, 1)

        obj = V1()
        buffer = WriteBuffer()
        obj.encode(buffer)
        buffer = ReadBuffer(buffer.get_data())
        obj2 = V2.decode(buffer)
        assert obj2.version == obj2.VERSION
