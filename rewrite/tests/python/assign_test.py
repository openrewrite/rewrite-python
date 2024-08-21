from rewrite.test import rewrite_run, python


#language=python
def test_assign():
    rewrite_run(python("a = 1"))