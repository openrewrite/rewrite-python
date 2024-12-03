from typing import Callable, TypeVar, List, Union
from uuid import UUID, uuid4


def random_id() -> UUID:
    return uuid4()

T = TypeVar('T')

def map_list(lst: List[T], fn: Callable[[T], Union[T, None]]) -> List[T]:
    changed = False
    mapped_lst = []
    for original in lst:
        new = fn(original)
        if new is not None:
            mapped_lst.append(new)
            changed |= new is not original
        else:
            changed = True

    return mapped_lst if changed else lst
