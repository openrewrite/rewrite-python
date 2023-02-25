package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class WhileTest implements RewriteTest {

    @Test
    void whileLoop() {
        rewriteRun(
          python(
            """
              while x:
                  pass
              """
          )
        );
    }
}
