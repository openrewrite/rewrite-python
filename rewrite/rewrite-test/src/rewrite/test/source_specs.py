from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True, eq=False)
class SourceSpec:
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    _parser: ParserBuilder

    @property
    def parser(self) -> ParserBuilder:
        return self._parser