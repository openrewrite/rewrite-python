package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ReturnTest implements RewriteTest {

    @Test
    void methodReturn() {
        rewriteRun(
          python(
            """
              def foo():
                  return 1
              """
          )
        );
    }
}
