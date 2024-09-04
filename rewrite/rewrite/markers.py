from __future__ import annotations
import traceback

from dataclasses import dataclass, replace
from typing import List, Protocol, ClassVar, cast, runtime_checkable, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .parser import Parser
from .utils import random_id


@runtime_checkable
class Marker(Protocol):
    @property
    def id(self) -> UUID:
        ...

    def with_id(self, id: UUID) -> Marker:
        ...

    def __eq__(self, other: object) -> bool:
        if self.__class__ == other.__class__:
            return self.id == cast(Marker, other).id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


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

    EMPTY: ClassVar[Markers]

    def __eq__(self, other: object) -> bool:
        if self.__class__ == other.__class__:
            return self.id == cast(Markers, other).id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


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
