from rewrite.test import rewrite_run, python

#language=python
def test_list():
    rewrite_run(python("a = [1, 2, 3]"))