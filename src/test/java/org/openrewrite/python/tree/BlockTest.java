package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class BlockTest implements RewriteTest {

    @Test
    public void singleStatement() {
        rewriteRun(python(
          """
            def f():
                pass
            """
        ));
    }

    @Test
    public void singleStatementWithDocstring() {
        rewriteRun(python(
          """
            def f():
                \"""a docstring\"""
                pass
            """
        ));
    }

    @Test
    public void singleStatementWithTrailingComment() {
        rewriteRun(python(
          """
            def f():
                pass  # a comment about the line
            """
        ));
    }

    @Test
    public void multiStatementWithBlankLines() {
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
    public void multiStatementWithTrailingComments() {
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
    public void multiStatementWithBetweenComments() {
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
