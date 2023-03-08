package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class LambdaTest implements RewriteTest {

    @Test
    void group() {
        rewriteRun(
          python(
            """
              x = lambda a : a + 10
              """
          )
        );
    }

}
