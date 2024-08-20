from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol, TypeVar, Generic, runtime_checkable, Dict, ClassVar, Any
from uuid import UUID

from rewrite import Tree, TreeVisitor
from rewrite.marker import Markers

P = TypeVar('P')
J2 = TypeVar('J2', bound='Json')


@runtime_checkable
class Json(Tree, Protocol):
    def accept(self, v: TreeVisitor[Any, P], p: P) -> Optional[Any]:
        from rewrite.json.visitor import JsonVisitor
        return self.accept_json(v.adapt(Json, JsonVisitor), p)

    def accept_json(self, v: 'JsonVisitor[P]', p: P) -> Optional['Json']:
        ...


@dataclass(frozen=True)
class Comment:
    _multiline: bool

    @property
    def multiline(self) -> bool:
        return self._multiline

    def with_multiline(self, multiline: bool) -> Comment:
        return self if multiline is self._multiline else Comment(multiline, self._text, self._suffix, self._markers)

    _text: str

    @property
    def text(self) -> str:
        return self._text

    def with_text(self, text: str) -> Comment:
        return self if text is self._text else Comment(self._multiline, text, self._suffix, self._markers)

    _suffix: str

    @property
    def suffix(self) -> str:
        return self._suffix

    def with_suffix(self, suffix: str) -> Comment:
        return self if suffix is self._suffix else Comment(self._multiline, self._text, suffix, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Comment:
        return self if markers is self._markers else Comment(self._multiline, self._text, self._suffix, markers)


@dataclass(frozen=True)
class Space:
    _comments: List[Comment]

    @property
    def comments(self) -> List[Comment]:
        return self._comments

    def with_comments(self, comments: List[Comment]) -> Space:
        return self if comments is self._comments else Space(comments, self._whitespace)

    _whitespace: Optional[str]

    @property
    def whitespace(self) -> Optional[str]:
        return self._whitespace

    def with_whitespace(self, whitespace: Optional[str]) -> Space:
        return self if whitespace is self._whitespace else Space(self._comments, whitespace)

    EMPTY: ClassVar[Space] = None


Space.EMPTY = Space([], '')


class JsonValue(Json, Protocol):
    pass


class JsonKey(Json, Protocol):
    pass


T = TypeVar('T', bound=Json)


@dataclass
class JsonRightPadded(Generic[T]):
    _element: T

    @property
    def element(self) -> T:
        return self._element

    def with_element(self, element: T) -> JsonRightPadded[T]:
        return self if element is self._element else JsonRightPadded(element, self._after, self._markers)

    _after: Space

    @property
    def after(self) -> Space:
        return self._after

    def with_after(self, after: Space) -> JsonRightPadded[T]:
        return self if after is self._after else JsonRightPadded(self._element, after, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JsonRightPadded[T]:
        return self if markers is self._markers else JsonRightPadded(self._element, self._after, markers)

    @classmethod
    def get_elements(cls, list: List[JsonRightPadded[T]]) -> List[T]:
        return [x.element for x in list]

    @classmethod
    def with_elements(cls, before: List[JsonRightPadded[J2]], elements: List[J2]) -> List[JsonRightPadded[J2]]:
        # a cheaper check for the most common case when there are no changes
        if len(elements) == len(before):
            has_changes = False
            for i in range(len(before)):
                if before[i].element != elements[i]:
                    has_changes = True
                    break
            if not has_changes:
                return before
        elif not elements:
            return []

        after: List[JsonRightPadded[J2]] = []
        before_by_id: Dict[UUID, JsonRightPadded[J2]] = {}

        for j in before:
            if j.element.id in before_by_id:
                raise Exception("Duplicate key")
            before_by_id[j.element.id] = j

        for t in elements:
            found = before_by_id.get(t.id)
            if found is not None:
                after.append(found.with_element(t))
            else:
                after.append(JsonRightPadded(t, Space.EMPTY, Markers.EMPTY))

        return after
