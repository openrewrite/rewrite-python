from typing import Type, Optional, TypeVar

from rewrite import Tree
from rewrite.java import Literal, JavaType
from rewrite.python import PythonVisitor
from rewrite.test import rewrite_run, python

T = TypeVar('T', bound=Tree)


def test_none():
    def after_recipe(cu):
        assert find_first(cu, Literal).type == JavaType.Primitive.None_

    # language=python
    rewrite_run(python("assert None", after_recipe=after_recipe))


def test_boolean():
    def after_recipe(cu):
        assert find_first(cu, Literal).type == JavaType.Primitive.Boolean

    # language=python
    rewrite_run(python("assert True", after_recipe=after_recipe))
    rewrite_run(python("assert False", after_recipe=after_recipe))


def test_dec_int():
    def after_recipe(cu):
        assert find_first(cu, Literal).type == JavaType.Primitive.Int

    # language=python
    rewrite_run(python("assert 0", after_recipe=after_recipe))


def test_hex_int():
    def after_recipe(cu):
        assert find_first(cu, Literal).type == JavaType.Primitive.Int

    # language=python
    rewrite_run(python("assert 0x1f", after_recipe=after_recipe))


def test_fraction():
    def after_recipe(cu):
        assert find_first(cu, Literal).type == JavaType.Primitive.Double

    # language=python
    rewrite_run(python("assert 0.000", after_recipe=after_recipe))


def test_fraction_leading_dot():
    def after_recipe(cu):
        assert find_first(cu, Literal).type == JavaType.Primitive.Double

    # language=python
    rewrite_run(python("assert .0", after_recipe=after_recipe))


def test_large_int():
    def after_recipe(cu):
        assert find_first(cu, Literal).type == JavaType.Primitive.Int

    # language=python
    rewrite_run(python("assert 0xC03A0019", after_recipe=after_recipe))


def test_byte_string_concatenation():
    def after_recipe(cu):
        assert find_first(cu, Literal).type == JavaType.Primitive.Double

    # language=python
    rewrite_run(python("assert b'hello' b'world'", after_recipe=after_recipe))


def test_bigint():
    def after_recipe(cu):
        assert find_first(cu, Literal).type == JavaType.Primitive.Int

    # language=python
    rewrite_run(python("assert 9223372036854775808", after_recipe=after_recipe))


def test_single_quoted_string():
    # language=python
    rewrite_run(python("assert 'foo'"))


def test_string_with_space():
    # language=python
    rewrite_run(python("assert 'foo bar'"))


def test_string_with_escaped_quote():
    # language=python
    rewrite_run(python("assert 'foo\\'bar'"))


def test_string_with_flags():
    # language=python
    rewrite_run(python("assert u'\u0394 (delta)'"))


def test_false_string_literal_concatenation():
    # language=python
    rewrite_run(
        python("""
               "a"
               b"b"
               """
               )
    )


def test_string_literal_concatenation_1():
    # language=python
    rewrite_run(python("assert 'a' 'b'"))


def test_string_literal_concatenation_2():
    # language=python
    rewrite_run(
        python(
            """ \
            assert ('a'
                    'b'
                    'c'
                    )
            """
        )
    )


def test_string_literal_concatenation_with_comments():
    # language=python
    rewrite_run(
        python(
            """ \
            assert ('a'
                    'b'
                    # foo
                    'c'
                    )
            """
        )
    )


def test_bytes():
    # language=python
    rewrite_run(python("assert b'\x68\x65\x6c\x6c\x6f'"))


def test_multiline_string_with_flags():
    # language=python
    rewrite_run(
        python(
            """\
            assert '''this is a
            multiline string
            '''
            """
        )
    )


def test_string_concatenation():
    # language=python
    rewrite_run(
        python(
            """\
            raise Exception(
                'foo'
                'bar'
            )
            """
        )
    )


def test_double_quoted_string():
    # language=python
    rewrite_run(python('assert "foo"'))


def find_first(tree: Tree, clazz: Type[T]) -> T:
    class Find(PythonVisitor[list[Tree]]):
        def visit(self, t: Tree, p: list[Tree]) -> Optional[Tree]:
            if isinstance(t, clazz):
                p.append(t)
                return t
            return super().visit(t, p)

    found = []
    Find().visit(tree, found)
    return found[0]
