from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol, TypeVar, Type, Iterable, Optional, Set, runtime_checkable
from uuid import UUID

from rewrite import Marker, random_id


@runtime_checkable
class Style(Protocol):
    def merge(self, lower_precedence: Style) -> Style:
        return self

    def apply_defaults(self) -> Style:
        return self


S = TypeVar('S', bound=Style)


@dataclass(frozen=True)
class NamedStyles(Marker):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> NamedStyles:
        return self if id is self._id else replace(self, _id=id)

    _name: str
    _display_name: str
    _description: Optional[str]
    _tags: Set[str]
    _styles: Iterable[Style]

    @classmethod
    def merge(cls, style_type: Type[S], named_styles: Iterable[NamedStyles]) -> Optional[S]:
        merged = None
        for named_style in named_styles:
            styles = named_style._styles
            if styles is not None:
                for style in styles:
                    if isinstance(style, style_type):
                        style = style.apply_defaults()
                        if merged is None:
                            merged = style
                        else:
                            merged = merged.merge(style)
        return merged

    @classmethod
    def build(cls, *styles: Style, name: str = "Default", display_name: str = "Default", description: Optional[str] = None):
        return NamedStyles(random_id(), name, display_name, description, set(), styles)