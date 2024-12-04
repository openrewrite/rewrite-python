from typing import Optional, cast, List

import rewrite.java as j
from rewrite import Tree
from rewrite.java import J, Assignment, JLeftPadded, AssignmentOperation, MemberReference, MethodInvocation, \
    MethodDeclaration, Empty, ArrayAccess, Space
from rewrite.python import PythonVisitor, SpacesStyle, Binary, ChainedAssignment
from rewrite.visitor import P


class SpacesVisitor(PythonVisitor):
    def __init__(self, style: SpacesStyle, stop_after: Tree = None):
        self._style = style
        self._before_parentheses = style.before_parentheses
        self._stop_after = stop_after

    def visit_method_declaration(self, method_declaration: MethodDeclaration, p: P) -> J:
        m: MethodDeclaration = cast(MethodDeclaration, super().visit_method_declaration(method_declaration, p))

        m = m.padding.with_parameters(
            self.space_before_container(m.padding.parameters, self._style.before_parentheses.method_declaration)
        )

        param_size = len(m.parameters)
        use_space = self._style.within.method_call_parentheses

        def _process_argument(index, arg, args_size):
            # TODO: Type expressions are not yet modified
            if index == 0:
                arg = arg.with_element(self.space_before(arg.element, use_space))
            else:
                arg = arg.with_element(self.space_before(arg.element, self._style.other.after_comma))

            if index == args_size - 1:
                arg = self.space_after(arg, use_space)
            else:
                arg = self.space_after(arg, self._style.other.before_comma)
            return arg

        m = m.padding.with_parameters(
            m.padding.parameters.padding.with_elements(
                [_process_argument(index, arg, param_size)
                 for index, arg in enumerate(m.padding.parameters.padding.elements)]
            )
        )

        # TODO: Type parameters are not supported yet
        if m.padding.type_parameters is not None:
            raise NotImplementedError("Type parameters are not supported yet")

        return m.padding.with_parameters(
            m.padding.parameters.with_before(
                Space.SINGLE_SPACE if self._before_parentheses.method_declaration else Space.EMPTY
            )
        )

    def visit_method_invocation(self, method_invocation: MethodInvocation, p: P) -> J:
        m: MethodInvocation = cast(MethodInvocation, super().visit_method_invocation(method_invocation, p))

        # Handle space before parenthesis for method e.g. foo (..) <-> foo(..)
        m = m.padding.with_arguments(m.padding.arguments.with_before(
            Space.SINGLE_SPACE if self._style.before_parentheses.method_call else Space.EMPTY))

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
        # TODO: Handle type parameters, relevant for constructors in Python.
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

    def visit_assignment(self, assignment: Assignment, p: P) -> J:
        """
        Handle assignment operator e.g. a = 1 <-> a=1
        """
        a: Assignment = cast(Assignment, super().visit_assignment(assignment, p))
        a = a.padding.with_assignment(
            self.space_before_jleftpadded(a.padding.assignment, self._style.around_operators.assignment))
        a = a.padding.with_assignment(
            a.padding.assignment.with_element(
                self.space_before(a.padding.assignment.element, self._style.around_operators.assignment)))
        return a

    def visit_assignment_operation(self, assignment_operation: AssignmentOperation, p: P) -> J:
        """
        Handle assignment operation e.g. a += 1 <-> a+=1
        """
        a: AssignmentOperation = cast(AssignmentOperation, super().visit_assignment_operation(assignment_operation, p))
        operator: JLeftPadded = a.padding.operator
        a = a.padding.with_operator(
            operator.with_before(update_space(operator.before, self._style.around_operators.assignment)))
        return a.with_assignment(self.space_before(a.assignment, self._style.around_operators.assignment))

    def visit_chained_assignment(self, chained_assignment: ChainedAssignment, p: P) -> J:
        """
        Handle chained assignment e.g. a = b = 1 <-> a=b=1
        """
        a: ChainedAssignment = cast(ChainedAssignment, super().visit_chained_assignment(chained_assignment, p))
        a = a.padding.with_variables(
            [v.with_after(update_space(v.after, self._style.around_operators.assignment)) for v in a.padding.variables])

        a = a.padding.with_variables(
            [v.with_element(
                self.space_before(v.element, self._style.around_operators.assignment if idx >= 1 else False)) for idx, v
                in enumerate(a.padding.variables)])

        return a.with_assignment(self.space_before(a.assignment, self._style.around_operators.assignment))

    def visit_member_reference(self, member_reference: MemberReference, p: P) -> J:
        m: MemberReference = cast(MemberReference, super().visit_member_reference(member_reference, p))

        if m.padding.type_parameters is not None:
            # TODO: Handle type parameters, relevant for constructors in Python.
            raise NotImplementedError("Type parameters are not supported yet")

        return m

    def visit_binary(self, binary: j.Binary, p: P) -> J:
        b: j.Binary = cast(j.Binary, super().visit_binary(binary, p))
        op: j.Binary.Type = b.operator

        # Additive operators, _self._style.around_operators.addition is True by default
        if op in [j.Binary.Type.Addition, j.Binary.Type.Subtraction]:
            b = self._apply_binary_space_around(b, self._style.around_operators.additive)
        elif op in [j.Binary.Type.Multiplication, j.Binary.Type.Division, j.Binary.Type.Modulo]:
            b = self._apply_binary_space_around(b, self._style.around_operators.multiplicative)
        elif op in [j.Binary.Type.LessThan, j.Binary.Type.GreaterThan, j.Binary.Type.LessThanOrEqual,
                    j.Binary.Type.GreaterThanOrEqual, j.Binary.Type.Equal, j.Binary.Type.NotEqual]:
            b = self._apply_binary_space_around(b, self._style.around_operators.relational)
        elif op in [j.Binary.Type.BitAnd, j.Binary.Type.BitOr, j.Binary.Type.BitXor]:
            b = self._apply_binary_space_around(b, self._style.around_operators.bitwise)
        elif op in [j.Binary.Type.LeftShift, j.Binary.Type.RightShift, j.Binary.Type.UnsignedRightShift]:
            b = self._apply_binary_space_around(b, self._style.around_operators.shift)
        elif op in [j.Binary.Type.Or, j.Binary.Type.And]:
            b = self._apply_binary_space_around(b, True)
        else:
            raise NotImplementedError(f"Operation {op} is not supported yet")

        return b

    def visit_python_binary(self, binary: Binary, p: P) -> J:
        b: Binary = cast(Binary, super().visit_python_binary(binary, p))
        op: Binary.Type = b.operator

        if op == Binary.Type.In or op == Binary.Type.Is or op == Binary.Type.IsNot or op == Binary.Type.NotIn:
            # TODO: Not sure what style options to use for these operators
            b = self._apply_binary_space_around(b, True)
        elif op == Binary.Type.FloorDivision or op == Binary.Type.MatrixMultiplication or op == Binary.Type.Power:
            b = self._apply_binary_space_around(b, self._style.around_operators.multiplicative)
        elif op == Binary.Type.StringConcatenation:
            b = self._apply_binary_space_around(b, self._style.around_operators.additive)
        return b

    def _apply_binary_space_around(self, binary, use_space_around: bool):
        operator = binary.padding.operator
        binary = binary.padding.with_operator(
            operator.with_before(update_space(operator.before, use_space_around))
        )
        binary = binary.with_right(self.space_before(binary.right, use_space_around))
        return binary

    @staticmethod
    def space_before(j: J, space_before: bool) -> J:
        space: Space = cast(Space, j.prefix)
        if space.comments or '\\' in space.whitespace:
            # don't touch whitespaces with comments or continuation characters
            return j

        return j.with_prefix(Space.SINGLE_SPACE if space_before else Space.EMPTY)

    @staticmethod
    def space_before_container(container: j.JContainer, space_before: bool) -> j.JContainer:
        if container.before.comments:
            # Perform the space rule for the suffix of the last comment only. Same as IntelliJ.
            comments: List[j.Comment] = SpacesVisitor.space_last_comment_suffix(container.before.comments, space_before)
            return container.with_before(container.before.with_comments(comments))

        if space_before and not_single_space(container.before.whitespace):
            return container.with_before(container.before.with_whitespace(" "))
        elif not space_before and only_spaces_and_not_empty(container.before.whitespace):
            return container.with_before(container.before.with_whitespace(""))
        else:
            return container

    @staticmethod
    def space_last_comment_suffix(comments: List[j.Comment], space_suffix: bool) -> List[j.Comment]:
        return [SpacesVisitor.space_suffix(comment, space_suffix) if i == len(comments) - 1 else comment for i, comment
                in
                enumerate(comments)]

    @staticmethod
    def space_suffix(comment: j.Comment, space_suffix: bool) -> j.Comment:
        if space_suffix and not_single_space(comment.suffix):
            return comment.with_suffix(" ")
        elif not space_suffix and only_spaces_and_not_empty(comment.suffix):
            return comment.with_suffix("")
        else:
            return comment

    @staticmethod
    def space_before_jleftpadded(j: JLeftPadded[J], space_before) -> JLeftPadded[J]:
        space: Space = cast(Space, j.before)
        if space.comments or '\\' in space.whitespace:
            # don't touch whitespaces with comments or continuation characters
            return j

        if space_before and not_single_space(space.whitespace):
            return j.with_before(space.with_whitespace(" "))
        elif not space_before and only_spaces_and_not_empty(space.whitespace):
            return j.with_before(space.with_whitespace(""))
        return j

    @staticmethod
    def space_after(j: J, space_after: bool) -> J:
        space: Space = cast(Space, j.after)
        if space.comments or '\\' in space.whitespace:
            # don't touch whitespaces with comments or continuation characters
            return j

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
