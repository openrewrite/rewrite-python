from typing import Protocol, Any


class ExecutionContext(Protocol):
    def get_message(self, key: str, default_value=None) -> Any:
        ...

    def put_message(self, key: str, value: Any):
        ...


class DelegatingExecutionContext(ExecutionContext):
    def __init__(self, delegate):
        self._delegate = delegate

    def get_message(self, key, default_value=None):
        return self._delegate.get_message(key, default_value)

    def put_message(self, key, value):
        self._delegate.put_message(key, value)


class InMemoryExecutionContext(ExecutionContext):
    # FIXME implement
    pass


class RecipeRunException(Exception):
    # FIXME implement
    pass


class Recipe:
    # FIXME implement
    pass
