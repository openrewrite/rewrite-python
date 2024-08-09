from typing import Protocol, runtime_checkable, TypeVar

from rewrite import Tree


P = TypeVar('P')


@runtime_checkable
class Yaml(Tree, Protocol):
    pass


class YamlKey(Protocol):
    pass
