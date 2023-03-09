package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

class BlockTest implements RewriteTest {

    @Test
    void singleStatement() {
        rewriteRun(python(
          """
            def f():
                pass
            """
        ));
    }

    @Test
    void singleStatementWithDocstring() {
        rewriteRun(python(
          """
            def f():
                \"""a docstring\"""
                pass
            """
        ));
    }

    @Test
    void singleStatementWithTrailingComment() {
        rewriteRun(python(
          """
            def f():
                pass  # a comment about the line
            """
        ));
    }

    @Test
    void multiStatementWithBlankLines() {
        rewriteRun(python(
          """
            def f():
                pass
                
                pass
                
                pass
            """
        ));
    }

    @Test
    void multiStatementWithTrailingComments() {
        rewriteRun(python(
          """
            def f():
                pass  # a comment about the line
                pass  # a comment about the line
                pass  # a comment about the line
            """
        ));
    }

    @Test
    void multiStatementWithBetweenComments() {
        rewriteRun(python(
          """
            def f():
                pass
                # a comment on its own line
                # another comment on its own line
                pass
                # a comment on its own line
                # another comment on its own line
                pass
            """
        ));
    }


}
