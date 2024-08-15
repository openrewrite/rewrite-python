from typing import Protocol, runtime_checkable, TypeVar, Any, Optional, TYPE_CHECKING

from rewrite import Tree, TreeVisitor

if TYPE_CHECKING:
    from rewrite.yaml.visitor import YamlVisitor

P = TypeVar('P')


@runtime_checkable
class Yaml(Tree, Protocol):
    def accept(self, v: TreeVisitor[Any, P], p: P) -> Optional[Any]:
        from rewrite.yaml.visitor import YamlVisitor
        return self.accept_yaml(v.adapt(Yaml, YamlVisitor), p)

    def accept_yaml(self, v: 'YamlVisitor[P]', p: P) -> Optional['Yaml']:
        ...


class YamlKey(Protocol):
    pass
