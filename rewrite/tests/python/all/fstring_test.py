import pytest

from rewrite.test import rewrite_run, python


@pytest.mark.parametrize('style', ["'", '"', '"""', "'''"])
def test_delimiters(style: str):
    rewrite_run(python(f"a = f{style}foo{style}"))


def test_multiline():
    # language=python
    rewrite_run(
        python("""
            a = f'''foo
            {None}
            bar'''
            """
               )
    )


def test_empty():
    # language=python
    rewrite_run(python("a = f''"))


def test_raw():
    # language=python
    rewrite_run(python("a = rf'raw'"))
    # language=python
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


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_debug():
    # language=python
    rewrite_run(python("a = f'{None=}'"))


def test_conversion():
    # language=python
    rewrite_run(python("""a = f'{"foo"!a}'"""))
    rewrite_run(python("""a = f'{"foo"!s}'"""))
    rewrite_run(python("""a = f'{"foo"!r}'"""))


def test_conversion_and_format():
    # language=python
    rewrite_run(python("""a = f'{"foo"!a:n}'"""))


def test_conversion_and_format_expr():
    # language=python
    rewrite_run(python("""a = f'{"foo"!s:<{5*2}}'"""))


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_nested_fstring_conversion_and_format_expr():
    # language=python
    rewrite_run(python("""a = f'{f"foo"!s:<{5*2}}'"""))


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


def test_simple_format_spec():
    # language=python
    rewrite_run(python("a = f'{1:n}'"))


def test_format_spec_with_precision_and_conversion():
    # language=python
    rewrite_run(python("a = f'{1:.2f}'"))


def test_nested_fstring_expression():
    # language=python
    rewrite_run(python("""a = f'{f"{1}"}'"""))


def test_nested_fstring_format():
    # language=python
    rewrite_run(python("""a = f'{f"{1}"}'"""))


def test_format_value():
    # language=python
    # rewrite_run(python("a = f'{1:.{2 + 3}f}'"))
    # language=python
    # rewrite_run(python('''a = f"{'abc':>{2*3}}"'''))
    # language=python
    rewrite_run(python("""a = f'{f"{'foo'}":>{2*3}}'"""))


def test_nested_fstring_with_format_value():
    # language=python
    rewrite_run(python("""a = f'{f"{'foo'}":>{2*3}}'"""))
