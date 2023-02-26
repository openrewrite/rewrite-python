package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class NewArrayTest implements RewriteTest {

    @Test
    void list() {
        rewriteRun(
          python(
            """
              n = [1, 2, 3]
              """
          )
        );
    }
}
