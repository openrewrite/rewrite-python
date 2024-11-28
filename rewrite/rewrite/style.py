from __future__ import annotations

from typing import Protocol


class Style(Protocol):
    def merge(self, lower_precedence: Style) -> Style:
        ...

    def apply_defaults(self) -> Style:
        return self
