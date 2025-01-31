from typing import Optional, cast, List, TypeVar

import rewrite.java as j
from rewrite import Tree, list_map
from rewrite.java import J, Assignment, JLeftPadded, AssignmentOperation, MemberReference, MethodInvocation, \
    MethodDeclaration, Empty, ArrayAccess, Space, If, Block, ClassDeclaration, VariableDeclarations, JRightPadded, \
    Import, ParameterizedType, Parentheses, Try, ControlParentheses, J2
from rewrite.python import PythonVisitor, SpacesStyle, Binary, ChainedAssignment, Slice, CollectionLiteral, \
    ForLoop, DictLiteral, KeyValue, TypeHint, MultiImport, ExpressionTypeTree, ComprehensionExpression, NamedArgument
from rewrite.visitor import P, Cursor


class SpacesVisitor(PythonVisitor):
    def __init__(self, style: SpacesStyle, stop_after: Optional[Tree] = None):
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

            if c.implements:
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

        if m.return_type_expression is not None:
            m = m.with_return_type_expression(space_before(m.return_type_expression, True))

        # TODO: Type parameters are not supported yet
        if m.padding.type_parameters is not None:
            raise NotImplementedError("Type parameters are not supported yet")

        return m.padding.with_parameters(
            m.padding.parameters.with_before(
                Space.SINGLE_SPACE if self._before_parentheses.method_declaration else Space.EMPTY
            )
        )

    def visit_catch(self, catch: Try.Catch, p: P) -> J:
        c = cast(Try.Catch, super().visit_catch(catch, p))
        # c = c.with_parameter(c.parameter.with_tree(space_before(c.parameter.tree, True)))
        return c

    def visit_control_parentheses(self, control_parentheses: ControlParentheses[J2], p: P) -> J:
        cp = cast(ControlParentheses[J2], super().visit_control_parentheses(control_parentheses, p))
        cp = space_before(cp, False)
        cp = cp.with_tree(space_before(cp.tree, True))
        return cp

    def visit_named_argument(self, named_argument: NamedArgument, p: P) -> J:
        a = cast(NamedArgument, super().visit_named_argument(named_argument, p))
        if a.padding.value is not None:
            a = a.padding.with_value(
                space_before_left_padded(a.padding.value, self._style.around_operators.eq_in_keyword_argument))
            return a.padding.with_value(
                space_before_left_padded_element(a.padding.value, self._style.around_operators.eq_in_keyword_argument))
        return a

    @staticmethod
    def _part_of_method_header(cursor: Cursor) -> bool:
        if (c := cursor.parent_tree_cursor()) and isinstance(c.value, VariableDeclarations):
            return c.parent_tree_cursor() is not None and isinstance(c.parent_tree_cursor().value, MethodDeclaration)
        return False

    def visit_variable(self, named_variable: VariableDeclarations.NamedVariable, p: P) -> J:
        v = cast(VariableDeclarations.NamedVariable, super().visit_variable(named_variable, p))

        # Check if the variable is a named parameter in a method declaration
        if not self._part_of_method_header(self.cursor):
            return v

        if v.padding.initializer is not None and v.padding.initializer.element is not None:
            use_space = self._style.around_operators.eq_in_named_parameter or v.variable_type is not None
            # Argument with a typehint will always receive a space e.g. foo(a: int =1) <-> foo(a: int = 1)
            use_space |= self.cursor.first_enclosing_or_throw(VariableDeclarations).type_expression is not None

            v = v.padding.with_initializer(
                space_before_left_padded(v.padding.initializer, use_space))
            v = v.padding.with_initializer(
                space_before_left_padded_element(v.padding.initializer, use_space))
        return v

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

        # ignore assignments of the form `<value> as x` in `with` statements
        if isinstance(self.cursor.parent_tree_cursor().value, j.Try.Resource):
            return a

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
            list_map(lambda v: v.with_after(update_space(v.after, self._style.around_operators.assignment)), a.padding.variables))

        a = a.padding.with_variables(
            list_map(lambda v, idx: v.with_element(
                space_before(v.element, self._style.around_operators.assignment if idx >= 1 else False)), a.padding.variables))

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
        elif op in [j.Binary.Type.Equal, j.Binary.Type.NotEqual]:
            b = self._apply_binary_space_around(b, self._style.around_operators.equality)
        elif op in [j.Binary.Type.LessThan, j.Binary.Type.GreaterThan, j.Binary.Type.LessThanOrEqual,
                    j.Binary.Type.GreaterThanOrEqual]:
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
        elif op in [Binary.Type.FloorDivision, Binary.Type.MatrixMultiplication]:
            b = self._apply_binary_space_around(b, self._style.around_operators.multiplicative)
        elif op == Binary.Type.StringConcatenation:
            b = self._apply_binary_space_around(b, self._style.around_operators.additive)
        elif op == Binary.Type.Power:
            b = self._apply_binary_space_around(b, self._style.around_operators.power)

        return b

    def visit_if(self, if_stm: If, p: P) -> J:
        if_: j.If = cast(If, super().visit_if(if_stm, p))

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

    def visit_parameterized_type(self, parameterized_type: ParameterizedType, p: P) -> J:
        pt = cast(ParameterizedType, super().visit_parameterized_type(parameterized_type, p))

        def _process_element(index, arg, last, use_space):
            if index == 0:
                arg = arg.with_element(space_before(arg.element, use_space))
            else:
                arg = arg.with_element(space_before(arg.element, self._style.other.after_comma))

            if last:
                arg = space_after(arg, use_space and arg.markers.find_first(j.TrailingComma) is None)
                arg = arg.with_markers(arg.markers.compute_by_type(j.TrailingComma, self._remap_trailing_comma_space))
            else:
                arg = space_after(arg, self._style.other.before_comma)

            return arg

        pt = pt.padding.with_type_parameters(
            pt.padding.type_parameters.padding.with_elements(
                list_map(
                    lambda arg, idx: _process_element(idx, arg,
                                                      last=idx == len(pt.padding.type_parameters.padding.elements) - 1,
                                                      use_space=self._style.within.brackets),
                    pt.padding.type_parameters.padding.elements
                )
            )
        )

        return pt

    def visit_parentheses(self, parentheses: Parentheses, p: P) -> J:
        p2 = cast(Parentheses, super().visit_parentheses(parentheses, p))
        p2 = p2.with_prefix(update_space(p2.prefix, False))
        p2 = p2.padding.with_tree(p2.padding.tree.with_after(update_space(p2.padding.tree.after, False)))
        return p2

    def visit_collection_literal(self, collection_literal: CollectionLiteral, p: P) -> J:
        cl = cast(CollectionLiteral, super().visit_collection_literal(collection_literal, p))

        # TODO: Refactor to remove duplicate code.
        def _process_element(index, arg, args_size, use_space):
            if index == 0:
                arg = arg.with_element(space_before(arg.element, use_space))
            else:
                arg = arg.with_element(space_before(arg.element, self._style.other.after_comma))

            if index == args_size - 1:
                arg = space_after(arg, use_space and arg.markers.find_first(j.TrailingComma) is None)
                arg = arg.with_markers(arg.markers.compute_by_type(j.TrailingComma, self._remap_trailing_comma_space))
            else:
                arg = space_after(arg, self._style.other.before_comma)

            return arg

        if cl.kind == CollectionLiteral.Kind.SET:
            _space_style = self._style.within.braces
        elif cl.kind == CollectionLiteral.Kind.LIST:
            _space_style = self._style.within.brackets
        elif cl.kind == CollectionLiteral.Kind.TUPLE:
            _space_style = self._style.within.brackets if self.cursor.first_enclosing(ExpressionTypeTree) else False

        cl = cl.padding.with_elements(
            cl.padding.elements.padding.with_elements(
                list_map(
                    lambda arg, idx: _process_element(idx, arg,
                                                      args_size=len(cl.padding.elements.padding.elements),
                                                      use_space=_space_style),
                    cl.padding.elements.padding.elements)))

        return cl

    def visit_dict_literal(self, dict_literal: DictLiteral, p: P) -> J:
        dl = cast(DictLiteral, super().visit_dict_literal(dict_literal, p))

        def _process_kv_pair(c: JRightPadded[KeyValue], idx: int, arg_size) -> JRightPadded[KeyValue]:
            # Handle both space before and after each comma in key-value pair and space before/after braces in
            # first argument e.g. {1: 2  ,   3: 4} <-> {1: 2, 3: 4}
            if idx == 0 or idx == arg_size - 1:
                if idx == 0:
                    before_comma_style = self._style.other.before_comma
                else:
                    before_comma_style = self._style.within.braces and c.markers.find_first(j.TrailingComma) is None
                after_comma_style = self._style.within.braces if idx == 0 else self._style.other.after_comma
                c = space_after_right_padded(c, before_comma_style)
                c = space_before_right_padded_element(c, after_comma_style)
            else:
                c = space_after_right_padded(c, self._style.other.before_comma)
                c = space_before_right_padded_element(c, self._style.other.after_comma)

            # Handle trailing comma space for last argument e.g. {1: 2, 3: 4, } <-> {1: 2, 3: 4,}
            if idx == arg_size - 1:
                c = c.with_markers(c.markers.compute_by_type(j.TrailingComma, self._remap_trailing_comma_space))

            return c

        dl = dl.padding.with_elements(
            dl.padding.elements.padding.with_elements(
                list_map(lambda x, idx: _process_kv_pair(x, idx, len(dl.padding.elements.padding.elements)),
                         dl.padding.elements.padding.elements)
            )
        )
        return dl

    def visit_multi_import(self, multi_import: MultiImport, p: P) -> J:
        mi: MultiImport = cast(MultiImport, super().visit_multi_import(multi_import, p))

        # Space after from
        if mi.padding.from_ is not None:
            mi = mi.padding.with_from(
                space_before_right_padded_element(mi.padding.from_, True)
            )

        # Single space after import keyword
        mi = mi.padding.with_names(
            space_before_container(mi.padding.names, True)
        )

        _names = mi.padding.names

        # Will handle space after import name before comma e.g. import foo   , bar <-> import foo, bar
        _names = _names.padding.with_elements(
            list_map(lambda x, idx: space_after_right_padded(x, self._style.other.before_comma),
                     _names.padding.elements)
        )
        _names = _names.padding.with_elements(
            list_map(lambda x, idx: space_before_right_padded_element(x, self._style.other.after_comma and idx != 0),
                     _names.padding.elements)
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
        th = th.with_type_tree(space_before(th.type_tree, self._style.other.after_colon))
        return th

    def visit_expression_type_tree(self, expression_type_tree: ExpressionTypeTree, p: P) -> J:
        ett = cast(ExpressionTypeTree, super().visit_expression_type_tree(expression_type_tree, p))
        # Can always be set to false as the collection literal will handle the space before the brackets
        ett = space_before(ett, False)
        return ett

    def visit_comprehension_expression(self, comprehension_expression: ComprehensionExpression, p: P) -> J:
        ce = cast(ComprehensionExpression, super().visit_comprehension_expression(comprehension_expression, p))

        # Handle space before result this will depend on the style setting for the comprehension type.
        if ce.kind == ComprehensionExpression.Kind.LIST:
            ce = ce.with_result(space_before(ce.result, self._style.within.brackets))
            ce = ce.with_suffix(update_space(ce.suffix, self._style.within.brackets))
        elif ce.kind == ComprehensionExpression.Kind.GENERATOR:
            ce = ce.with_result(space_before(ce.result, False))
            ce = ce.with_suffix(update_space(ce.suffix, False))
        elif ce.kind in (ComprehensionExpression.Kind.SET, ComprehensionExpression.Kind.DICT):
            ce = ce.with_result(space_before(ce.result, self._style.within.braces))
            ce = ce.with_suffix(update_space(ce.suffix, self._style.within.braces))

        return ce

    def visit_key_value(self, key_value: KeyValue, p: P) -> J:
        # Handle space before and after colon in key-value pair e.g. {1 :   2} <-> {1: 2}
        kv = cast(KeyValue, super().visit_key_value(key_value, p))
        kv = kv.with_value(space_before(kv.value, self._style.other.after_colon))
        return kv.padding.with_key(space_after_right_padded(kv.padding.key, self._style.other.before_colon))

    def visit_comprehension_condition(self, condition: ComprehensionExpression.Condition, p: P) -> J:
        cond = cast(ComprehensionExpression.Condition, super().visit_comprehension_condition(condition, p))
        # Set single space before and after comprehension 'if' keyword.
        cond = space_before(cond, True)
        cond = cond.with_expression(space_before(cond.expression, True))
        return cond

    def visit_comprehension_clause(self, clause: ComprehensionExpression.Clause, p: P) -> J:
        cc = cast(ComprehensionExpression.Clause, super().visit_comprehension_clause(clause, p))

        # Ensure single space before 'for' keyword
        cc = space_before(cc, True)

        # Single before 'in' keyword e.g. ..i   in...  <-> ...i in...
        cc = cc.padding.with_iterated_list(space_before_left_padded(cc.padding.iterated_list, True))
        # Single space before 'iterator' variable (or after for keyword) e.g. ...for   i <-> ...for i
        cc = cc.with_iterator_variable(space_before(cc.iterator_variable, True))
        # Ensure single space after 'in' keyword e.g. ...in   range(10) <-> ...in range(10)
        cc = cc.padding.with_iterated_list(space_before_left_padded_element(cc.padding.iterated_list, True))
        return cc

    def _remap_trailing_comma_space(self, tc: j.TrailingComma) -> j.TrailingComma:
        return tc.with_suffix(update_space(tc.suffix, self._style.other.after_comma))


J2 = TypeVar('J2', bound=j.J)


def space_before(j: J2, add_space: bool) -> J2:
    prefix: Space = cast(Space, j.prefix)

    if prefix.comments or ('\n' in prefix.whitespace):
        return j

    if add_space and not_single_space(prefix.whitespace):
        return j.with_prefix(prefix.with_whitespace(" "))  # pyright: ignore [reportReturnType]
    elif not add_space and only_spaces_and_not_empty(prefix.whitespace):
        return j.with_prefix(prefix.with_whitespace(""))  # pyright: ignore [reportReturnType]

    return j


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


def space_before_left_padded_element(left: j.JLeftPadded, add_space: bool) -> j.JLeftPadded:
    return left.with_element(space_before(left.element, add_space))

def space_before_right_padded_element(right: j.JRightPadded, add_space: bool) -> j.JRightPadded:
    return right.with_element(space_before(right.element, add_space))


def space_last_comment_suffix(comments: List[j.Comment], add_space: bool) -> List[j.Comment]:
    return list_map(lambda c, i: space_suffix(c, add_space) if i == len(comments) - 1 else c, comments)


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
