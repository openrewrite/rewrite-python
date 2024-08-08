from typing import Protocol, runtime_checkable

from rewrite.core import Tree


@runtime_checkable
class Yaml(Tree, Protocol):
    pass


class YamlKey(Protocol):
    pass
