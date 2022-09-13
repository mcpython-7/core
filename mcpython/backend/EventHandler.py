import asyncio
import logging
import queue
import typing


class CombinedEventException(Exception):
    def __init__(self, children: typing.Iterable[Exception]):
        self.children = children
        super().__init__(repr(children))


class EventHandler:
    def __init__(self, name: str = "<unnamed event handler>"):
        self.name = name
        self.LOGGER = logging.getLogger(name)
        self._events: typing.Set[str] = set()
        self._event_queue = queue.Queue()
        self._subscribers: typing.Dict[
            str, typing.List[typing.Callable[[...], typing.Awaitable]]
        ] = {}
        self._children: typing.List[EventHandler] = []

        self.__enabled = True

    def enable(self):
        self.__enabled = True

    def disable(self):
        self.__enabled = False

    def subscribe(self, event: str, callback: typing.Callable[[...], typing.Awaitable]):
        if event not in self._events:
            raise NameError(f"event name '{event}' is not registered!")

        self._subscribers.setdefault(event, []).append(callback)
        return callback

    def create_child_handler(self, name=None) -> "EventHandler":
        instance = EventHandler(name or f"<child event handler of {self.name}>")
        instance._events = self._events
        self._children.append(instance)
        return instance

    def register_event_type(self, name: str):
        if name in self._events:
            raise ValueError(f"event name '{name}' is already registered!")

        self._events.add(name)
        self._subscribers.setdefault(name, [])

    def remove_event_type(self, name: str, discard_subscribers=True):
        self._events.remove(name)

        if discard_subscribers:
            del self._subscribers[name]

    async def invoke_event(
        self,
        name: str,
        args=tuple(),
        kwargs=None,
        run_parallel=True,
        ignore_exceptions=False,
        abort_on_exception=True,
    ):
        """
        Invokes the event in the handler

        :param name: the name of the event
        :param args: the args to use
        :param kwargs: the kwargs to use
        :param run_parallel: if events should be called in parallel or not
        :param ignore_exceptions: if exceptions should be ignored
        :param abort_on_exception: if to abort further execution if an exception is raised
        :raises NameError: if the event name is not registered
        :raises CombinedEventException: if run_parallel and not ignore_exceptions and exceptions are raised
        """

        if name not in self._events:
            raise NameError(f"event name '{name}' is not registered!")

        awaits = self._create_invoke_ables(name, args, kwargs or {})

        if run_parallel:
            exceptions = await asyncio.gather(*awaits)

            if any(e != None for e in exceptions):
                if not ignore_exceptions:
                    raise CombinedEventException(exceptions)
            else:
                pass

            return

        exceptions = []

        for sub in awaits:
            try:
                await sub
            except Exception as e:
                if ignore_exceptions:
                    continue

                if abort_on_exception:
                    raise e

                exceptions.append(e)

        if not ignore_exceptions and exceptions:
            raise CombinedEventException(exceptions)
        else:
            for exception in exceptions:
                self.LOGGER.exception(f"Error during invoking event {name}", exc_info=exception)

    async def invoke_cancelable(
        self,
        name: str,
        args=tuple(),
        kwargs=None,
        ignore_exceptions=False,
        abort_on_exception=True,
    ):
        if name not in self._events:
            raise NameError(f"event name '{name}' is not registered!")

        awaits = self._create_invoke_ables(name, args, kwargs or {})
        exceptions = []

        for sub in awaits:
            try:
                result = await sub

                if result is True:
                    break

            except Exception as e:
                if abort_on_exception:
                    if ignore_exceptions:
                        return

                    raise e

                elif ignore_exceptions:
                    continue

                exceptions.append(e)

        if not ignore_exceptions and exceptions:
            raise CombinedEventException(exceptions)
        else:
            for exception in exceptions:
                self.LOGGER.exception(f"Error during invoking event {name} (cancelable)", exc_info=exception)

    def _create_invoke_ables(self, event_name: str, args, kwargs):
        if not self.__enabled or event_name not in self._subscribers:
            return

        for sub in self._subscribers[event_name]:
            r = sub(*args, **kwargs)

            if not isinstance(r, typing.Awaitable):
                raise RuntimeError(f"no awaitable got back from {sub}")

            yield r

        for handler in self._children:
            yield from handler._create_invoke_ables(event_name, args, kwargs)

    def schedule_invoke_event(
        self,
        name: str,
        args=tuple(),
        kwargs=None,
        run_parallel=True,
        ignore_exceptions=False,
        abort_on_exception=True,
    ):
        self._event_queue.put(
            self.invoke_event(
                name, args, kwargs, run_parallel, ignore_exceptions, abort_on_exception
            )
        )

    async def invoke_event_queue(self):
        while self._event_queue.qsize() > 0:
            await self._event_queue.get()
