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
    mapped_lst = None

    with_index = len(inspect.signature(fn).parameters) == 2
    for index, original in enumerate(lst):
        new = fn(original, index) if with_index else fn(original)
        if new is None:
            if mapped_lst is None:
                mapped_lst = lst[:index]
            changed = True
        elif new is not original:
            if mapped_lst is None:
                mapped_lst = lst[:index]
            mapped_lst.append(new)
            changed = True
        elif mapped_lst is not None:
            mapped_lst.append(original)

    return mapped_lst if changed else lst
