from typing import Protocol, runtime_checkable

from rewrite.core import Tree


@runtime_checkable
class Xml(Tree, Protocol):
    pass


class Content(Tree, Protocol):
    pass


class Misc(Tree, Protocol):
    pass
