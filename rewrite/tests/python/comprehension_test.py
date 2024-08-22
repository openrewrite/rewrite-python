from rewrite.test import rewrite_run, python


def test_basic_list_comprehension():
    # language=python
    rewrite_run(python("a = [ e+1 for e in [1, 2, ]]"))


def test_list_comprehension_with_if():
    # language=python
    rewrite_run(python("a = [ e+1 for e in [1, 2, ] if e > 1]"))


def test_list_comprehension_with_multiple_ifs():
    # language=python
    rewrite_run(python("a = [ e+1 for e in [1, 2, ] if e > 1  if e < 10]"))


def test_basic_set_comprehension():
    # language=python
    rewrite_run(python("a = { e for e in range(10)}"))


def test_set_comprehension_with_if():
    # language=python
    rewrite_run(python("a = { e for e in range(10) if e > 1}"))


def test_set_comprehension_with_multiple_ifs():
    # language=python
    rewrite_run(python("a = { e for e in range(10) if e > 1 if e < 10}"))


def test_basic_dict_comprehension():
    # language=python
    rewrite_run(python("a = {n: n * 2 for n in range(10)}"))


def test_dict_comprehension_with_if():
    # language=python
    rewrite_run(python("a = {e:e for e in range(10) if e > 1}"))


def test_dict_comprehension_with_multiple_ifs():
    # language=python
    rewrite_run(python("a = {e:None for e in range(10) if e > 1 if e < 10}"))
