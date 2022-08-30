from unittest import TestCase
from mcpython.backend.EventHandler import EventHandler
import asyncio


class TestEventHandler(TestCase):
    COUNTER = 0
    RESULTS = []

    async def target_invoke(self, *args, **kwargs):
        self.COUNTER += 1
        self.RESULTS.append((args, kwargs))

    def assertCalls(self, count: int, msg=""):
        self.assertEqual(count, self.COUNTER, msg)

    def setUp(self):
        self.COUNTER = 0
        self.RESULTS.clear()

    def test_event_name_double_register(self):
        instance = EventHandler()
        instance.register_event_type("test")
        self.assertRaises(ValueError, lambda: instance.register_event_type("test"))

    def test_register_for_not_present(self):
        instance = EventHandler()
        self.assertRaises(
            NameError, lambda: instance.subscribe("test", self.target_invoke)
        )
        self.assertCalls(0)

    def test_invoke(self):
        instance = EventHandler()
        instance.register_event_type("test")
        instance.subscribe("test", self.target_invoke)
        asyncio.get_event_loop().run_until_complete(instance.invoke_event("test"))
        self.assertCalls(1)

    def test_invoke_twice(self):
        instance = EventHandler()
        instance.register_event_type("test")
        instance.subscribe("test", self.target_invoke)
        asyncio.get_event_loop().run_until_complete(instance.invoke_event("test"))
        asyncio.get_event_loop().run_until_complete(instance.invoke_event("test"))
        self.assertCalls(2)

    def test_subscribe_twice(self):
        instance = EventHandler()
        instance.register_event_type("test")
        instance.subscribe("test", self.target_invoke)
        instance.subscribe("test", self.target_invoke)
        asyncio.get_event_loop().run_until_complete(instance.invoke_event("test"))
        self.assertCalls(2)

    def test_disable(self):
        instance = EventHandler()
        instance.register_event_type("test")
        instance.subscribe("test", self.target_invoke)
        instance.disable()
        asyncio.get_event_loop().run_until_complete(instance.invoke_event("test"))
        self.assertCalls(0)

    def test_sub_invoke(self):
        instance = EventHandler()
        instance.register_event_type("test")
        instance2 = instance.create_child_handler()
        instance2.subscribe("test", self.target_invoke)
        asyncio.get_event_loop().run_until_complete(instance.invoke_event("test"))
        self.assertCalls(1)

    def test_disable_sub(self):
        instance = EventHandler()
        instance.register_event_type("test")
        instance2 = instance.create_child_handler()
        instance2.subscribe("test", self.target_invoke)
        instance2.disable()
        asyncio.get_event_loop().run_until_complete(instance.invoke_event("test"))
        self.assertCalls(0)

    def test_disable_parent(self):
        instance = EventHandler()
        instance.register_event_type("test")
        instance2 = instance.create_child_handler()
        instance2.subscribe("test", self.target_invoke)
        instance.disable()
        asyncio.get_event_loop().run_until_complete(instance.invoke_event("test"))
        self.assertCalls(0)
