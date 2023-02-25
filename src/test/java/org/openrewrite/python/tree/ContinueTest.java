package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ContinueTest implements RewriteTest {

    @Test
    void forLoopContinue() {
        rewriteRun(
          python(
            """
              for x in xs:
                  continue
              """
          )
        );
    }
}
