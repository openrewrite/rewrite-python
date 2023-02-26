package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class AssignTest implements RewriteTest {

    @Test
    void assignment() {
        rewriteRun(
          python(
            """
              j = 1
              k = 2
              """
          )
        );
    }
}
