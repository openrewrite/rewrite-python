from dataclasses import dataclass

from ..style import Style


class PythonStyle(Style):
    pass


@dataclass(frozen=True)
class SpacesStyle(PythonStyle):
    @dataclass(frozen=True)
    class BeforeParentheses:
        method_call_parentheses: bool
        method_parentheses: bool
        left_bracket: bool

    @dataclass(frozen=True)
    class AroundOperators:
        assignment: bool
        equality: bool
        relational: bool
        bitwise: bool
        additive: bool
        multiplicative: bool
        shift: bool
        power: bool
        eq_in_named_parameter: bool
        eq_in_keyword_argument: bool

    @dataclass(frozen=True)
    class Within:
        brackets: bool
        method_parentheses: bool
        empty_method_parentheses: bool
        method_call_parentheses: bool
        empty_method_call_parentheses: bool
        braces: bool

    @dataclass(frozen=True)
    class Other:
        before_comma: bool
        after_comma: bool
        before_semicolon: bool
        before_for_semicolon: bool
        before_colon: bool
        after_colon: bool
        before_backslash: bool
        before_hash: bool
        after_hash: bool

    beforeParentheses: BeforeParentheses
    aroundOperators: AroundOperators
    within: Within
    other: Other
