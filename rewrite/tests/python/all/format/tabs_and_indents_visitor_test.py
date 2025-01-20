import pytest

from rewrite.python import IntelliJ
from rewrite.python.format import TabsAndIndentsVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_multi_assignment():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def assign_values():
             a, b = 1, 2
             x, y, z = 3, 4, 5
             return a, b, x, y, z
            """,
            """
            def assign_values():
                a, b = 1, 2
                x, y, z = 3, 4, 5
                return a, b, x, y, z
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
        # spec = RecipeSpec().with_recipes(from_visitor(AutoFormatVisitor()))
    )


def test_if_else_statement():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def check_value(x):
             if x > 0:
              return "Positive"
             else:
              return "Non-positive"
            """,
            """
            def check_value(x):
                if x > 0:
                    return "Positive"
                else:
                    return "Non-positive"
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_if_else_statement_no_else_with_extra_statements():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def check_value(x):
             if x > 0:
              a = 1 + x
              return "Positive"
             a = -1 + x
             return "Non-positive"
            """,
            """
            def check_value(x):
                if x > 0:
                    a = 1 + x
                    return "Positive"
                a = -1 + x
                return "Non-positive"
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_if_else_statement_no_else_multi_return_values():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """\
            def check_value(x):
              if x > 0:
                a = 1 + x
                return a, "Positive"
              return a
            """,
            """\
            def check_value(x):
                if x > 0:
                    a = 1 + x
                    return a, "Positive"
                return a
            """
        ),
        # spec=RecipeSpec().with_recipes(from_visitor(AutoFormatVisitor()))
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_if_else_statement_no_else_multi_return_values_as_tuple():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """\
            def check_value(x):
              if x > 0:
                a = 1 + x
                return (a, "Positive")
              return a
            """,
            """\
            def check_value(x):
                if x > 0:
                    a = 1 + x
                    return (a, "Positive")
                return a
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_if_elif_else_statement():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def check_value(x):
             if x > 0:
              return "Positive"
             elif x < 0:
              return "Negative"
             else:
              return "Null"
            """,
            """
            def check_value(x):
                if x > 0:
                    return "Positive"
                elif x < 0:
                    return "Negative"
                else:
                    return "Null"
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_for_statement():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def sum_list(lst):
             total = 0
             for num in lst:
              total += num
             return total
            """,
            """
            def sum_list(lst):
                total = 0
                for num in lst:
                    total += num
                return total
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_for_statement_with_list_comprehension():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def even_numbers(lst):
             return [x for x in lst if x % 2 == 0]
            """,
            """
            def even_numbers(lst):
                return [x for x in lst if x % 2 == 0]
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_for_statement_with_list_comprehension_multiline():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def even_numbers(lst):
             return [x for x
                in lst if x % 2 == 0]
            """,
            """
            def even_numbers(lst):
                return [x for x
                    in lst if x % 2 == 0]
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_while_statement():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def countdown(n):
             while n > 0:
              print(n)
              n -= 1
            """,
            """
            def countdown(n):
                while n > 0:
                    print(n)
                    n -= 1
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_class_statement():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            class MyClass:
             def __init__(self, value):
              self.value = value
             def get_value(self):
              return self.value
            """,
            """
            class MyClass:
                def __init__(self, value):
                    self.value = value
                def get_value(self):
                    return self.value
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_with_statement():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def read_file(file_path):
             with open(file_path, 'r') as file:
              content = file.read()
             return content
            """,
            """
            def read_file(file_path):
                with open(file_path, 'r') as file:
                    content = file.read()
                return content
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_try_statement_basic():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def divide(a, b):
             try:
              c = a / b
             except ZeroDivisionError:
              return None
             return c
            """,
            """
            def divide(a, b):
                try:
                    c = a / b
                except ZeroDivisionError:
                    return None
                return c
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_try_statement_with_multi_return():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def divide(a, b):
             try:
              c = a / b
              if c > 42: return a, c
             except ZeroDivisionError:
              return None
             return a, b
            """,
            """
            def divide(a, b):
                try:
                    c = a / b
                    if c > 42: return a, c
                except ZeroDivisionError:
                    return None
                return a, b
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_basic_indent_modification():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(2).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            '''
            def my_function():
              return None
            ''',
            '''
            def my_function():
                return None
            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_multiline_list():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(
        4).with_continuation_indent(8)
    rewrite_run(
        # language=python
        python(
            """\
            my_list = [ #cool
              1,
                 2,
                    3,
                4
            ]
            """,
            """\
            my_list = [ #cool
                1,
                2,
                3,
                4
            ]
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_multiline_call_with_positional_args_no_align_multiline():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    # noinspection PyInconsistentIndentation
    rewrite_run(
        # language=python
        python(
            """
            def long_function_name(var_one, var_two,
                    var_three,
                    var_four):
                print(var_one)
            """,
            """
            def long_function_name(var_one, var_two,
                    var_three,
                    var_four):
                print(var_one)
            """
        ),
        spec=RecipeSpec()
        .with_recipes(
            from_visitor(TabsAndIndentsVisitor(style))
        )
    )


def test_multiline_call_with_positional_args_and_no_arg_first_line():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    # noinspection PyInconsistentIndentation
    rewrite_run(
        # language=python
        python(
            """
            def long_function_name(
                var_one,
                        var_two, var_three,
                    var_four):
                print(var_one)
            """,
            """
            def long_function_name(
                    var_one,
                    var_two, var_three,
                    var_four):
                print(var_one)
            """
        ),
        spec=RecipeSpec()
        .with_recipes(
            from_visitor(TabsAndIndentsVisitor(style))
        )
    )


def test_multiline_call_with_args_without_multiline_align():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            """
            result = long_function_name(10, 'foo',
               another_arg=42,
                final_arg="bar")
            """,
            """
            result = long_function_name(10, 'foo',
                another_arg=42,
                final_arg="bar")
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_multiline_list_inside_function():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def create_list():
              my_list = [
                1,
                     2,
                 3,
                4
                ]
              return my_list
            """,
            """
            def create_list():
                my_list = [
                    1,
                    2,
                    3,
                    4
                ]
                return my_list
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )

def test_multiline_list_inside_function_with_trailing_comma():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def create_list():
              my_list = [
                1,
                     2,
                 3,
                4,
                ]
              return my_list
            """,
            """
            def create_list():
                my_list = [
                    1,
                    2,
                    3,
                    4,
                ]
                return my_list
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_basic_dictionary():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4).with_indent_size(4)
    rewrite_run(
        # language=python
        python(
            """
            config = {
             "key1": "value1",
             "key2": "value2"
            }
            """,
            """
            config = {
                "key1": "value1",
                "key2": "value2"
            }
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_nested_dictionary():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            """
            config = {
            "section": {
             "key1": "value1",
             "key2": [10, 20,
             30]
            },
             "another_section": {"nested_key": "val"}
            }
            """,
            """
            config = {
                "section": {
                    "key1": "value1",
                    "key2": [10, 20,
                        30]
                },
                "another_section": {"nested_key": "val"}
            }
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_nested_dictionary_with_trailing_commas():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            """
            config = {
            "section": {
             "key1": "value1",
             "key2": [10, 20,
             30],
            },
             "another_section": {"nested_key": "val"}
            }
            """,
            """
            config = {
                "section": {
                    "key1": "value1",
                    "key2": [10, 20,
                        30],
                },
                "another_section": {"nested_key": "val"}
            }
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_list_comprehension():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def even_numbers(n):
             return [x for x in range(n)
             if x % 2 == 0]
            """,
            """
            def even_numbers(n):
                return [x for x in range(n)
                    if x % 2 == 0]
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_comment_alignment():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            '''
                # Informative comment 1
            def my_function(a, b):
              # Informative comment 2

              # Informative comment 3
              if a > b:
                # cool
                a = b + 1
              return None # Informative comment 4
              # Informative comment 5
            ''',
            '''
            # Informative comment 1
            def my_function(a, b):
                # Informative comment 2

                # Informative comment 3
                if a > b:
                    # cool
                    a = b + 1
                return None # Informative comment 4
            # Informative comment 5
            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )
    return None


def test_comment_alignment_if_and_return():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            '''
            def my_function(a, b):
              if a > b:
                # cool
                a = b + 1
                # cool
              return None
            ''',
            '''
            def my_function(a, b):
                if a > b:
                    # cool
                    a = b + 1
                # cool
                return None
            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )
    return None


def test_string_literal_assignment():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            '''
             a = """
             This is a string that
             should not be modified.
             """
            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_string_literal_assignment_in_function():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            '''
            def my_function():
             a = """
             This is a string that
             should align with the function body.
             """
             return None
            ''',
            '''
            def my_function():
                a = """
             This is a string that
             should align with the function body.
             """
                return None
            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_string_literal_comment():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            '''
            1+1
            """
            This is a comment that
            should not be modified.
            """
            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_int_literal():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            '''
            1
            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_docstring_alignment():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            '''
            def my_function():
              """
              This is a docstring that
              should align with the function body.
              """
              return None
            ''',
            '''
            def my_function():
                """
                This is a docstring that
                should align with the function body.
                """
                return None
            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_method_select_suffix_already_correct():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            """
            x = ("foo".startswith("f"))
            """),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_top_level_string():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            """
            'foo'
            """),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


@pytest.mark.xfail
def test_method_select_suffix_new_line_already_correct():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            """
            x = ("foo"
                 .startswith("f"))
            """),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


@pytest.mark.xfail
def test_method_select_suffix():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            """
            x = ("foo"
                .startswith("f"))
            """,
            """
            x = ("foo"
                 .startswith("f"))
            """),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )
