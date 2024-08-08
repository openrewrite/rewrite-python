from typing import runtime_checkable, Protocol

from rewrite.core import Tree


@runtime_checkable
class Properties(Tree, Protocol):
    pass
