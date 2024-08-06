from __future__ import annotations

from typing import List, Optional, Protocol, TypeVar, Generic

from attr import dataclass

from rewrite.core import Tree, SourceFile
from rewrite.core.marker import Markers
from rewrite.json.tree.tree import Json


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


T = TypeVar('T', bound=Json)

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


@dataclass
class JContainer(Generic[T]):
    pass