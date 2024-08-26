import pytest

from rewrite.test import rewrite_run, python


@pytest.mark.parametrize('style', ["'", '"', '"""', "'''"])
def test_delimiters(style: str):
    rewrite_run(python(f"a = f{style}foo{style}"))


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_multiline():
    rewrite_run(
        python("""
            a = f'''foo
            {None}
            bar'''
            """
       )
    )


def test_empty():
    rewrite_run(python("a = f''"))


def test_raw():
    rewrite_run(python("a = rf'raw'"))
    rewrite_run(python("a = Fr'raw'"))


def test_no_expr():
    # language=python
    rewrite_run(python("a = f'foo'"))


def test_only_expr():
    # language=python
    rewrite_run(python("a = f'{None}'"))


def test_expr_with_prefix():
    # language=python
    rewrite_run(python("a = f'{ None}'"))


def test_expr_with_suffix():
    # language=python
    rewrite_run(python("a = f'{None }'"))


def test_embedded_expr():
    # language=python
    rewrite_run(python("a = f'-{None}-'"))


def test_embedded_set():
    # language=python
    rewrite_run(python("a = f'-{ {1, 2} }-'"))


def test_escaped_braces():
    # language=python
    rewrite_run(python("a = f'{{foo{{bar}}baz}}'"))


def test_comment_in_expr():
    # language=python
    rewrite_run(
        python(
            """
            f"abc{a # This is a comment }
            + 3}"
            """
        )
    )


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_format_spec():
    # language=python
    rewrite_run(python("a = f'{1:n}'"))
