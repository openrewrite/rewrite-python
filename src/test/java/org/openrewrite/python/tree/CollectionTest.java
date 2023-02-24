package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class CollectionTest implements RewriteTest {

    @Test
    void listExpression() {
        rewriteRun(
          python("xs = [1, 2, 3]")
        );
    }

    @Test
    void listExpressionEmpty() {
        rewriteRun(
          python("xs = []")
        );
    }
    
    @Test
    void tupleExpression() {
        rewriteRun(
          python("xs = (1, 2, 3)")
        );
    }

    @Test
    void tupleExpressionEmpty() {
        rewriteRun(
          python("xs = ()")
        );
    }

    @Test
    void tupleExpressionSingle() {
        // ()     => tuple
        // (1)    => int
        // (1,)   => tuple      <-- test this case
        // (1, 2) => tuple
        rewriteRun(
          python("xs = (1,)")
        );
    }

    @Test
    void setExpression() {
        rewriteRun(
          python("xs = {1, 2, 3}")
        );
    }

    @Test
    void dictExpression() {
        rewriteRun(
          python("xs = {\"foo\": \"bar\", \"foo2\": \"bar2\"}")
        );
    }

    @Test
    void dictExpressionEmpty() {
        rewriteRun(
          python("xs = {}")
        );
    }
}
