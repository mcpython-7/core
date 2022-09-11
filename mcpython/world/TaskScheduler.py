import asyncio
import queue
import typing
import logging


class TaskScheduler:
    def __init__(self):
        self._invoke_on_tick = []
        self._special_invoke_on_tick = {}
        self._linear_callbacks = queue.Queue()

    def add_tick_callback(self, target: typing.Callable[[float], typing.Awaitable] | typing.Callable[[], typing.Awaitable], supress_exceptions=True):
        tar = target

        if target.__code__.co_argcount == 0:
            if not supress_exceptions:
                async def tar(dt):
                    try:
                        await target()
                    except Exception as e:
                        logging.error(e)
        elif not supress_exceptions:
            async def tar(dt):
                try:
                    await target(dt)
                except Exception as e:
                    logging.error(e)

        self._invoke_on_tick.append(tar)

        if tar != target:
            self._special_invoke_on_tick[target] = tar

    def remove_tick_callback(self, target: typing.Callable[[float], typing.Awaitable] | typing.Callable[[], typing.Awaitable]):
        if target in self._invoke_on_tick:
            self._invoke_on_tick.remove(target)
            return

        if target in self._special_invoke_on_tick:
            self._invoke_on_tick.remove(self._special_invoke_on_tick.pop(target))
            return

        raise ValueError(f"{target} is not registered for ticking!")

    def add_linear_callback(self, target: typing.Callable[[], typing.Awaitable] | typing.Awaitable):
        """
        Invokes the given 'target' (callable with awaitable or awaitable) as soon as possible on the main thread
        """
        self._linear_callbacks.put(target if isinstance(target, typing.Awaitable) else target())

    async def tick(self, dt: float):
        await asyncio.gather(*(
            func(dt)
            for func in self._invoke_on_tick
        ))

        while self._linear_callbacks.qsize() > 0:
            await self._linear_callbacks.get(False)


SCHEDULER = TaskScheduler()

