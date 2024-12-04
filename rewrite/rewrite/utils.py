import inspect
from typing import Callable, TypeVar, List, Union
from uuid import UUID, uuid4


def random_id() -> UUID:
    return uuid4()

T = TypeVar('T')

# Define a type that allows both single and two-argument callables
FnType = Union[Callable[[T], Union[T, None]], Callable[[T, int], Union[T, None]]]

def list_map(fn: FnType, lst: List[T]) -> List[T]:
    changed = False
    mapped_lst = []

    if len(inspect.signature(fn).parameters) == 1:
        for original in lst:
            new = fn(original)
            if new is not None:
                mapped_lst.append(new)
                changed |= new is not original
            else:
                changed = True
    else:
        for index, original in enumerate(lst):
            new = fn(original, index)
            if new is not None:
                mapped_lst.append(new)
                changed |= new is not original
            else:
                changed = True

    return mapped_lst if changed else lst
