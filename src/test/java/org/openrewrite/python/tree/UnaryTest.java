package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class UnaryTest implements RewriteTest {

    @Test
    void not() {
        rewriteRun(
          python("not y")
        );
    }
}
