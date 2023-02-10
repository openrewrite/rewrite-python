package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class VariableDeclarationsTest implements RewriteTest {

    @Test
    void variableDeclNoSpace() {
        rewriteRun(
          python("n=1")
        );
    }

    @Test
    void variableDecl() {
        rewriteRun(
          python("n = 1")
        );
    }
}
