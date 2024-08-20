from typing import Protocol, runtime_checkable, TypeVar, Any, Optional

from rewrite import Tree, TreeVisitor

P = TypeVar('P')


@runtime_checkable
class Xml(Tree, Protocol):
    def accept(self, v: TreeVisitor[Any, P], p: P) -> Optional[Any]:
        from rewrite.xml.visitor import XmlVisitor
        return self.accept_xml(v.adapt(Xml, XmlVisitor), p)

    def accept_xml(self, v: 'XmlVisitor[P]', p: P) -> Optional['Xml']:
        ...


class Content(Tree, Protocol):
    pass


class Misc(Tree, Protocol):
    pass
