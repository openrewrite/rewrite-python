import pytest

from rewrite.test import rewrite_run, python


def test_none():
    # language=python
    rewrite_run(python("assert None"))


def test_boolean():
    # language=python
    rewrite_run(python("assert True"))
    # language=python
    rewrite_run(python("assert False"))


def test_dec_int():
    # language=python
    rewrite_run(python("assert 0"))


def test_hex_int():
    # language=python
    rewrite_run(python("assert 0x1f"))


def test_fraction():
    # language=python
    rewrite_run(python("assert 0.000"))


def test_fraction_leading_dot():
    # language=python
    rewrite_run(python("assert .0"))


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


@pytest.mark.xfail(reason="Still needs to be built using lexer", strict=True)
def test_string_literal_concatenation():
    # language=python
    rewrite_run(python("assert 'a' 'b'"))


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


def test_double_quoted_string():
    # language=python
    rewrite_run(python('assert "foo"'))
