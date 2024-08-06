from __future__ import annotations

import weakref
from dataclasses import replace
from typing import List, Optional, Protocol, TypeVar, Generic

from attr import dataclass

from rewrite.core import Tree, SourceFile
from rewrite.core.marker import Markers


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


@dataclass
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
    def get_elements(cls, list: List[JRightPadded[T]]) -> List[T]:
        return [x.element for x in list]

    @classmethod
    def with_elements(cls, list: List[JRightPadded[T]], elements: List[T]) -> List[JRightPadded[T]]:
        # TODO implement
        pass


@dataclass
class JLeftPadded(Generic[T]):
    pass


@dataclass(frozen=True)
class JContainer(Generic[T]):
    _before: Space

    @property
    def before(self) -> Space:
        return self._before

    def with_before(self, before: Space) -> JContainer[T]:
        return self if before is self._before else replace(self, _before=before)

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
        return self if markers is self._markers else replace(self, _markers=markers)

    @dataclass
    class PaddingHelper:
        _t: JContainer[T]

        @property
        def elements(self) -> List[JRightPadded[T]]:
            return self._t._elements

        def with_elements(self, elements: List[JRightPadded[T]]) -> JContainer[T]:
            return self._t if self._t._elements is elements else replace(self._t, _elements=elements)

    _padding: weakref.ReferenceType[JContainer.PaddingHelper] = None

    @property
    def padding(self) -> JContainer.PaddingHelper:
        p: JContainer.PaddingHelper
        if self._padding is None:
            p = JContainer.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = JContainer.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p
