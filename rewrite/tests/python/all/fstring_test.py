import pytest

from rewrite.test import rewrite_run, python


@pytest.mark.parametrize('style', ["'", '"', '"""', "'''"])
class TestFString:
    def test_empty(self, style: str):
        rewrite_run(python(f"a = f{style}{style}"))


    def test_no_expr(self, style: str):
        # language=python
        rewrite_run(python("a = f'foo'"))


    def test_only_expr(self, style: str):
        # language=python
        rewrite_run(python("a = f'{None}'"))


    def test_expr_with_prefix(self, style: str):
        # language=python
        rewrite_run(python("a = f'{ None}'"))


    def test_expr_with_suffix(self, style: str):
        # language=python
        rewrite_run(python("a = f'{None }'"))


    def test_embedded_expr(self, style: str):
        # language=python
        rewrite_run(python("a = f'-{None}-'"))


    def test_embedded_set(self, style: str):
        # language=python
        rewrite_run(python("a = f'-{ {1, 2} }-'"))


    def test_escaped_braces(self, style: str):
        # language=python
        rewrite_run(python("a = f'{{foo{{bar}}baz}}'"))
