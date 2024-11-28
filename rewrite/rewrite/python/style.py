from dataclasses import dataclass
from typing import Protocol

from ..style import Style, NamedStyles


class PythonStyle(Style, Protocol):
    pass


@dataclass(frozen=True)
class SpacesStyle(PythonStyle):
    @dataclass(frozen=True)
    class BeforeParentheses:
        _method_call: bool
        _method_declaration: bool
        _left_bracket: bool

    @dataclass(frozen=True)
    class AroundOperators:
        _assignment: bool
        _equality: bool
        _relational: bool
        _bitwise: bool
        _additive: bool
        _multiplicative: bool
        _shift: bool
        _power: bool
        _eq_in_named_parameter: bool
        _eq_in_keyword_argument: bool

    @dataclass(frozen=True)
    class Within:
        _brackets: bool
        _method_declaration_parentheses: bool
        _empty_method_declaration_parentheses: bool
        _method_call_parentheses: bool
        _empty_method_call_parentheses: bool
        _braces: bool

    @dataclass(frozen=True)
    class Other:
        _before_comma: bool
        _after_comma: bool
        _before_for_semicolon: bool
        _before_colon: bool
        _after_colon: bool
        _before_backslash: bool
        _before_hash: bool
        _after_hash: bool

    beforeParentheses: BeforeParentheses
    aroundOperators: AroundOperators
    within: Within
    other: Other


class IntelliJ(NamedStyles):
    @classmethod
    def spaces(cls) -> SpacesStyle:
        return SpacesStyle(
            SpacesStyle.BeforeParentheses(
                _method_call=False,
                _method_declaration=False,
                _left_bracket=False,
            ),
            SpacesStyle.AroundOperators(
                _assignment=True,
                _equality=True,
                _relational=True,
                _bitwise=True,
                _additive=True,
                _multiplicative=True,
                _shift=True,
                _power=True,
                _eq_in_named_parameter=False,
                _eq_in_keyword_argument=False,
            ),
            SpacesStyle.Within(
                _brackets=False,
                _method_declaration_parentheses=False,
                _empty_method_declaration_parentheses=False,
                _method_call_parentheses=False,
                _empty_method_call_parentheses=False,
                _braces=False,
            ),
            SpacesStyle.Other(
                _before_comma=False,
                _after_comma=True,
                _before_for_semicolon=False,
                _before_colon=False,
                _after_colon=True,
                _before_backslash=True,
                _before_hash=True,
                _after_hash=True,
            ),
        )
