package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class DictLiteralTest implements RewriteTest {

    @Test
    void dictLiteral() {
        rewriteRun(
          python(
            """
              class Test:
                  d = { 'a': 1, 'b': 2 }
              """
          )
        );
    }
}
