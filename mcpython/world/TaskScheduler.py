import asyncio
import functools
import multiprocessing
import queue
import sys
import typing
import logging

import _queue


class TaskScheduler:
    def __init__(self):
        self._invoke_on_tick = []
        self._special_invoke_on_tick = {}
        self._linear_callbacks = queue.Queue()
        self._scheduled_in_ticks: typing.List[typing.List[typing.Awaitable]] = [
            [] for _ in range(20)
        ]

    def add_tick_callback(
        self,
        target: typing.Callable[[float], typing.Awaitable]
        | typing.Callable[[], typing.Awaitable],
        supress_exceptions=True,
    ):
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

    def remove_tick_callback(
        self,
        target: typing.Callable[[float], typing.Awaitable]
        | typing.Callable[[], typing.Awaitable],
    ):
        if target in self._invoke_on_tick:
            self._invoke_on_tick.remove(target)
            return

        if target in self._special_invoke_on_tick:
            self._invoke_on_tick.remove(self._special_invoke_on_tick.pop(target))
            return

        raise ValueError(f"{target} is not registered for ticking!")

    def add_linear_callback(
        self, target: typing.Callable[[], typing.Awaitable] | typing.Awaitable
    ):
        """
        Invokes the given 'target' (callable with awaitable or awaitable) as soon as possible on the main thread
        """
        self._linear_callbacks.put(
            target if isinstance(target, typing.Awaitable) else target()
        )

    def add_invoke_in_ticks(
        self,
        target: typing.Callable[[], typing.Awaitable] | typing.Awaitable,
        ticks: int,
    ):
        if ticks > len(self._scheduled_in_ticks):
            self._scheduled_in_ticks += [
                [] for _ in range(ticks - len(self._scheduled_in_ticks))
            ]

        self._scheduled_in_ticks[ticks].append(
            target if isinstance(target, typing.Awaitable) else target()
        )

    async def tick(self, dt: float):
        await asyncio.gather(*(func(dt) for func in self._invoke_on_tick))

        this_ticks = self._scheduled_in_ticks.pop(0)
        await asyncio.gather(*this_ticks)
        del this_ticks
        self._scheduled_in_ticks.append([])

        while self._linear_callbacks.qsize() > 0:
            await self._linear_callbacks.get(False)


class OffProcessWorker:
    CURRENT_PROCESS = None
    WORKER_LOGGER = logging.getLogger(__name__)

    @classmethod
    def _exit(cls):
        cls.WORKER_LOGGER.fatal("Stopping Worker Process!")
        sys.exit(1)

    @classmethod
    async def _run_target_with_callback(
        cls,
        target: typing.Callable[[], typing.Awaitable] | typing.Awaitable,
        callback: typing.Callable[[object], typing.Awaitable],
    ):
        target = target if isinstance(target, typing.Awaitable) else target()
        result = await target

        WORKER.result_data_queue.put(functools.partial(callback, result))

    def __init__(self):
        self.task_queue = multiprocessing.Queue()
        self.result_data_queue = multiprocessing.Queue()

    def put_task(self, target: typing.Callable[[], typing.Awaitable | object]):
        self.task_queue.put(target)

    def put_task_with_callback(
        self,
        target: typing.Callable[[], typing.Awaitable | object],
        callback: typing.Callable[[object], typing.Awaitable | object],
    ):
        self.put_task(
            functools.partial(self._run_target_with_callback, target, callback)
        )

    def start(self):
        OffProcessWorker.CURRENT_PROCESS = multiprocessing.Process(
            target=OffProcessWorker.target, args=(self,), name="mcpython worker process"
        )
        OffProcessWorker.CURRENT_PROCESS.start()

        SCHEDULER.add_tick_callback(self.fetch_results)

    async def fetch_results(self, dt: float = 0):
        while not self.result_data_queue.empty():
            try:
                r = self.result_data_queue.get()
                if callable(r):
                    r = r()
                if isinstance(r, typing.Awaitable):
                    await r
            except Exception as e:
                self.WORKER_LOGGER.error(e)

    def stop(self):
        try:
            while True:
                self.task_queue.get(block=False)
        except _queue.Empty:
            pass

        self.task_queue.put(self._exit)

    def target(self):
        global WORKER
        WORKER = self

        self.WORKER_LOGGER.info("Starting Worker Process...")

        while True:
            task = self.task_queue.get()

            try:
                result = task()
                if isinstance(result, typing.Awaitable):
                    # todo: maybe async this?
                    asyncio.run(result)
            except Exception as e:
                self.WORKER_LOGGER.error(e)


SCHEDULER = TaskScheduler()
WORKER = OffProcessWorker()
