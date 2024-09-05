from rewrite.test import rewrite_run, python


def test_empty():
    # language=python
    rewrite_run(python("a = []"))


def test_trailing_comma():
    # language=python
    rewrite_run(python("a = [1, 2,  ]"))


def test_array_subscript():
    # language=python
    rewrite_run(python("a = [1, 2][0]"))


def test_array_slice():
    # language=python
    rewrite_run(python("a = [1, 2][0:1]"))


def test_array_slice_no_upper():
    # language=python
    rewrite_run(python("a = [1, 2][0:]"))


def test_array_slice_no_lower():
    # language=python
    rewrite_run(python("a = [1, 2][:1]"))


def test_array_slice_no_lower_no_upper():
    # language=python
    rewrite_run(python("a = [1, 2][::1]"))


def test_array_slice_full():
    # language=python
    rewrite_run(python("a = [1, 2][0:1:1]"))


def test_array_slice_tuple_index_1():
    # language=python
    rewrite_run(python("a = [1, 2][0,1]"))


def test_array_slice_tuple_index_2():
    # language=python
    rewrite_run(python("a = [1, 2][(0,1)]"))
