from __future__ import annotations

import weakref
from typing import List, Optional, Protocol, TypeVar, Generic, ClassVar

from attr import dataclass

from rewrite.core import Tree, SourceFile
from rewrite.core.marker import Markers
from rewrite.java.tree.tree import J


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

class JavaSourceFile(SourceFile, Protocol):
    pass


class Expression(Tree, Protocol):
    pass


class Statement(Tree, Protocol):
    pass


class NameTree(Tree, Protocol):
    pass


class TypeTree(Tree, Protocol):
    pass


class TypedTree(Tree, Protocol):
    pass


class Loop(Tree, Protocol):
    pass


class MethodCall(Tree, Protocol):
    pass


class JavaType(Protocol):
    pass


T = TypeVar('T')
J2 = TypeVar('J2', bound=J)


@dataclass(frozen=True)
class JRightPadded(Generic[T]):
    _element: T

    @property
    def element(self) -> T:
        return self._element

    def with_element(self, element: T) -> JRightPadded[T]:
        return self if element is self._element else JRightPadded(element, self._after, self._markers)

    _after: Space

    @property
    def after(self) -> Space:
        return self._after

    def with_after(self, after: Space) -> JRightPadded[T]:
        return self if after is self._after else JRightPadded(self._element, after, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JRightPadded[T]:
        return self if markers is self._markers else JRightPadded(self._element, self._after, markers)

    @classmethod
    def get_elements(cls, padded_list: List[JRightPadded[T]]) -> List[T]:
        return [x.element for x in padded_list]

    @classmethod
    def with_elements(cls, padded_list: List[JRightPadded[T]], elements: List[T]) -> List[JRightPadded[T]]:
        # TODO implement
        pass


@dataclass(frozen=True)
class JLeftPadded(Generic[T]):
    _before: Space

    @property
    def before(self) -> Space:
        return self._before

    def with_before(self, before: Space) -> JLeftPadded[T]:
        return self if before is self._before else JLeftPadded(before, self._element, self._markers)

    _element: T

    @property
    def element(self) -> T:
        return self._element

    def with_element(self, element: T) -> JLeftPadded[T]:
        return self if element is self._element else JLeftPadded(self._before, element, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JLeftPadded[T]:
        return self if markers is self._markers else JLeftPadded(self._before, self._element, markers)

    @classmethod
    def get_elements(cls, padded_list: List[JLeftPadded[T]]) -> List[T]:
        return [x.element for x in padded_list]

    @classmethod
    def with_elements(cls, padded_list: List[JLeftPadded[T]], elements: List[T]) -> List[JLeftPadded[T]]:
        # TODO implement
        pass


@dataclass(frozen=True)
class JContainer(Generic[T]):
    _before: Space

    @property
    def before(self) -> Space:
        return self._before

    def with_before(self, before: Space) -> JContainer[T]:
        return self if before is self._before else JContainer(before, self._elements, self._markers)

    _elements: List[JRightPadded[T]]

    @property
    def elements(self) -> List[T]:
        return JRightPadded.get_elements(self._elements)

    def with_elements(self, elements: List[T]) -> JContainer[T]:
        return self.padding.with_elements(JRightPadded.with_elements(self._elements, elements))

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JContainer[T]:
        return self if markers is self._markers else JContainer(self._before, self._elements, markers)

    @dataclass
    class PaddingHelper:
        _t: JContainer[T]

        @property
        def elements(self) -> List[JRightPadded[T]]:
            return self._t._elements

        def with_elements(self, elements: List[JRightPadded[T]]) -> JContainer[T]:
            return self._t if self._t._elements is elements else JContainer(self._t._before, elements, self._t._markers)

    _padding: weakref.ReferenceType[JContainer.PaddingHelper] = None

    @property
    def padding(self) -> JContainer.PaddingHelper:
        p: JContainer.PaddingHelper
        if self._padding is None:
            p = JContainer.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = JContainer.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    @classmethod
    def with_elements_nullable(cls, before: Optional[JContainer[J2]], elements: Optional[List[J2]]) -> Optional[JContainer[J2]]:
        if elements is None or elements == []:
            return None
        if before is None:
            return JContainer(Space.EMPTY, elements, Markers.EMPTY)
        return before.padding.with_elements(JRightPadded.with_elements(before._elements, elements))
