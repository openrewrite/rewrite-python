from rewrite.python import IntelliJ
from rewrite.python.format import TabsAndIndentsVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_multiline_call_with_post_arg_only():
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


def test_multiline_call_with_args():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
    rewrite_run(
        # language=python
        python(
            """
            def example_function():
             result = some_method(10, 'foo',
            another_arg=42,
            final_arg="bar")
             return result
            """,
            """
            def example_function():
                result = some_method(10, 'foo',
                                     another_arg=42,
                                     final_arg="bar")
                return result
            """
        ),
        spec=RecipeSpec().with_recipes(from_visitor(TabsAndIndentsVisitor(style)))
    )


def test_multiline_list():
    style = IntelliJ.tabs_and_indents().with_use_tab_character(False).with_tab_size(4)
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
             return [ x for x in range(n)
             if x % 2 == 0]
            """,
            """
            def even_numbers(n):
                return [
                    x for x in range(n)
                    if x % 2 == 0
                ]
            """
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
