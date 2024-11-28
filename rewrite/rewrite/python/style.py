from dataclasses import dataclass

from ..style import Style, NamedStyles


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


class IntelliJ(NamedStyles):
    @classmethod
    def spaces(cls) -> SpacesStyle:
        return SpacesStyle(
            SpacesStyle.BeforeParentheses(
                method_call_parentheses=False,
                method_parentheses=False,
                left_bracket=False,
            ),
            SpacesStyle.AroundOperators(
                assignment=True,
                equality=True,
                relational=True,
                bitwise=True,
                additive=True,
                multiplicative=True,
                shift=True,
                power=True,
                eq_in_named_parameter=False,
                eq_in_keyword_argument=False,
            ),
            SpacesStyle.Within(
                brackets=False,
                method_parentheses=False,
                empty_method_parentheses=False,
                method_call_parentheses=False,
                empty_method_call_parentheses=False,
                braces=False,
            ),
            SpacesStyle.Other(
                before_comma=False,
                after_comma=True,
                before_for_semicolon=False,
                before_colon=False,
                after_colon=True,
                before_backslash=True,
                before_hash=True,
                after_hash=True,
            ),
        )
