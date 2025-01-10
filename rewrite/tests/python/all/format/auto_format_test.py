from rewrite.python.format import AutoFormatVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_intellij_tabs_and_indents_example_should_not_be_changed():
    rewrite_run(
        # language=python
        python(
            '''\
            def foo():
                print('bar')


            def long_function_name(
                    var_one, var_two, var_three,
                    var_four):
                print(var_one)
            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(AutoFormatVisitor()))
    )
    return None


def test_intellij_spaces_example_should_not_be_changed():
    rewrite_run(
        # language=python
        python(
            '''\
            def settings_preview(argument, key=value):
                dict = {1: 'a', 2: 'b', 3: 'c'}
                x = dict[1]
                expr = (1 + 2) * 3 << 4 ** 5 & 16
                if expr == 0 or abs(expr) < 0: print('weird'); return
                settings_preview(key=1)

            foo = \
                bar


            def no_params():
                return globals()

            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(AutoFormatVisitor()))
    )
    return None


def test_intellij_blank_lines_should_not_be_changed():
    rewrite_run(
        # language=python
        python(
            '''\
            import os


            class C(object):
                import sys
                x = 1

                def foo(self):
                    import platform
                    print(platform.processor())

            '''
        ),
        spec=RecipeSpec().with_recipes(from_visitor(AutoFormatVisitor()))
    )
    return None
