from rewrite.test import rewrite_run, python


def test_simple():
    # language=python
    rewrite_run(python("import io"))


def test_simple_with_alias():
    # language=python
    rewrite_run(python("import io as io"))


def test_qualified():
    # language=python
    rewrite_run(python("import xml.dom"))


def test_multiple():
    # language=python
    rewrite_run(python("import xml.dom ,  io "))


def test_from():
    # language=python
    rewrite_run(python("from io import StringIO as sio"))


def test_from_parenthesized():
    # language=python
    rewrite_run(python("from io import (StringIO as sio)"))


def test_from_parenthesized_trailing_comma():
    # language=python
    rewrite_run(python("from io import (StringIO as sio , )"))
