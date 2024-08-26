from rewrite.test import rewrite_run, python


def test_empty():
    # language=python
    rewrite_run(python("a = f''"))


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
