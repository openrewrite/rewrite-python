import pytest

from rewrite.python.format.remove_trailing_whitespace_visitor import RemoveTrailingWhitespaceVisitor
from rewrite.test import rewrite_run, RecipeSpec, from_visitor, python


class Foo:
    pass


@pytest.mark.parametrize('n_spaces', list(range(0, 4)))
@pytest.mark.parametrize('linebreaks', ['\n', '\r\n', '\r\n\n', '\n\n'])
def test_tabs_to_spaces(n_spaces, linebreaks):
    # noinspection PyInconsistentIndentation
    spaces = ' ' * n_spaces
    rewrite_run(
        python(
            # language=python
            f"""\
            class Foo:{spaces}{linebreaks}\
                def bar(self):
                    return 42{linebreaks}
            {spaces}{linebreaks}
            """,
            # language=python
            f"""\
            class Foo:{linebreaks}\
                def bar(self):
                    return 42{linebreaks}
            {linebreaks}
            """
        ),
        spec=RecipeSpec()
        .with_recipes(
            from_visitor(RemoveTrailingWhitespaceVisitor())
        )
    )
