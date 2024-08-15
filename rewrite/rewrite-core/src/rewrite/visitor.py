from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar, Optional, Dict, List, Any, cast, Type, ClassVar

from rewrite import SourceFile, Tree, RecipeRunException
from rewrite.marker import Markers, Marker

O = TypeVar('O')
T = TypeVar('T', bound=Tree)
T2 = TypeVar('T2', bound=Tree)
P = TypeVar('P')


@dataclass(frozen=True)
class Cursor:
    ROOT_VALUE: ClassVar[str] = "root"

    parent: Optional[Cursor]
    value: object
    messages: Optional[Dict[str, object]] = None

    def get_message(self, key: str, default_value: O) -> O:
        return default_value if self.messages is None else cast(O, self.messages.get(key))


class TreeVisitor(Protocol[T, P]):
    _visit_count: int = 0
    _cursor: Cursor = Cursor(None, "root")
    _after_visit: Optional[List[TreeVisitor[Any, P]]]

    def is_acceptable(self, source_file: SourceFile, p: P) -> bool:
        return True

    @property
    def cursor(self) -> Cursor:
        return self._cursor

    @cursor.setter
    def cursor(self, cursor: Cursor) -> None:
        self._cursor = cursor

    def pre_visit(self, tree: T, p: P) -> Optional[T]:
        return cast(Optional[T], self.default_value(tree, p))

    def post_visit(self, tree: T, p: P) -> Optional[T]:
        return cast(Optional[T], self.default_value(tree, p))

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[T]:
        if parent is not None:
            self._cursor = parent

        if tree is None:
            return cast(Optional[T], self.default_value(None, p))

        top_level = False
        if self._visit_count == 0:
            top_level = True

        self._visit_count += 1
        self.cursor = Cursor(self._cursor, tree)

        t: Optional[T] = None
        is_acceptable = tree.is_acceptable(self, p) and (
                    not isinstance(tree, SourceFile) or self.is_acceptable(tree, p))

        try:
            if is_acceptable:
                t = self.pre_visit(cast(T, tree), p)
                if not self._cursor.get_message("STOP_AFTER_PRE_VISIT", False):
                    if t is not None:
                        t = t.accept(self, p)
                    if t is not None:
                        t = self.post_visit(t, p)

            self.cursor = self._cursor.parent # type: ignore

            if top_level:
                if t is not None and self._after_visit is not None:
                    for v in self._after_visit:
                        if v is not None:
                            v.cursor = self.cursor
                            t = v.visit(t, p)

                self._after_visit = None
                self._visit_count = 0

        except Exception as e:
            if isinstance(e, RecipeRunException):
                raise e

            raise RecipeRunException(e, self.cursor)

        return t if is_acceptable else cast(Optional[T], tree)

    def visit_and_cast(self, tree: Optional[Tree], t_type: Type[T2], p: P) -> T2:
        return cast(T2, self.visit(tree, p))

    def default_value(self, tree: Optional[Tree], p: P) -> Optional[Tree]:
        return tree

    def visit_markers(self, markers: Markers, p: P) -> Markers:
        if markers is None or markers is Markers.EMPTY:
            return Markers.EMPTY
        elif len(markers.markers) == 0:
            return markers
        return markers.with_markers([self.visit_marker(m, p) for m in markers.markers])

    def visit_marker(self, marker: Marker, p: P) -> Marker:
        return marker

    def adapt(self, tree_type, visitor_type) -> TreeVisitor[Tree, Any]:
        # FIXME implement the visitor adapting
        return self
