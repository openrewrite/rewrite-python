from rewrite.test import rewrite_run, python


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_del():
    # language=python
    rewrite_run(python("del a"))
