from rewrite.test import rewrite_run, python


# noinspection PyUnresolvedReferences
def test_attribute():
    # language=python
    rewrite_run(python("a = foo.bar"))


# noinspection PyUnresolvedReferences
def test_nested_attribute():
    # language=python
    rewrite_run(python("a = foo.bar.baz"))
