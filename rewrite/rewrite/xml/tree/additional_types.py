from typing import Protocol

from rewrite.core import Tree


class Content(Tree, Protocol):
    pass


class Misc(Tree, Protocol):
    pass
