package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ListComprehensionTest implements RewriteTest {

    @Test
    void listComprehension() {
        rewriteRun(
          python("[x for x in xs if x]")
        );
    }
}
