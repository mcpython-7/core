import asyncio
import queue
import typing


class CombinedEventException(Exception):
    def __init__(self, children: typing.Iterable[Exception]):
        self.children = children
        super().__init__(repr(children))


class EventHandler:
    def __init__(self):
        self.events: typing.Set[str] = set()
        self.event_queue = queue.Queue()
        self.subscribers: typing.Dict[str, typing.List[typing.Callable[[...], typing.Awaitable]]] = {}

    def register_event_type(self, name: str):
        if name in self.events:
            raise ValueError(f"event name '{name}' is already registered!")

        self.events.add(name)
        self.subscribers.setdefault(name, [])

    def remove_event_type(self, name: str, discard_subscribers=True):
        self.events.remove(name)

        if discard_subscribers:
            del self.subscribers[name]

    async def invoke_event(self, name: str, args=tuple(), kwargs=None, run_parallel=True, ignore_exceptions=False):
        """
        Invokes the event in the handler

        :param name: the name of the event
        :param args: the args to use
        :param kwargs: the kwargs to use
        :param run_parallel: if events should be called in parallel or not
        :param ignore_exceptions: if exceptions should be ignored
        :raises NameError: if the event name is not registered
        :raises CombinedEventException: if run_parallel and not ignore_exceptions and exceptions are raised
        """

        if name not in self.events:
            raise NameError(f"event name '{name}' is not registered!")

        awaits = self.__create_invoke_ables(self.subscribers[name], args, kwargs or {})

        if run_parallel:
            exceptions = await asyncio.gather(
                *awaits
            )

            if exceptions and not ignore_exceptions:
                raise CombinedEventException(exceptions)

            return

        exceptions = []

        for sub in awaits:
            try:
                await sub
            except Exception as e:
                if ignore_exceptions: continue

                exceptions.append(e)

        if not ignore_exceptions and exceptions:
            raise CombinedEventException(exceptions)

    def __create_invoke_ables(self, subscribers: typing.List[typing.Callable], args, kwargs):
        for sub in subscribers:
            r = sub(*args, **kwargs)

            if not isinstance(r, typing.Awaitable):
                raise RuntimeError(f"no awaitable got back from {sub}")

            yield r

    def schedule_invoke_event(self, name: str, args=tuple(), kwargs=None, run_parallel=True, ignore_exceptions=False):
        self.event_queue.put(self.invoke_event(name, args, kwargs, run_parallel, ignore_exceptions))

    async def invoke_event_queue(self):
        while self.event_queue.qsize() > 0:
            await self.event_queue.get()

