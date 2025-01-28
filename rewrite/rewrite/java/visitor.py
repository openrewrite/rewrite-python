from typing import cast, TypeVar, Union

from rewrite import SourceFile, TreeVisitor, list_map
from . import extensions
from .support_types import *
from .tree import *

# noinspection DuplicatedCode
class JavaVisitor(TreeVisitor[J, P]):
    def is_acceptable(self, source_file: SourceFile, p: P) -> bool:
        return isinstance(source_file, J)

    def visit_expression(self, expression: Expression, p: P) -> J:
        return expression

    def visit_statement(self, statement: Statement, p: P) -> J:
        return statement

    def visit_annotated_type(self, annotated_type: AnnotatedType, p: P) -> J:
        annotated_type = annotated_type.with_prefix(self.visit_space(annotated_type.prefix, Space.Location.ANNOTATED_TYPE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(annotated_type, p))
        if not isinstance(temp_expression, AnnotatedType):
            return temp_expression
        annotated_type = cast(AnnotatedType, temp_expression)
        annotated_type = annotated_type.with_markers(self.visit_markers(annotated_type.markers, p))
        annotated_type = annotated_type.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), annotated_type.annotations))
        annotated_type = annotated_type.with_type_expression(self.visit_and_cast(annotated_type.type_expression, TypeTree, p))
        return annotated_type

    def visit_annotation(self, annotation: Annotation, p: P) -> J:
        annotation = annotation.with_prefix(self.visit_space(annotation.prefix, Space.Location.ANNOTATION_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(annotation, p))
        if not isinstance(temp_expression, Annotation):
            return temp_expression
        annotation = cast(Annotation, temp_expression)
        annotation = annotation.with_markers(self.visit_markers(annotation.markers, p))
        annotation = annotation.with_annotation_type(self.visit_and_cast(annotation.annotation_type, NameTree, p))
        annotation = annotation.padding.with_arguments(self.visit_container(annotation.padding.arguments, JContainer.Location.ANNOTATION_ARGUMENTS, p))
        return annotation

    def visit_array_access(self, array_access: ArrayAccess, p: P) -> J:
        array_access = array_access.with_prefix(self.visit_space(array_access.prefix, Space.Location.ARRAY_ACCESS_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(array_access, p))
        if not isinstance(temp_expression, ArrayAccess):
            return temp_expression
        array_access = cast(ArrayAccess, temp_expression)
        array_access = array_access.with_markers(self.visit_markers(array_access.markers, p))
        array_access = array_access.with_indexed(self.visit_and_cast(array_access.indexed, Expression, p))
        array_access = array_access.with_dimension(self.visit_and_cast(array_access.dimension, ArrayDimension, p))
        return array_access

    def visit_array_type(self, array_type: ArrayType, p: P) -> J:
        array_type = array_type.with_prefix(self.visit_space(array_type.prefix, Space.Location.ARRAY_TYPE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(array_type, p))
        if not isinstance(temp_expression, ArrayType):
            return temp_expression
        array_type = cast(ArrayType, temp_expression)
        array_type = array_type.with_markers(self.visit_markers(array_type.markers, p))
        array_type = array_type.with_element_type(self.visit_and_cast(array_type.element_type, TypeTree, p))
        array_type = array_type.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), array_type.annotations))
        array_type = array_type.with_dimension(self.visit_left_padded(array_type.dimension, JLeftPadded.Location.ARRAY_TYPE_DIMENSION, p))
        return array_type

    def visit_assert(self, assert_: Assert, p: P) -> J:
        assert_ = assert_.with_prefix(self.visit_space(assert_.prefix, Space.Location.ASSERT_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(assert_, p))
        if not isinstance(temp_statement, Assert):
            return temp_statement
        assert_ = cast(Assert, temp_statement)
        assert_ = assert_.with_markers(self.visit_markers(assert_.markers, p))
        assert_ = assert_.with_condition(self.visit_and_cast(assert_.condition, Expression, p))
        assert_ = assert_.with_detail(self.visit_left_padded(assert_.detail, JLeftPadded.Location.ASSERT_DETAIL, p))
        return assert_

    def visit_assignment(self, assignment: Assignment, p: P) -> J:
        assignment = assignment.with_prefix(self.visit_space(assignment.prefix, Space.Location.ASSIGNMENT_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(assignment, p))
        if not isinstance(temp_statement, Assignment):
            return temp_statement
        assignment = cast(Assignment, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(assignment, p))
        if not isinstance(temp_expression, Assignment):
            return temp_expression
        assignment = cast(Assignment, temp_expression)
        assignment = assignment.with_markers(self.visit_markers(assignment.markers, p))
        assignment = assignment.with_variable(self.visit_and_cast(assignment.variable, Expression, p))
        assignment = assignment.padding.with_assignment(self.visit_left_padded(assignment.padding.assignment, JLeftPadded.Location.ASSIGNMENT, p))
        return assignment

    def visit_assignment_operation(self, assignment_operation: AssignmentOperation, p: P) -> J:
        assignment_operation = assignment_operation.with_prefix(self.visit_space(assignment_operation.prefix, Space.Location.ASSIGNMENT_OPERATION_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(assignment_operation, p))
        if not isinstance(temp_statement, AssignmentOperation):
            return temp_statement
        assignment_operation = cast(AssignmentOperation, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(assignment_operation, p))
        if not isinstance(temp_expression, AssignmentOperation):
            return temp_expression
        assignment_operation = cast(AssignmentOperation, temp_expression)
        assignment_operation = assignment_operation.with_markers(self.visit_markers(assignment_operation.markers, p))
        assignment_operation = assignment_operation.with_variable(self.visit_and_cast(assignment_operation.variable, Expression, p))
        assignment_operation = assignment_operation.padding.with_operator(self.visit_left_padded(assignment_operation.padding.operator, JLeftPadded.Location.ASSIGNMENT_OPERATION_OPERATOR, p))
        assignment_operation = assignment_operation.with_assignment(self.visit_and_cast(assignment_operation.assignment, Expression, p))
        return assignment_operation

    def visit_binary(self, binary: Binary, p: P) -> J:
        binary = binary.with_prefix(self.visit_space(binary.prefix, Space.Location.BINARY_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(binary, p))
        if not isinstance(temp_expression, Binary):
            return temp_expression
        binary = cast(Binary, temp_expression)
        binary = binary.with_markers(self.visit_markers(binary.markers, p))
        binary = binary.with_left(self.visit_and_cast(binary.left, Expression, p))
        binary = binary.padding.with_operator(self.visit_left_padded(binary.padding.operator, JLeftPadded.Location.BINARY_OPERATOR, p))
        binary = binary.with_right(self.visit_and_cast(binary.right, Expression, p))
        return binary

    def visit_block(self, block: Block, p: P) -> J:
        block = block.with_prefix(self.visit_space(block.prefix, Space.Location.BLOCK_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(block, p))
        if not isinstance(temp_statement, Block):
            return temp_statement
        block = cast(Block, temp_statement)
        block = block.with_markers(self.visit_markers(block.markers, p))
        block = block.padding.with_static(self.visit_right_padded(block.padding.static, JRightPadded.Location.STATIC_INIT, p))
        block = block.padding.with_statements(list_map(lambda v: self.visit_right_padded(v, JRightPadded.Location.BLOCK_STATEMENT, p), block.padding.statements))
        block = block.with_end(self.visit_space(block.end, Space.Location.BLOCK_END, p))
        return block

    def visit_break(self, break_: Break, p: P) -> J:
        break_ = break_.with_prefix(self.visit_space(break_.prefix, Space.Location.BREAK_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(break_, p))
        if not isinstance(temp_statement, Break):
            return temp_statement
        break_ = cast(Break, temp_statement)
        break_ = break_.with_markers(self.visit_markers(break_.markers, p))
        break_ = break_.with_label(self.visit_and_cast(break_.label, Identifier, p))
        return break_

    def visit_case(self, case: Case, p: P) -> J:
        case = case.with_prefix(self.visit_space(case.prefix, Space.Location.CASE_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(case, p))
        if not isinstance(temp_statement, Case):
            return temp_statement
        case = cast(Case, temp_statement)
        case = case.with_markers(self.visit_markers(case.markers, p))
        case = case.padding.with_case_labels(self.visit_container(case.padding.case_labels, JContainer.Location.CASE_CASE_LABELS, p))
        case = case.padding.with_statements(self.visit_container(case.padding.statements, JContainer.Location.CASE, p))
        case = case.padding.with_body(self.visit_right_padded(case.padding.body, JRightPadded.Location.CASE_BODY, p))
        case = case.with_guard(self.visit_and_cast(case.guard, Expression, p))
        return case

    def visit_class_declaration(self, class_declaration: ClassDeclaration, p: P) -> J:
        class_declaration = class_declaration.with_prefix(self.visit_space(class_declaration.prefix, Space.Location.CLASS_DECLARATION_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(class_declaration, p))
        if not isinstance(temp_statement, ClassDeclaration):
            return temp_statement
        class_declaration = cast(ClassDeclaration, temp_statement)
        class_declaration = class_declaration.with_markers(self.visit_markers(class_declaration.markers, p))
        class_declaration = class_declaration.with_leading_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), class_declaration.leading_annotations))
        class_declaration = class_declaration.with_modifiers(list_map(lambda v: self.visit_and_cast(v, Modifier, p), class_declaration.modifiers))
        class_declaration = class_declaration.padding.with_kind(self.visit_and_cast(class_declaration.padding.kind, ClassDeclaration.Kind, p))
        class_declaration = class_declaration.with_name(self.visit_and_cast(class_declaration.name, Identifier, p))
        class_declaration = class_declaration.padding.with_type_parameters(self.visit_container(class_declaration.padding.type_parameters, JContainer.Location.TYPE_PARAMETERS, p))
        class_declaration = class_declaration.padding.with_primary_constructor(self.visit_container(class_declaration.padding.primary_constructor, JContainer.Location.RECORD_STATE_VECTOR, p))
        class_declaration = class_declaration.padding.with_extends(self.visit_left_padded(class_declaration.padding.extends, JLeftPadded.Location.EXTENDS, p))
        class_declaration = class_declaration.padding.with_implements(self.visit_container(class_declaration.padding.implements, JContainer.Location.IMPLEMENTS, p))
        class_declaration = class_declaration.padding.with_permits(self.visit_container(class_declaration.padding.permits, JContainer.Location.PERMITS, p))
        class_declaration = class_declaration.with_body(self.visit_and_cast(class_declaration.body, Block, p))
        return class_declaration

    def visit_class_declaration_kind(self, kind: ClassDeclaration.Kind, p: P) -> J:
        kind = kind.with_prefix(self.visit_space(kind.prefix, Space.Location.CLASS_KIND, p))
        kind = kind.with_markers(self.visit_markers(kind.markers, p))
        kind = kind.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), kind.annotations))
        return kind

    def visit_compilation_unit(self, compilation_unit: CompilationUnit, p: P) -> J:
        compilation_unit = compilation_unit.with_prefix(self.visit_space(compilation_unit.prefix, Space.Location.COMPILATION_UNIT_PREFIX, p))
        compilation_unit = compilation_unit.with_markers(self.visit_markers(compilation_unit.markers, p))
        compilation_unit = compilation_unit.padding.with_package_declaration(self.visit_right_padded(compilation_unit.padding.package_declaration, JRightPadded.Location.PACKAGE, p))
        compilation_unit = compilation_unit.padding.with_imports(list_map(lambda v: self.visit_right_padded(v, JRightPadded.Location.IMPORT, p), compilation_unit.padding.imports))
        compilation_unit = compilation_unit.with_classes(list_map(lambda v: self.visit_and_cast(v, ClassDeclaration, p), compilation_unit.classes))
        compilation_unit = compilation_unit.with_eof(self.visit_space(compilation_unit.eof, Space.Location.COMPILATION_UNIT_EOF, p))
        return compilation_unit

    def visit_continue(self, continue_: Continue, p: P) -> J:
        continue_ = continue_.with_prefix(self.visit_space(continue_.prefix, Space.Location.CONTINUE_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(continue_, p))
        if not isinstance(temp_statement, Continue):
            return temp_statement
        continue_ = cast(Continue, temp_statement)
        continue_ = continue_.with_markers(self.visit_markers(continue_.markers, p))
        continue_ = continue_.with_label(self.visit_and_cast(continue_.label, Identifier, p))
        return continue_

    def visit_do_while_loop(self, do_while_loop: DoWhileLoop, p: P) -> J:
        do_while_loop = do_while_loop.with_prefix(self.visit_space(do_while_loop.prefix, Space.Location.DO_WHILE_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(do_while_loop, p))
        if not isinstance(temp_statement, DoWhileLoop):
            return temp_statement
        do_while_loop = cast(DoWhileLoop, temp_statement)
        do_while_loop = do_while_loop.with_markers(self.visit_markers(do_while_loop.markers, p))
        do_while_loop = do_while_loop.padding.with_body(self.visit_right_padded(do_while_loop.padding.body, JRightPadded.Location.WHILE_BODY, p))
        do_while_loop = do_while_loop.padding.with_while_condition(self.visit_left_padded(do_while_loop.padding.while_condition, JLeftPadded.Location.WHILE_CONDITION, p))
        return do_while_loop

    def visit_empty(self, empty: Empty, p: P) -> J:
        empty = empty.with_prefix(self.visit_space(empty.prefix, Space.Location.EMPTY_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(empty, p))
        if not isinstance(temp_statement, Empty):
            return temp_statement
        empty = cast(Empty, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(empty, p))
        if not isinstance(temp_expression, Empty):
            return temp_expression
        empty = cast(Empty, temp_expression)
        empty = empty.with_markers(self.visit_markers(empty.markers, p))
        return empty

    def visit_enum_value(self, enum_value: EnumValue, p: P) -> J:
        enum_value = enum_value.with_prefix(self.visit_space(enum_value.prefix, Space.Location.ENUM_VALUE_PREFIX, p))
        enum_value = enum_value.with_markers(self.visit_markers(enum_value.markers, p))
        enum_value = enum_value.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), enum_value.annotations))
        enum_value = enum_value.with_name(self.visit_and_cast(enum_value.name, Identifier, p))
        enum_value = enum_value.with_initializer(self.visit_and_cast(enum_value.initializer, NewClass, p))
        return enum_value

    def visit_enum_value_set(self, enum_value_set: EnumValueSet, p: P) -> J:
        enum_value_set = enum_value_set.with_prefix(self.visit_space(enum_value_set.prefix, Space.Location.ENUM_VALUE_SET_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(enum_value_set, p))
        if not isinstance(temp_statement, EnumValueSet):
            return temp_statement
        enum_value_set = cast(EnumValueSet, temp_statement)
        enum_value_set = enum_value_set.with_markers(self.visit_markers(enum_value_set.markers, p))
        enum_value_set = enum_value_set.padding.with_enums(list_map(lambda v: self.visit_right_padded(v, JRightPadded.Location.ENUM_VALUE, p), enum_value_set.padding.enums))
        return enum_value_set

    def visit_field_access(self, field_access: FieldAccess, p: P) -> J:
        field_access = field_access.with_prefix(self.visit_space(field_access.prefix, Space.Location.FIELD_ACCESS_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(field_access, p))
        if not isinstance(temp_statement, FieldAccess):
            return temp_statement
        field_access = cast(FieldAccess, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(field_access, p))
        if not isinstance(temp_expression, FieldAccess):
            return temp_expression
        field_access = cast(FieldAccess, temp_expression)
        field_access = field_access.with_markers(self.visit_markers(field_access.markers, p))
        field_access = field_access.with_target(self.visit_and_cast(field_access.target, Expression, p))
        field_access = field_access.padding.with_name(self.visit_left_padded(field_access.padding.name, JLeftPadded.Location.FIELD_ACCESS_NAME, p))
        return field_access

    def visit_for_each_loop(self, for_each_loop: ForEachLoop, p: P) -> J:
        for_each_loop = for_each_loop.with_prefix(self.visit_space(for_each_loop.prefix, Space.Location.FOR_EACH_LOOP_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(for_each_loop, p))
        if not isinstance(temp_statement, ForEachLoop):
            return temp_statement
        for_each_loop = cast(ForEachLoop, temp_statement)
        for_each_loop = for_each_loop.with_markers(self.visit_markers(for_each_loop.markers, p))
        for_each_loop = for_each_loop.with_control(self.visit_and_cast(for_each_loop.control, ForEachLoop.Control, p))
        for_each_loop = for_each_loop.padding.with_body(self.visit_right_padded(for_each_loop.padding.body, JRightPadded.Location.FOR_BODY, p))
        return for_each_loop

    def visit_for_each_control(self, control: ForEachLoop.Control, p: P) -> J:
        control = control.with_prefix(self.visit_space(control.prefix, Space.Location.FOR_EACH_CONTROL_PREFIX, p))
        control = control.with_markers(self.visit_markers(control.markers, p))
        control = control.padding.with_variable(self.visit_right_padded(control.padding.variable, JRightPadded.Location.FOREACH_VARIABLE, p))
        control = control.padding.with_iterable(self.visit_right_padded(control.padding.iterable, JRightPadded.Location.FOREACH_ITERABLE, p))
        return control

    def visit_for_loop(self, for_loop: ForLoop, p: P) -> J:
        for_loop = for_loop.with_prefix(self.visit_space(for_loop.prefix, Space.Location.FOR_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(for_loop, p))
        if not isinstance(temp_statement, ForLoop):
            return temp_statement
        for_loop = cast(ForLoop, temp_statement)
        for_loop = for_loop.with_markers(self.visit_markers(for_loop.markers, p))
        for_loop = for_loop.with_control(self.visit_and_cast(for_loop.control, ForLoop.Control, p))
        for_loop = for_loop.padding.with_body(self.visit_right_padded(for_loop.padding.body, JRightPadded.Location.FOR_BODY, p))
        return for_loop

    def visit_for_control(self, control: ForLoop.Control, p: P) -> J:
        control = control.with_prefix(self.visit_space(control.prefix, Space.Location.FOR_CONTROL_PREFIX, p))
        control = control.with_markers(self.visit_markers(control.markers, p))
        control = control.padding.with_init(list_map(lambda v: self.visit_right_padded(v, JRightPadded.Location.FOR_INIT, p), control.padding.init))
        control = control.padding.with_condition(self.visit_right_padded(control.padding.condition, JRightPadded.Location.FOR_CONDITION, p))
        control = control.padding.with_update(list_map(lambda v: self.visit_right_padded(v, JRightPadded.Location.FOR_UPDATE, p), control.padding.update))
        return control

    def visit_parenthesized_type_tree(self, parenthesized_type_tree: ParenthesizedTypeTree, p: P) -> J:
        parenthesized_type_tree = parenthesized_type_tree.with_prefix(self.visit_space(parenthesized_type_tree.prefix, Space.Location.PARENTHESES_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(parenthesized_type_tree, p))
        if not isinstance(temp_expression, ParenthesizedTypeTree):
            return temp_expression
        parenthesized_type_tree = cast(ParenthesizedTypeTree, temp_expression)
        parenthesized_type_tree = parenthesized_type_tree.with_markers(self.visit_markers(parenthesized_type_tree.markers, p))
        parenthesized_type_tree = parenthesized_type_tree.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), parenthesized_type_tree.annotations))
        parenthesized_type_tree = parenthesized_type_tree.with_parenthesized_type(self.visit_and_cast(parenthesized_type_tree.parenthesized_type, Parentheses[TypeTree], p))
        return parenthesized_type_tree

    def visit_identifier(self, identifier: Identifier, p: P) -> J:
        identifier = identifier.with_prefix(self.visit_space(identifier.prefix, Space.Location.IDENTIFIER_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(identifier, p))
        if not isinstance(temp_expression, Identifier):
            return temp_expression
        identifier = cast(Identifier, temp_expression)
        identifier = identifier.with_markers(self.visit_markers(identifier.markers, p))
        identifier = identifier.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), identifier.annotations))
        return identifier

    def visit_if(self, if_: If, p: P) -> J:
        if_ = if_.with_prefix(self.visit_space(if_.prefix, Space.Location.IF_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(if_, p))
        if not isinstance(temp_statement, If):
            return temp_statement
        if_ = cast(If, temp_statement)
        if_ = if_.with_markers(self.visit_markers(if_.markers, p))
        if_ = if_.with_if_condition(self.visit_and_cast(if_.if_condition, ControlParentheses[Expression], p))
        if_ = if_.padding.with_then_part(self.visit_right_padded(if_.padding.then_part, JRightPadded.Location.IF_THEN, p))
        if_ = if_.with_else_part(self.visit_and_cast(if_.else_part, If.Else, p))
        return if_

    def visit_else(self, else_: If.Else, p: P) -> J:
        else_ = else_.with_prefix(self.visit_space(else_.prefix, Space.Location.ELSE_PREFIX, p))
        else_ = else_.with_markers(self.visit_markers(else_.markers, p))
        else_ = else_.padding.with_body(self.visit_right_padded(else_.padding.body, JRightPadded.Location.IF_ELSE, p))
        return else_

    def visit_import(self, import_: Import, p: P) -> J:
        import_ = import_.with_prefix(self.visit_space(import_.prefix, Space.Location.IMPORT_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(import_, p))
        if not isinstance(temp_statement, Import):
            return temp_statement
        import_ = cast(Import, temp_statement)
        import_ = import_.with_markers(self.visit_markers(import_.markers, p))
        import_ = import_.padding.with_static(self.visit_left_padded(import_.padding.static, JLeftPadded.Location.STATIC_IMPORT, p))
        import_ = import_.with_qualid(self.visit_and_cast(import_.qualid, FieldAccess, p))
        import_ = import_.padding.with_alias(self.visit_left_padded(import_.padding.alias, JLeftPadded.Location.IMPORT_ALIAS_PREFIX, p))
        return import_

    def visit_instance_of(self, instance_of: InstanceOf, p: P) -> J:
        instance_of = instance_of.with_prefix(self.visit_space(instance_of.prefix, Space.Location.INSTANCEOF_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(instance_of, p))
        if not isinstance(temp_expression, InstanceOf):
            return temp_expression
        instance_of = cast(InstanceOf, temp_expression)
        instance_of = instance_of.with_markers(self.visit_markers(instance_of.markers, p))
        instance_of = instance_of.padding.with_expression(self.visit_right_padded(instance_of.padding.expression, JRightPadded.Location.INSTANCEOF, p))
        instance_of = instance_of.with_clazz(self.visit_and_cast(instance_of.clazz, J, p))
        instance_of = instance_of.with_pattern(self.visit_and_cast(instance_of.pattern, J, p))
        return instance_of

    def visit_deconstruction_pattern(self, deconstruction_pattern: DeconstructionPattern, p: P) -> J:
        deconstruction_pattern = deconstruction_pattern.with_prefix(self.visit_space(deconstruction_pattern.prefix, Space.Location.DECONSTRUCTION_PATTERN_PREFIX, p))
        deconstruction_pattern = deconstruction_pattern.with_markers(self.visit_markers(deconstruction_pattern.markers, p))
        deconstruction_pattern = deconstruction_pattern.with_deconstructor(self.visit_and_cast(deconstruction_pattern.deconstructor, Expression, p))
        deconstruction_pattern = deconstruction_pattern.padding.with_nested(self.visit_container(deconstruction_pattern.padding.nested, JContainer.Location.DECONSTRUCTION_PATTERN_NESTED, p))
        return deconstruction_pattern

    def visit_intersection_type(self, intersection_type: IntersectionType, p: P) -> J:
        intersection_type = intersection_type.with_prefix(self.visit_space(intersection_type.prefix, Space.Location.INTERSECTION_TYPE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(intersection_type, p))
        if not isinstance(temp_expression, IntersectionType):
            return temp_expression
        intersection_type = cast(IntersectionType, temp_expression)
        intersection_type = intersection_type.with_markers(self.visit_markers(intersection_type.markers, p))
        intersection_type = intersection_type.padding.with_bounds(self.visit_container(intersection_type.padding.bounds, JContainer.Location.TYPE_BOUNDS, p))
        return intersection_type

    def visit_label(self, label: Label, p: P) -> J:
        label = label.with_prefix(self.visit_space(label.prefix, Space.Location.LABEL_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(label, p))
        if not isinstance(temp_statement, Label):
            return temp_statement
        label = cast(Label, temp_statement)
        label = label.with_markers(self.visit_markers(label.markers, p))
        label = label.padding.with_label(self.visit_right_padded(label.padding.label, JRightPadded.Location.LABEL, p))
        label = label.with_statement(self.visit_and_cast(label.statement, Statement, p))
        return label

    def visit_lambda(self, lambda_: Lambda, p: P) -> J:
        lambda_ = lambda_.with_prefix(self.visit_space(lambda_.prefix, Space.Location.LAMBDA_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(lambda_, p))
        if not isinstance(temp_statement, Lambda):
            return temp_statement
        lambda_ = cast(Lambda, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(lambda_, p))
        if not isinstance(temp_expression, Lambda):
            return temp_expression
        lambda_ = cast(Lambda, temp_expression)
        lambda_ = lambda_.with_markers(self.visit_markers(lambda_.markers, p))
        lambda_ = lambda_.with_parameters(self.visit_and_cast(lambda_.parameters, Lambda.Parameters, p))
        lambda_ = lambda_.with_arrow(self.visit_space(lambda_.arrow, Space.Location.LAMBDA_ARROW_PREFIX, p))
        lambda_ = lambda_.with_body(self.visit_and_cast(lambda_.body, J, p))
        return lambda_

    def visit_lambda_parameters(self, parameters: Lambda.Parameters, p: P) -> J:
        parameters = parameters.with_prefix(self.visit_space(parameters.prefix, Space.Location.LAMBDA_PARAMETERS_PREFIX, p))
        parameters = parameters.with_markers(self.visit_markers(parameters.markers, p))
        parameters = parameters.padding.with_parameters(list_map(lambda v: self.visit_right_padded(v, JRightPadded.Location.LAMBDA_PARAM, p), parameters.padding.parameters))
        return parameters

    def visit_literal(self, literal: Literal, p: P) -> J:
        literal = literal.with_prefix(self.visit_space(literal.prefix, Space.Location.LITERAL_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(literal, p))
        if not isinstance(temp_expression, Literal):
            return temp_expression
        literal = cast(Literal, temp_expression)
        literal = literal.with_markers(self.visit_markers(literal.markers, p))
        return literal

    def visit_member_reference(self, member_reference: MemberReference, p: P) -> J:
        member_reference = member_reference.with_prefix(self.visit_space(member_reference.prefix, Space.Location.MEMBER_REFERENCE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(member_reference, p))
        if not isinstance(temp_expression, MemberReference):
            return temp_expression
        member_reference = cast(MemberReference, temp_expression)
        member_reference = member_reference.with_markers(self.visit_markers(member_reference.markers, p))
        member_reference = member_reference.padding.with_containing(self.visit_right_padded(member_reference.padding.containing, JRightPadded.Location.MEMBER_REFERENCE_CONTAINING, p))
        member_reference = member_reference.padding.with_type_parameters(self.visit_container(member_reference.padding.type_parameters, JContainer.Location.TYPE_PARAMETERS, p))
        member_reference = member_reference.padding.with_reference(self.visit_left_padded(member_reference.padding.reference, JLeftPadded.Location.MEMBER_REFERENCE_NAME, p))
        return member_reference

    def visit_method_declaration(self, method_declaration: MethodDeclaration, p: P) -> J:
        method_declaration = method_declaration.with_prefix(self.visit_space(method_declaration.prefix, Space.Location.METHOD_DECLARATION_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(method_declaration, p))
        if not isinstance(temp_statement, MethodDeclaration):
            return temp_statement
        method_declaration = cast(MethodDeclaration, temp_statement)
        method_declaration = method_declaration.with_markers(self.visit_markers(method_declaration.markers, p))
        method_declaration = method_declaration.with_leading_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), method_declaration.leading_annotations))
        method_declaration = method_declaration.with_modifiers(list_map(lambda v: self.visit_and_cast(v, Modifier, p), method_declaration.modifiers))
        method_declaration = method_declaration.annotations.with_type_parameters(self.visit_and_cast(method_declaration.annotations.type_parameters, TypeParameters, p))
        method_declaration = method_declaration.with_return_type_expression(self.visit_and_cast(method_declaration.return_type_expression, TypeTree, p))
        method_declaration = method_declaration.annotations.with_name(method_declaration.annotations.name.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), method_declaration.annotations.name.annotations)).with_identifier(self.visit_and_cast(method_declaration.annotations.name.identifier, Identifier, p)))
        method_declaration = method_declaration.padding.with_parameters(self.visit_container(method_declaration.padding.parameters, JContainer.Location.METHOD_DECLARATION_PARAMETERS, p))
        method_declaration = method_declaration.padding.with_throws(self.visit_container(method_declaration.padding.throws, JContainer.Location.THROWS, p))
        method_declaration = method_declaration.with_body(self.visit_and_cast(method_declaration.body, Block, p))
        method_declaration = method_declaration.padding.with_default_value(self.visit_left_padded(method_declaration.padding.default_value, JLeftPadded.Location.METHOD_DECLARATION_DEFAULT_VALUE, p))
        return method_declaration

    def visit_method_invocation(self, method_invocation: MethodInvocation, p: P) -> J:
        method_invocation = method_invocation.with_prefix(self.visit_space(method_invocation.prefix, Space.Location.METHOD_INVOCATION_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(method_invocation, p))
        if not isinstance(temp_statement, MethodInvocation):
            return temp_statement
        method_invocation = cast(MethodInvocation, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(method_invocation, p))
        if not isinstance(temp_expression, MethodInvocation):
            return temp_expression
        method_invocation = cast(MethodInvocation, temp_expression)
        method_invocation = method_invocation.with_markers(self.visit_markers(method_invocation.markers, p))
        method_invocation = method_invocation.padding.with_select(self.visit_right_padded(method_invocation.padding.select, JRightPadded.Location.METHOD_SELECT, p))
        method_invocation = method_invocation.padding.with_type_parameters(self.visit_container(method_invocation.padding.type_parameters, JContainer.Location.TYPE_PARAMETERS, p))
        method_invocation = method_invocation.with_name(self.visit_and_cast(method_invocation.name, Identifier, p))
        method_invocation = method_invocation.padding.with_arguments(self.visit_container(method_invocation.padding.arguments, JContainer.Location.METHOD_INVOCATION_ARGUMENTS, p))
        return method_invocation

    def visit_modifier(self, modifier: Modifier, p: P) -> J:
        modifier = modifier.with_prefix(self.visit_space(modifier.prefix, Space.Location.MODIFIER_PREFIX, p))
        modifier = modifier.with_markers(self.visit_markers(modifier.markers, p))
        modifier = modifier.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), modifier.annotations))
        return modifier

    def visit_multi_catch(self, multi_catch: MultiCatch, p: P) -> J:
        multi_catch = multi_catch.with_prefix(self.visit_space(multi_catch.prefix, Space.Location.MULTI_CATCH_PREFIX, p))
        multi_catch = multi_catch.with_markers(self.visit_markers(multi_catch.markers, p))
        multi_catch = multi_catch.padding.with_alternatives(list_map(lambda v: self.visit_right_padded(v, JRightPadded.Location.CATCH_ALTERNATIVE, p), multi_catch.padding.alternatives))
        return multi_catch

    def visit_new_array(self, new_array: NewArray, p: P) -> J:
        new_array = new_array.with_prefix(self.visit_space(new_array.prefix, Space.Location.NEW_ARRAY_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(new_array, p))
        if not isinstance(temp_expression, NewArray):
            return temp_expression
        new_array = cast(NewArray, temp_expression)
        new_array = new_array.with_markers(self.visit_markers(new_array.markers, p))
        new_array = new_array.with_type_expression(self.visit_and_cast(new_array.type_expression, TypeTree, p))
        new_array = new_array.with_dimensions(list_map(lambda v: self.visit_and_cast(v, ArrayDimension, p), new_array.dimensions))
        new_array = new_array.padding.with_initializer(self.visit_container(new_array.padding.initializer, JContainer.Location.NEW_ARRAY_INITIALIZER, p))
        return new_array

    def visit_array_dimension(self, array_dimension: ArrayDimension, p: P) -> J:
        array_dimension = array_dimension.with_prefix(self.visit_space(array_dimension.prefix, Space.Location.DIMENSION_PREFIX, p))
        array_dimension = array_dimension.with_markers(self.visit_markers(array_dimension.markers, p))
        array_dimension = array_dimension.padding.with_index(self.visit_right_padded(array_dimension.padding.index, JRightPadded.Location.ARRAY_INDEX, p))
        return array_dimension

    def visit_new_class(self, new_class: NewClass, p: P) -> J:
        new_class = new_class.with_prefix(self.visit_space(new_class.prefix, Space.Location.NEW_CLASS_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(new_class, p))
        if not isinstance(temp_statement, NewClass):
            return temp_statement
        new_class = cast(NewClass, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(new_class, p))
        if not isinstance(temp_expression, NewClass):
            return temp_expression
        new_class = cast(NewClass, temp_expression)
        new_class = new_class.with_markers(self.visit_markers(new_class.markers, p))
        new_class = new_class.padding.with_enclosing(self.visit_right_padded(new_class.padding.enclosing, JRightPadded.Location.NEW_CLASS_ENCLOSING, p))
        new_class = new_class.with_new(self.visit_space(new_class.new, Space.Location.NEW_PREFIX, p))
        new_class = new_class.with_clazz(self.visit_and_cast(new_class.clazz, TypeTree, p))
        new_class = new_class.padding.with_arguments(self.visit_container(new_class.padding.arguments, JContainer.Location.NEW_CLASS_ARGUMENTS, p))
        new_class = new_class.with_body(self.visit_and_cast(new_class.body, Block, p))
        return new_class

    def visit_nullable_type(self, nullable_type: NullableType, p: P) -> J:
        nullable_type = nullable_type.with_prefix(self.visit_space(nullable_type.prefix, Space.Location.NULLABLE_TYPE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(nullable_type, p))
        if not isinstance(temp_expression, NullableType):
            return temp_expression
        nullable_type = cast(NullableType, temp_expression)
        nullable_type = nullable_type.with_markers(self.visit_markers(nullable_type.markers, p))
        nullable_type = nullable_type.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), nullable_type.annotations))
        nullable_type = nullable_type.padding.with_type_tree(self.visit_right_padded(nullable_type.padding.type_tree, JRightPadded.Location.NULLABLE, p))
        return nullable_type

    def visit_package(self, package: Package, p: P) -> J:
        package = package.with_prefix(self.visit_space(package.prefix, Space.Location.PACKAGE_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(package, p))
        if not isinstance(temp_statement, Package):
            return temp_statement
        package = cast(Package, temp_statement)
        package = package.with_markers(self.visit_markers(package.markers, p))
        package = package.with_expression(self.visit_and_cast(package.expression, Expression, p))
        package = package.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), package.annotations))
        return package

    def visit_parameterized_type(self, parameterized_type: ParameterizedType, p: P) -> J:
        parameterized_type = parameterized_type.with_prefix(self.visit_space(parameterized_type.prefix, Space.Location.PARAMETERIZED_TYPE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(parameterized_type, p))
        if not isinstance(temp_expression, ParameterizedType):
            return temp_expression
        parameterized_type = cast(ParameterizedType, temp_expression)
        parameterized_type = parameterized_type.with_markers(self.visit_markers(parameterized_type.markers, p))
        parameterized_type = parameterized_type.with_clazz(self.visit_and_cast(parameterized_type.clazz, NameTree, p))
        parameterized_type = parameterized_type.padding.with_type_parameters(self.visit_container(parameterized_type.padding.type_parameters, JContainer.Location.TYPE_PARAMETERS, p))
        return parameterized_type

    def visit_parentheses(self, parentheses: Parentheses[J2], p: P) -> J:
        parentheses = parentheses.with_prefix(self.visit_space(parentheses.prefix, Space.Location.PARENTHESES_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(parentheses, p))
        if not isinstance(temp_expression, Parentheses):
            return temp_expression
        parentheses = cast(Parentheses[J2], temp_expression)
        parentheses = parentheses.with_markers(self.visit_markers(parentheses.markers, p))
        parentheses = parentheses.padding.with_tree(self.visit_right_padded(parentheses.padding.tree, JRightPadded.Location.PARENTHESES, p))
        return parentheses

    def visit_control_parentheses(self, control_parentheses: ControlParentheses[J2], p: P) -> J:
        control_parentheses = control_parentheses.with_prefix(self.visit_space(control_parentheses.prefix, Space.Location.CONTROL_PARENTHESES_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(control_parentheses, p))
        if not isinstance(temp_expression, ControlParentheses):
            return temp_expression
        control_parentheses = cast(ControlParentheses[J2], temp_expression)
        control_parentheses = control_parentheses.with_markers(self.visit_markers(control_parentheses.markers, p))
        control_parentheses = control_parentheses.padding.with_tree(self.visit_right_padded(control_parentheses.padding.tree, JRightPadded.Location.PARENTHESES, p))
        return control_parentheses

    def visit_primitive(self, primitive: Primitive, p: P) -> J:
        primitive = primitive.with_prefix(self.visit_space(primitive.prefix, Space.Location.PRIMITIVE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(primitive, p))
        if not isinstance(temp_expression, Primitive):
            return temp_expression
        primitive = cast(Primitive, temp_expression)
        primitive = primitive.with_markers(self.visit_markers(primitive.markers, p))
        return primitive

    def visit_return(self, return_: Return, p: P) -> J:
        return_ = return_.with_prefix(self.visit_space(return_.prefix, Space.Location.RETURN_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(return_, p))
        if not isinstance(temp_statement, Return):
            return temp_statement
        return_ = cast(Return, temp_statement)
        return_ = return_.with_markers(self.visit_markers(return_.markers, p))
        return_ = return_.with_expression(self.visit_and_cast(return_.expression, Expression, p))
        return return_

    def visit_switch(self, switch: Switch, p: P) -> J:
        switch = switch.with_prefix(self.visit_space(switch.prefix, Space.Location.SWITCH_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(switch, p))
        if not isinstance(temp_statement, Switch):
            return temp_statement
        switch = cast(Switch, temp_statement)
        switch = switch.with_markers(self.visit_markers(switch.markers, p))
        switch = switch.with_selector(self.visit_and_cast(switch.selector, ControlParentheses[Expression], p))
        switch = switch.with_cases(self.visit_and_cast(switch.cases, Block, p))
        return switch

    def visit_switch_expression(self, switch_expression: SwitchExpression, p: P) -> J:
        switch_expression = switch_expression.with_prefix(self.visit_space(switch_expression.prefix, Space.Location.SWITCH_EXPRESSION_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(switch_expression, p))
        if not isinstance(temp_expression, SwitchExpression):
            return temp_expression
        switch_expression = cast(SwitchExpression, temp_expression)
        switch_expression = switch_expression.with_markers(self.visit_markers(switch_expression.markers, p))
        switch_expression = switch_expression.with_selector(self.visit_and_cast(switch_expression.selector, ControlParentheses[Expression], p))
        switch_expression = switch_expression.with_cases(self.visit_and_cast(switch_expression.cases, Block, p))
        return switch_expression

    def visit_synchronized(self, synchronized: Synchronized, p: P) -> J:
        synchronized = synchronized.with_prefix(self.visit_space(synchronized.prefix, Space.Location.SYNCHRONIZED_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(synchronized, p))
        if not isinstance(temp_statement, Synchronized):
            return temp_statement
        synchronized = cast(Synchronized, temp_statement)
        synchronized = synchronized.with_markers(self.visit_markers(synchronized.markers, p))
        synchronized = synchronized.with_lock(self.visit_and_cast(synchronized.lock, ControlParentheses[Expression], p))
        synchronized = synchronized.with_body(self.visit_and_cast(synchronized.body, Block, p))
        return synchronized

    def visit_ternary(self, ternary: Ternary, p: P) -> J:
        ternary = ternary.with_prefix(self.visit_space(ternary.prefix, Space.Location.TERNARY_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(ternary, p))
        if not isinstance(temp_statement, Ternary):
            return temp_statement
        ternary = cast(Ternary, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(ternary, p))
        if not isinstance(temp_expression, Ternary):
            return temp_expression
        ternary = cast(Ternary, temp_expression)
        ternary = ternary.with_markers(self.visit_markers(ternary.markers, p))
        ternary = ternary.with_condition(self.visit_and_cast(ternary.condition, Expression, p))
        ternary = ternary.padding.with_true_part(self.visit_left_padded(ternary.padding.true_part, JLeftPadded.Location.TERNARY_TRUE, p))
        ternary = ternary.padding.with_false_part(self.visit_left_padded(ternary.padding.false_part, JLeftPadded.Location.TERNARY_FALSE, p))
        return ternary

    def visit_throw(self, throw: Throw, p: P) -> J:
        throw = throw.with_prefix(self.visit_space(throw.prefix, Space.Location.THROW_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(throw, p))
        if not isinstance(temp_statement, Throw):
            return temp_statement
        throw = cast(Throw, temp_statement)
        throw = throw.with_markers(self.visit_markers(throw.markers, p))
        throw = throw.with_exception(self.visit_and_cast(throw.exception, Expression, p))
        return throw

    def visit_try(self, try_: Try, p: P) -> J:
        try_ = try_.with_prefix(self.visit_space(try_.prefix, Space.Location.TRY_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(try_, p))
        if not isinstance(temp_statement, Try):
            return temp_statement
        try_ = cast(Try, temp_statement)
        try_ = try_.with_markers(self.visit_markers(try_.markers, p))
        try_ = try_.padding.with_resources(self.visit_container(try_.padding.resources, JContainer.Location.TRY_RESOURCES, p))
        try_ = try_.with_body(self.visit_and_cast(try_.body, Block, p))
        try_ = try_.with_catches(list_map(lambda v: self.visit_and_cast(v, Try.Catch, p), try_.catches))
        try_ = try_.padding.with_finally(self.visit_left_padded(try_.padding.finally_, JLeftPadded.Location.TRY_FINALLY, p))
        return try_

    def visit_try_resource(self, resource: Try.Resource, p: P) -> J:
        resource = resource.with_prefix(self.visit_space(resource.prefix, Space.Location.TRY_RESOURCE, p))
        resource = resource.with_markers(self.visit_markers(resource.markers, p))
        resource = resource.with_variable_declarations(self.visit_and_cast(resource.variable_declarations, TypedTree, p))
        return resource

    def visit_catch(self, catch: Try.Catch, p: P) -> J:
        catch = catch.with_prefix(self.visit_space(catch.prefix, Space.Location.CATCH_PREFIX, p))
        catch = catch.with_markers(self.visit_markers(catch.markers, p))
        catch = catch.with_parameter(self.visit_and_cast(catch.parameter, ControlParentheses[VariableDeclarations], p))
        catch = catch.with_body(self.visit_and_cast(catch.body, Block, p))
        return catch

    def visit_type_cast(self, type_cast: TypeCast, p: P) -> J:
        type_cast = type_cast.with_prefix(self.visit_space(type_cast.prefix, Space.Location.TYPE_CAST_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(type_cast, p))
        if not isinstance(temp_expression, TypeCast):
            return temp_expression
        type_cast = cast(TypeCast, temp_expression)
        type_cast = type_cast.with_markers(self.visit_markers(type_cast.markers, p))
        type_cast = type_cast.with_clazz(self.visit_and_cast(type_cast.clazz, ControlParentheses[TypeTree], p))
        type_cast = type_cast.with_expression(self.visit_and_cast(type_cast.expression, Expression, p))
        return type_cast

    def visit_type_parameter(self, type_parameter: TypeParameter, p: P) -> J:
        type_parameter = type_parameter.with_prefix(self.visit_space(type_parameter.prefix, Space.Location.TYPE_PARAMETERS_PREFIX, p))
        type_parameter = type_parameter.with_markers(self.visit_markers(type_parameter.markers, p))
        type_parameter = type_parameter.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), type_parameter.annotations))
        type_parameter = type_parameter.with_modifiers(list_map(lambda v: self.visit_and_cast(v, Modifier, p), type_parameter.modifiers))
        type_parameter = type_parameter.with_name(self.visit_and_cast(type_parameter.name, Expression, p))
        type_parameter = type_parameter.padding.with_bounds(self.visit_container(type_parameter.padding.bounds, JContainer.Location.TYPE_BOUNDS, p))
        return type_parameter

    def visit_type_parameters(self, type_parameters: TypeParameters, p: P) -> J:
        type_parameters = type_parameters.with_prefix(self.visit_space(type_parameters.prefix, Space.Location.TYPE_PARAMETERS_PREFIX, p))
        type_parameters = type_parameters.with_markers(self.visit_markers(type_parameters.markers, p))
        type_parameters = type_parameters.with_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), type_parameters.annotations))
        type_parameters = type_parameters.padding.with_type_parameters(list_map(lambda v: self.visit_right_padded(v, JRightPadded.Location.TYPE_PARAMETER, p), type_parameters.padding.type_parameters))
        return type_parameters

    def visit_unary(self, unary: Unary, p: P) -> J:
        unary = unary.with_prefix(self.visit_space(unary.prefix, Space.Location.UNARY_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(unary, p))
        if not isinstance(temp_statement, Unary):
            return temp_statement
        unary = cast(Unary, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(unary, p))
        if not isinstance(temp_expression, Unary):
            return temp_expression
        unary = cast(Unary, temp_expression)
        unary = unary.with_markers(self.visit_markers(unary.markers, p))
        unary = unary.padding.with_operator(self.visit_left_padded(unary.padding.operator, JLeftPadded.Location.UNARY_OPERATOR, p))
        unary = unary.with_expression(self.visit_and_cast(unary.expression, Expression, p))
        return unary

    def visit_variable_declarations(self, variable_declarations: VariableDeclarations, p: P) -> J:
        variable_declarations = variable_declarations.with_prefix(self.visit_space(variable_declarations.prefix, Space.Location.VARIABLE_DECLARATIONS_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(variable_declarations, p))
        if not isinstance(temp_statement, VariableDeclarations):
            return temp_statement
        variable_declarations = cast(VariableDeclarations, temp_statement)
        variable_declarations = variable_declarations.with_markers(self.visit_markers(variable_declarations.markers, p))
        variable_declarations = variable_declarations.with_leading_annotations(list_map(lambda v: self.visit_and_cast(v, Annotation, p), variable_declarations.leading_annotations))
        variable_declarations = variable_declarations.with_modifiers(list_map(lambda v: self.visit_and_cast(v, Modifier, p), variable_declarations.modifiers))
        variable_declarations = variable_declarations.with_type_expression(self.visit_and_cast(variable_declarations.type_expression, TypeTree, p))
        variable_declarations = variable_declarations.with_varargs(self.visit_space(variable_declarations.varargs, Space.Location.VARARGS, p))
        variable_declarations = variable_declarations.with_dimensions_before_name(list_map(lambda v: v.with_before(self.visit_space(v.before, Space.Location.DIMENSION_PREFIX, p)).with_element(self.visit_space(v.element, Space.Location.DIMENSION, p)), variable_declarations.dimensions_before_name))
        variable_declarations = variable_declarations.padding.with_variables(list_map(lambda v: self.visit_right_padded(v, JRightPadded.Location.NAMED_VARIABLE, p), variable_declarations.padding.variables))
        return variable_declarations

    def visit_variable(self, named_variable: VariableDeclarations.NamedVariable, p: P) -> J:
        named_variable = named_variable.with_prefix(self.visit_space(named_variable.prefix, Space.Location.VARIABLE_PREFIX, p))
        named_variable = named_variable.with_markers(self.visit_markers(named_variable.markers, p))
        named_variable = named_variable.with_name(self.visit_and_cast(named_variable.name, Identifier, p))
        named_variable = named_variable.with_dimensions_after_name(list_map(lambda v: v.with_before(self.visit_space(v.before, Space.Location.DIMENSION_PREFIX, p)).with_element(self.visit_space(v.element, Space.Location.DIMENSION, p)), named_variable.dimensions_after_name))
        named_variable = named_variable.padding.with_initializer(self.visit_left_padded(named_variable.padding.initializer, JLeftPadded.Location.VARIABLE_INITIALIZER, p))
        return named_variable

    def visit_while_loop(self, while_loop: WhileLoop, p: P) -> J:
        while_loop = while_loop.with_prefix(self.visit_space(while_loop.prefix, Space.Location.WHILE_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(while_loop, p))
        if not isinstance(temp_statement, WhileLoop):
            return temp_statement
        while_loop = cast(WhileLoop, temp_statement)
        while_loop = while_loop.with_markers(self.visit_markers(while_loop.markers, p))
        while_loop = while_loop.with_condition(self.visit_and_cast(while_loop.condition, ControlParentheses[Expression], p))
        while_loop = while_loop.padding.with_body(self.visit_right_padded(while_loop.padding.body, JRightPadded.Location.WHILE_BODY, p))
        return while_loop

    def visit_wildcard(self, wildcard: Wildcard, p: P) -> J:
        wildcard = wildcard.with_prefix(self.visit_space(wildcard.prefix, Space.Location.WILDCARD_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(wildcard, p))
        if not isinstance(temp_expression, Wildcard):
            return temp_expression
        wildcard = cast(Wildcard, temp_expression)
        wildcard = wildcard.with_markers(self.visit_markers(wildcard.markers, p))
        wildcard = wildcard.padding.with_bound(self.visit_left_padded(wildcard.padding.bound, JLeftPadded.Location.WILDCARD_BOUND, p))
        wildcard = wildcard.with_bounded_type(self.visit_and_cast(wildcard.bounded_type, NameTree, p))
        return wildcard

    def visit_yield(self, yield_: Yield, p: P) -> J:
        yield_ = yield_.with_prefix(self.visit_space(yield_.prefix, Space.Location.YIELD_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(yield_, p))
        if not isinstance(temp_statement, Yield):
            return temp_statement
        yield_ = cast(Yield, temp_statement)
        yield_ = yield_.with_markers(self.visit_markers(yield_.markers, p))
        yield_ = yield_.with_value(self.visit_and_cast(yield_.value, Expression, p))
        return yield_

    def visit_unknown(self, unknown: Unknown, p: P) -> J:
        unknown = unknown.with_prefix(self.visit_space(unknown.prefix, Space.Location.UNKNOWN_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(unknown, p))
        if not isinstance(temp_statement, Unknown):
            return temp_statement
        unknown = cast(Unknown, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(unknown, p))
        if not isinstance(temp_expression, Unknown):
            return temp_expression
        unknown = cast(Unknown, temp_expression)
        unknown = unknown.with_markers(self.visit_markers(unknown.markers, p))
        unknown = unknown.with_source(self.visit_and_cast(unknown.source, Unknown.Source, p))
        return unknown

    def visit_unknown_source(self, source: Unknown.Source, p: P) -> J:
        source = source.with_prefix(self.visit_space(source.prefix, Space.Location.UNKNOWN_SOURCE_PREFIX, p))
        source = source.with_markers(self.visit_markers(source.markers, p))
        return source

    def visit_erroneous(self, erroneous: Erroneous, p: P) -> J:
        erroneous = erroneous.with_prefix(self.visit_space(erroneous.prefix, Space.Location.ERRONEOUS_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(erroneous, p))
        if not isinstance(temp_statement, Erroneous):
            return temp_statement
        erroneous = cast(Erroneous, temp_statement)
        temp_expression = cast(Expression, self.visit_expression(erroneous, p))
        if not isinstance(temp_expression, Erroneous):
            return temp_expression
        erroneous = cast(Erroneous, temp_expression)
        erroneous = erroneous.with_markers(self.visit_markers(erroneous.markers, p))
        return erroneous

    def visit_container(self, container: Optional[JContainer[J2]], loc: JContainer.Location, p: P) -> JContainer[J2]:
        return extensions.visit_container(self, container, loc, p)

    def visit_left_padded(self, left: Optional[JLeftPadded[T]], loc: JLeftPadded.Location, p: P) -> Optional[JLeftPadded[T]]:
        return extensions.visit_left_padded(self, left, loc, p)

    def visit_right_padded(self, right: Optional[JRightPadded[T]], loc: JRightPadded.Location, p: P) -> Optional[JRightPadded[T]]:
        return extensions.visit_right_padded(self, right, loc, p)

    def visit_space(self, space: Optional[Space], loc: Optional[Space.Location], p: P) -> Space:
        return extensions.visit_space(self, space, loc, p)
