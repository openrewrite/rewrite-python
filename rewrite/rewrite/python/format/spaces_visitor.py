from typing import Optional, cast, TypeVar

from rewrite import Tree
from rewrite.java import J
from rewrite.java import MethodInvocation, MethodDeclaration, Empty, ArrayAccess, Space
from rewrite.python import PythonVisitor, SpacesStyle
from rewrite.visitor import P

J2 = TypeVar('J2', bound=J)


class SpacesVisitor(PythonVisitor):
    def __init__(self, style: SpacesStyle, stop_after: Tree = None):
        self._style = style
        self._before_parentheses = style.before_parentheses
        self._stop_after = stop_after

    def visit_method_declaration(self, method_declaration: MethodDeclaration, p: P) -> J:
        md: MethodDeclaration = cast(MethodDeclaration, super().visit_method_declaration(method_declaration, p))
        return md.padding.with_parameters(
            md.padding.parameters.with_before(
                Space.SINGLE_SPACE if self._before_parentheses.method_declaration else Space.EMPTY
            )
        )

    def visit_method_invocation(self, method_invocation: MethodInvocation, p: P) -> J:
        m: MethodInvocation = cast(MethodInvocation, super().visit_method_invocation(method_invocation, p))

        if not m.arguments or isinstance(m.arguments[0], Empty):
            # Handle within method call parenthesis with no arguments e.g. foo() <-> foo( )
            use_space = self._style.within.empty_method_call_parentheses
            m = m.padding.with_arguments(
                m.padding.arguments.padding.with_elements(
                    [arg.with_element(self.space_before(arg.element, use_space)) for arg in
                     m.padding.arguments.padding.elements]
                )
            )
        else:
            # Handle:
            # - Within method call parenthesis with arguments e.g. foo( 1, 2 ) <-> foo(1, 2).
            #   Note: this only applies to the space left of the first argument and right of the last argument.
            # - Space after comma e.g. foo(1,2,3) <-> foo(1, 2, 3)
            args_size = len(m.arguments)
            use_space = self._style.within.method_call_parentheses

            def _process_argument(index, arg, args_size, use_space):
                if index == 0:
                    arg = arg.with_element(self.space_before(arg.element, use_space))
                else:
                    arg = arg.with_element(self.space_before(arg.element, self._style.other.after_comma))

                if index == args_size - 1:
                    arg = self.space_after(arg, use_space)
                else:
                    arg = self.space_after(arg, self._style.other.before_comma)

                return arg

            m = m.padding.with_arguments(
                m.padding.arguments.padding.with_elements(
                    [_process_argument(index, arg, args_size, use_space)
                     for index, arg in enumerate(m.padding.arguments.padding.elements)]
                )
            )

        # Handle space before parenthesis for method e.g. foo (..) <-> foo(..)
        m = m.padding.with_arguments(
            m.padding.arguments.with_before(
                Space.SINGLE_SPACE if self._style.before_parentheses.method_call else Space.EMPTY)
        )

        return m

    def visit_array_access(self, array_access: ArrayAccess, p: P) -> J:
        a: ArrayAccess = cast(ArrayAccess, super().visit_array_access(array_access, p))
        use_space_within_brackets = self._style.within.brackets
        index_padding = a.dimension.padding.index
        element_prefix = update_space(index_padding.element.prefix, use_space_within_brackets)
        index_after = update_space(index_padding.after, use_space_within_brackets)

        a = a.with_dimension(
            a.dimension.padding.with_index(
                index_padding.with_element(
                    index_padding.element.with_prefix(element_prefix)
                ).with_after(index_after)
            ).with_prefix(update_space(a.dimension.prefix, self._style.before_parentheses.left_bracket))
        )
        return a

    def space_before(self, j: J2, space_before: bool) -> J2:
        space: Space = cast(Space, j.prefix)
        if space.comments or '\\' in space.whitespace:
            # don't touch whitespaces with comments or continuation characters
            return j

        return j.with_prefix(Space.SINGLE_SPACE if space_before else Space.EMPTY)

    def space_after(self, j: J2, space_after: bool) -> J2:
        space: Space = cast(Space, j.after)
        if space.comments or '\\' in space.whitespace:
            # don't touch whitespaces with comments or continuation characters
            return j
        #
        if space_after and not_single_space(space.whitespace):
            return j.with_after(space.with_whitespace(" "))
        elif not space_after and only_spaces_and_not_empty(space.whitespace):
            return j.with_after(space.with_whitespace(""))
        return j


def update_space(s: Space, have_space: bool) -> Space:
    if s.comments:
        return s

    if have_space and not_single_space(s.whitespace):
        return s.with_whitespace(" ")
    elif not have_space and only_spaces_and_not_empty(s.whitespace):
        return s.with_whitespace("")
    else:
        return s


def only_spaces(s: Optional[str]) -> bool:
    return s is not None and all(c in {' ', '\t'} for c in s)


def only_spaces_and_not_empty(s: Optional[str]) -> bool:
    return bool(s) and only_spaces(s)


def not_single_space(s: Optional[str]) -> bool:
    return s is not None and only_spaces(s) and s != " "
