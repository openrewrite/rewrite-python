import pytest

from rewrite.test import rewrite_run, python


# noinspection PyUnresolvedReferences
def test_simple():
    # language=python
    rewrite_run(python("import io"))


# noinspection PyUnresolvedReferences
def test_simple_with_alias():
    # language=python
    rewrite_run(python("import io as io"))


# noinspection PyUnresolvedReferences
@pytest.mark.xfail(reason="The parser performs Unicode normalization which can't be disabled", strict=True)
def test_unicode_char_normalization():
    # language=python
    rewrite_run(python("from .main import MaµToMan"))


# noinspection PyUnresolvedReferences
def test_qualified():
    # language=python
    rewrite_run(python("import xml.dom"))


# noinspection PyUnresolvedReferences
def test_multiple():
    # language=python
    rewrite_run(python("import xml.dom ,  io "))


# noinspection PyUnresolvedReferences
def test_from():
    # language=python
    rewrite_run(python("from io import StringIO as sio"))


# noinspection PyUnresolvedReferences
def test_from_parenthesized():
    # language=python
    rewrite_run(python("from io import (StringIO as sio)"))


# noinspection PyUnresolvedReferences
def test_from_parenthesized_trailing_comma():
    # language=python
    rewrite_run(python("from io import (StringIO as sio , )"))


# noinspection PyUnresolvedReferences
def test_relative_import_0():
    # language=python
    rewrite_run(python("from . import bar"))


# noinspection PyUnresolvedReferences
def test_relative_import_1():
    # language=python
    rewrite_run(python("from .foo import bar"))


# noinspection PyUnresolvedReferences
def test_relative_import_2():
    # language=python
    rewrite_run(python("from ..foo import bar"))


# noinspection PyUnresolvedReferences
def test_crlf():
    # language=python
    rewrite_run(python(
        """\
        import foo
        import bar
        """.replace('\n', '\r\n')
    ))
