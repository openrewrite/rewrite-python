from typing import Optional, cast, List, TypeVar

import rewrite.java as j
from rewrite import Tree, list_map
from rewrite.java import J, Assignment, JLeftPadded, AssignmentOperation, MemberReference, MethodInvocation, \
    MethodDeclaration, Empty, ArrayAccess, Space, If, Block, ClassDeclaration, VariableDeclarations, JRightPadded, \
    Import
from rewrite.python import PythonVisitor, SpacesStyle, Binary, ChainedAssignment, Slice, CollectionLiteral, \
    ForLoop, DictLiteral, KeyValue, TypeHint, MultiImport
from rewrite.visitor import P


class SpacesVisitor(PythonVisitor):
    def __init__(self, style: SpacesStyle, stop_after: Tree = None):
        self._style = style
        self._before_parentheses = style.before_parentheses
        self._stop_after = stop_after

    def visit_class_declaration(self, class_declaration: ClassDeclaration, p: P) -> J:
        c = cast(ClassDeclaration, super().visit_class_declaration(class_declaration, p))

        # Handle space before parentheses for class declaration e.g. class A () <-> class A()
        if c.padding.implements is not None:
            c = c.padding.with_implements(
                space_before_container(c.padding.implements, self._style.before_parentheses.method_call)
            )

            param_size = len(c.padding.implements.elements)
            use_space = self._style.within.method_call_parentheses

            # TODO: Refactor to remove duplicate code.
            def _process_argument(index, arg, args_size):
                if index == 0:
                    arg = arg.with_element(space_before(arg.element, use_space))
                else:
                    arg = arg.with_element(space_before(arg.element, self._style.other.after_comma))

                if index == args_size - 1:
                    arg = space_after(arg, use_space)
                else:
                    arg = space_after(arg, self._style.other.before_comma)

                return arg

            c = c.padding.with_implements(
                c.padding.implements.padding.with_elements(
                    list_map(lambda arg, index: _process_argument(index, arg, param_size),
                             c.padding.implements.padding.elements)))
        return c

    def visit_method_declaration(self, method_declaration: MethodDeclaration, p: P) -> J:
        m: MethodDeclaration = cast(MethodDeclaration, super().visit_method_declaration(method_declaration, p))

        m = m.padding.with_parameters(
            space_before_container(m.padding.parameters, self._style.before_parentheses.method_declaration)
        )

        param_size = len(m.parameters)
        use_space = self._style.within.method_call_parentheses

        def _process_argument(index, arg, args_size):
            # TODO: Fix Type hint handling
            # Handle space before type hint colon e.g. foo(a: int) <-> foo(a:int)
            if isinstance(arg.element, VariableDeclarations) and arg.element.type_expression:
                vd = cast(VariableDeclarations, arg.element)
                arg = arg.with_element(vd.with_type_expression(
                    space_before(vd.type_expression, self._style.other.after_colon))
                                       .padding.with_variables(
                    list_map(lambda v: space_after_right_padded(v, self._style.other.before_colon),
                             vd.padding.variables))
                                       )

            if index == 0:
                arg = arg.with_element(space_before(arg.element, use_space))
            else:
                arg = arg.with_element(space_before(arg.element, self._style.other.after_comma))

            if index == args_size - 1:
                arg = space_after(arg, use_space)
            else:
                arg = space_after(arg, self._style.other.before_comma)
            return arg

        m = m.padding.with_parameters(
            m.padding.parameters.padding.with_elements(
                list_map(lambda arg, idx: _process_argument(idx, arg, param_size),
                         m.padding.parameters.padding.elements)
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

    def visit_block(self, block: Block, p: P) -> J:
        b = cast(Block, super().visit_block(block, p))
        b = space_before(b, self._style.other.before_colon)
        return b

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
                    list_map(lambda arg: arg.with_element(space_before(arg.element, use_space)),
                             m.padding.arguments.padding.elements)
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
                    arg = arg.with_element(space_before(arg.element, use_space))
                else:
                    arg = arg.with_element(space_before(arg.element, self._style.other.after_comma))

                if index == args_size - 1:
                    arg = space_after(arg, use_space)
                else:
                    arg = space_after(arg, self._style.other.before_comma)

                return arg

            m = m.padding.with_arguments(
                m.padding.arguments.padding.with_elements(
                    list_map(lambda arg, idx: _process_argument(idx, arg, args_size, use_space),
                             m.padding.arguments.padding.elements)))

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
            space_before_left_padded(a.padding.assignment, self._style.around_operators.assignment))
        a = a.padding.with_assignment(
            a.padding.assignment.with_element(
                space_before(a.padding.assignment.element, self._style.around_operators.assignment)))
        return a

    def visit_assignment_operation(self, assignment_operation: AssignmentOperation, p: P) -> J:
        """
        Handle assignment operation e.g. a += 1 <-> a+=1
        """
        a: AssignmentOperation = cast(AssignmentOperation, super().visit_assignment_operation(assignment_operation, p))
        operator: JLeftPadded = a.padding.operator
        a = a.padding.with_operator(
            operator.with_before(update_space(operator.before, self._style.around_operators.assignment)))
        return a.with_assignment(space_before(a.assignment, self._style.around_operators.assignment))

    def visit_chained_assignment(self, chained_assignment: ChainedAssignment, p: P) -> J:
        """
        Handle chained assignment e.g. a = b = 1 <-> a=b=1
        """
        a: ChainedAssignment = cast(ChainedAssignment, super().visit_chained_assignment(chained_assignment, p))
        a = a.padding.with_variables(
            [v.with_after(update_space(v.after, self._style.around_operators.assignment)) for v in a.padding.variables])

        a = a.padding.with_variables(
            [v.with_element(
                space_before(v.element, self._style.around_operators.assignment if idx >= 1 else False)) for idx, v
                in enumerate(a.padding.variables)])

        return a.with_assignment(space_before(a.assignment, self._style.around_operators.assignment))

    def visit_member_reference(self, member_reference: MemberReference, p: P) -> J:
        m: MemberReference = cast(MemberReference, super().visit_member_reference(member_reference, p))

        if m.padding.type_parameters is not None:
            # TODO: Handle type parameters, relevant for constructors in Python.
            raise NotImplementedError("Type parameters are not supported yet")

        return m

    def _apply_binary_space_around(self, binary, use_space_around: bool):
        operator = binary.padding.operator
        binary = binary.padding.with_operator(
            operator.with_before(update_space(operator.before, use_space_around))
        )
        return binary.with_right(space_before(binary.right, use_space_around))

    def visit_binary(self, binary: j.Binary, p: P) -> J:
        b: j.Binary = cast(j.Binary, super().visit_binary(binary, p))
        op: j.Binary.Type = b.operator

        # Handle space around all binary operators e.g. 1 +   1 <-> 1 + 1 or 1+1 depending on style
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

    def visit_if(self, if_stm: If, p: P) -> J:
        if_: j.If = cast(If, super().visit_if(if_stm, p))

        # Handle space before if condition e.g. if    True: <-> if True:
        if_ = if_.with_if_condition(space_before(if_._if_condition, True))

        # Handle space before if colon e.g. if True:    pass <-> if True: pass
        if_ = if_.with_if_condition(
            if_.if_condition.padding.with_tree(
                space_after(if_.if_condition.padding.tree, self._style.other.before_colon))
        )
        return if_

    def visit_else(self, else_: If.Else, p: P) -> J:
        e: j.If.Else = cast(j.If.Else, super().visit_else(else_, p))
        e = e.padding.with_body(space_before_right_padded_element(e.padding.body, self._style.other.before_colon))

        return e

    def visit_slice(self, slice: Slice, p: P) -> J:
        s: Slice = cast(Slice, super().visit_slice(slice, p))
        use_space = self._style.within.brackets

        if s.padding.start is not None:
            s = s.padding.with_start(space_before_right_padded_element(s.padding.start, use_space))
            s = s.padding.with_start(space_after_right_padded(s.padding.start, use_space))
        if s.padding.stop is not None:
            # TODO: Check if "before" is correct, in PyCharm it is not supported but we could still support it.
            s = s.padding.with_stop(space_before_right_padded_element(s.padding.stop, use_space))
            s = s.padding.with_stop(space_after_right_padded(s.padding.stop, use_space))

            if s.padding.step is not None:
                # TODO: Check if "before" is correct, in PyCharm it is not supported but we could still support it.
                s = s.padding.with_step(space_before_right_padded_element(s.padding.step, use_space))
                s = s.padding.with_step(space_after_right_padded(s.padding.step, use_space))
        return s

    def visit_python_for_loop(self, for_loop: ForLoop, p: P) -> J:
        fl = cast(ForLoop, super().visit_python_for_loop(for_loop, p))

        # Set single space before loop target e.g. for    i in...: <-> for i in ...:
        fl = fl.with_target(space_before(fl.target, True))

        # Set single space before loop iterable, and in keyword e.g. for i in    []: <-> for i in []:
        fl = fl.padding.with_iterable(space_before_left_padded(fl.padding.iterable, True))
        fl = fl.padding.with_iterable(space_before_right_padded_element(fl.padding.iterable, True))
        return fl

    def visit_collection_literal(self, collection_literal: CollectionLiteral, p: P) -> J:
        cl = cast(CollectionLiteral, super().visit_collection_literal(collection_literal, p))

        # TODO: Refactor to remove duplicate code.
        def _process_element(index, arg, args_size, use_space):
            if index == 0:
                arg = arg.with_element(space_before(arg.element, use_space))
            else:
                arg = arg.with_element(space_before(arg.element, self._style.other.after_comma))

            if index == args_size - 1:
                arg = space_after(arg, use_space)
            else:
                arg = space_after(arg, self._style.other.before_comma)

            return arg

        cl = cl.padding.with_elements(
            cl.padding.elements.padding.with_elements(
                list_map(
                    lambda arg, idx: _process_element(idx, arg,
                                                      args_size=len(cl.padding.elements.padding.elements),
                                                      use_space=self._style.within.brackets),
                    cl.padding.elements.padding.elements)))

        return cl

    def visit_dict_literal(self, dict_literal: DictLiteral, p: P) -> J:
        dl = cast(DictLiteral, super().visit_dict_literal(dict_literal, p))

        def _process_kv_pair(c: JRightPadded[KeyValue], idx: int, arg_size) -> JRightPadded[KeyValue]:
            # Handle both space before and after each comma in key-value pair  and space before/after braces in
            # first argument e.g. {1: 2  ,   3: 4} <-> {1: 2, 3: 4}
            if idx == 0 or idx == arg_size - 1:
                before_comma_style = self._style.other.before_comma if idx == 0 else self._style.within.braces
                after_comma_style = self._style.within.braces if idx == 0 else self._style.other.after_comma
                c = space_after_right_padded(c, before_comma_style)
                c = space_before_right_padded_element(c, after_comma_style)
            else:
                c = space_after_right_padded(c, self._style.other.before_comma)
                c = space_before_right_padded_element(c, self._style.other.after_comma)

            # Handle space before and after colon in key-value pair e.g. {1 :   2} <-> {1: 2}
            kv = cast(KeyValue, c.element)
            kv = kv.with_value(space_before(kv.value, self._style.other.after_colon))
            kv = kv.padding.with_key(space_after_right_padded(kv.padding.key, self._style.other.before_colon))
            return c.with_element(kv)

        dl = dl.padding.with_elements(
            dl.padding.elements.padding.with_elements(
                list_map(lambda x, idx: _process_kv_pair(x, idx, len(dl.padding.elements.padding.elements)),
                         dl.padding.elements.padding.elements)
            )
        )
        return dl

    def visit_multi_import(self, multi_import: MultiImport, p: P) -> J:
        mi: MultiImport = cast(MultiImport, super().visit_multi_import(multi_import, p))

        _space_on_first_import = lambda idx: mi.padding.from_ is None if idx == 0 else self._style.other.after_comma

        mi = mi.padding.with_names(
            mi.padding.names.with_elements(
                list_map(lambda x, idx: space_before(x, _space_on_first_import(idx)),
                         mi.padding.names.elements)
            )
        )
        _names = mi.padding.names
        _names = _names.padding.with_elements(
            list_map(lambda x: space_after(x, self._style.other.before_comma), _names.padding.elements)
        )
        return mi.padding.with_names(_names)

    def visit_import(self, import_: Import, p: P) -> J:
        imp: Import = cast(Import, super().visit_import(import_, p))
        # Always use single space before and after alias 'as' keyword e.g. import foo  as  bar <-> import foo as bar
        if imp.padding.alias:
            imp = imp.with_alias(space_before(imp.alias, True))
            imp = imp.padding.with_alias(space_before_left_padded(imp.padding.alias, True))
        return imp

    def visit_type_hint(self, type_hint: TypeHint, p: P) -> J:
        th: TypeHint = cast(TypeHint, super().visit_type_hint(type_hint, p))
        th = space_before(th, self._style.other.before_colon)
        return th.with_type_tree(space_before(th.type_tree, self._style.other.after_colon))


J2 = TypeVar('J2', bound=j.J)


def space_before(j: J2, add_space: bool) -> J2:
    space: Space = cast(Space, j.prefix)
    if space.comments or '\\' in space.whitespace:
        # don't touch whitespaces with comments or continuation characters
        return j

    return j.with_prefix(Space.SINGLE_SPACE if add_space else Space.EMPTY)


def space_before_container(container: j.JContainer, add_space: bool) -> j.JContainer:
    if container.before.comments:
        # Perform the space rule for the suffix of the last comment only. Same as IntelliJ.
        comments: List[j.Comment] = space_last_comment_suffix(container.before.comments, add_space)
        return container.with_before(container.before.with_comments(comments))

    if add_space and not_single_space(container.before.whitespace):
        return container.with_before(container.before.with_whitespace(" "))
    elif not add_space and only_spaces_and_not_empty(container.before.whitespace):
        return container.with_before(container.before.with_whitespace(""))
    else:
        return container


def space_before_right_padded_element(container: j.JRightPadded, add_space: bool) -> j.JRightPadded:
    return container.with_element(space_before(container.element, add_space))


def space_last_comment_suffix(comments: List[j.Comment], add_space: bool) -> List[j.Comment]:
    return [space_suffix(comment, add_space) if i == len(comments) - 1 else comment for i, comment
            in
            enumerate(comments)]


def space_suffix(comment: j.Comment, add_space: bool) -> j.Comment:
    if add_space and not_single_space(comment.suffix):
        return comment.with_suffix(" ")
    elif not add_space and only_spaces_and_not_empty(comment.suffix):
        return comment.with_suffix("")
    else:
        return comment


def space_before_left_padded(j: JLeftPadded[J2], add_space) -> JLeftPadded[J2]:
    space: Space = cast(Space, j.before)
    if space.comments or '\\' in space.whitespace:
        # don't touch whitespaces with comments or continuation characters
        return j

    if add_space and not_single_space(space.whitespace):
        return j.with_before(space.with_whitespace(" "))
    elif not add_space and only_spaces_and_not_empty(space.whitespace):
        return j.with_before(space.with_whitespace(""))
    return j


def space_after(j: J2, add_space: bool) -> J2:
    space: Space = cast(Space, j.after)
    if space.comments or '\\' in space.whitespace:
        # don't touch whitespaces with comments or continuation characters
        return j

    if add_space and not_single_space(space.whitespace):
        return j.with_after(space.with_whitespace(" "))
    elif not add_space and only_spaces_and_not_empty(space.whitespace):
        return j.with_after(space.with_whitespace(""))
    return j


def space_after_right_padded(right: JRightPadded[J2], add_space: bool) -> JRightPadded[J2]:
    space: Space = right.after
    if space.comments or '\\' in space.whitespace:
        # don't touch whitespaces with comments or continuation characters
        return right

    if add_space and not_single_space(space.whitespace):
        return right.with_after(space.with_whitespace(" "))
    elif not add_space and only_spaces_and_not_empty(space.whitespace):
        return right.with_after(space.with_whitespace(""))
    return right


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
