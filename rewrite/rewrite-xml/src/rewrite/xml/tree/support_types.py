from typing import Protocol, runtime_checkable, TypeVar

from rewrite import Tree


P = TypeVar('P')


@runtime_checkable
class Xml(Tree, Protocol):
    pass


class Content(Tree, Protocol):
    pass


class Misc(Tree, Protocol):
    pass
