from rewrite.test import rewrite_run, python


def test_comment():
    # language=python
    rewrite_run(python("assert 1 # type: foo"))


def test_windows_line_endings():
    rewrite_run(python("assert 1 # type: foo\r\n"))
