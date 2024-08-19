from argparse import ArgumentError

from rewrite.remote.test import foo
import pytest


@pytest.fixture(scope="session")
def rewrite_remote():
    remoting_context = foo.foo()
    yield remoting_context
    remoting_context.close()

