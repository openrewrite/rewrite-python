from rewrite.test import rewrite_run, python


def test_list():
    # language=python
    rewrite_run(python("l = [*[1], 2]"))

def test_dict():
    # language=python
    rewrite_run(python("d = {**{'x':1}, 'y':2}"))
