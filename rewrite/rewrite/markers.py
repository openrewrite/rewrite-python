from __future__ import annotations

import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import List, ClassVar, cast, TYPE_CHECKING, Callable, TypeVar, Type
from uuid import UUID

if TYPE_CHECKING:
    from .parser import Parser
from .utils import random_id


class Marker(ABC):
    @property
    @abstractmethod
    def id(self) -> UUID:
        ...

    @abstractmethod
    def with_id(self, id: UUID) -> Marker:
        ...

    def __eq__(self, other: object) -> bool:
        if self.__class__ == other.__class__:
            return self.id == cast(Marker, other).id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


M = TypeVar('M', bound=Marker)

@dataclass(frozen=True, eq=False)
class Markers:
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Markers:
        return self if id is self._id else Markers(id, self._markers)

    _markers: List[Marker]

    @property
    def markers(self) -> List[Marker]:
        return self._markers

    def with_markers(self, markers: List[Marker]) -> Markers:
        return self if markers is self._markers else Markers(self._id, markers)

    def find_first(self, type: type):
        for marker in self.markers:
            if isinstance(marker, type):
                return marker
        return None

    def find_all(self, type: type):
        return [m for m in self.markers if isinstance(m, type)]

    def compute_if(self, condition: Callable[[Marker], bool], remap_fn: Callable[[Marker], Marker]) -> Markers:
        """
        Replace all markers that satisfy the condition with the result of the remapping function.

        :param condition: predicate to check if the marker should be remapped
        :param remap_fn: function to remap the marker
        :return: new Markers instance with the updated markers, or the same instance if no markers were updated
        """
        updated_markers = []
        for marker in self.markers:
            if condition(marker):
                updated_markers.append(remap_fn(marker))

        return Markers(self.id, updated_markers) if updated_markers else self

    def compute_by_type(self, cls: Type[M], remap_fn: Callable[[M], Marker]) -> Markers:
        """
        Replace all markers of the given type with the result of the function.

        :param cls: type of the markers to remap
        :param remap_fn: function to remap the marker
        :return: new Markers instance with the updated markers, or the same instance if no markers were updated
        """
        return self.compute_if(lambda m: isinstance(m, cls), remap_fn)

    EMPTY: ClassVar[Markers]

    def __eq__(self, other: object) -> bool:
        if self.__class__ == other.__class__:
            return self.id == cast(Markers, other).id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def build(cls, id, markers) -> Markers:
        return Markers(id, markers)


Markers.EMPTY = Markers(random_id(), [])


@dataclass(frozen=True, eq=False)
class ParseExceptionResult(Marker):
    @classmethod
    def build(cls, parser: 'Parser', exception: Exception) -> ParseExceptionResult:
        return cls(random_id(), type(parser).__name__, type(exception).__name__,
                   ''.join(traceback.format_exception(exception)))

    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ParseExceptionResult:
        return self if id is self._id else replace(self, _id=id)

    _parser_type: str

    @property
    def parser_type(self) -> str:
        return self._parser_type

    def with_parser_type(self, parser_type: str) -> ParseExceptionResult:
        return self if parser_type is self._parser_type else replace(self, _parser_type=parser_type)

    _exception_type: str

    @property
    def exception_type(self) -> str:
        return self._exception_type

    def with_exception_type(self, exception_type: str) -> ParseExceptionResult:
        return self if exception_type is self._exception_type else replace(self, _exception_type=exception_type)

    _message: str

    @property
    def message(self) -> str:
        return self._message

    def with_message(self, message: str) -> ParseExceptionResult:
        return self if message is self._message else replace(self, _message=message)
