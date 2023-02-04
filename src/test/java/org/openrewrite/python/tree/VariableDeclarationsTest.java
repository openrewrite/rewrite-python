package org.openrewrite.python.tree;

import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class VariableDeclarationsTest implements RewriteTest {

    void variableDecl() {
        rewriteRun(
          python("n = 1")
        );
    }
}
