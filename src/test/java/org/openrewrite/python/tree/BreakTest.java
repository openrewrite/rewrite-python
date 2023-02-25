package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class BreakTest implements RewriteTest {

    @Test
    void forLoopBreak() {
        rewriteRun(
          python(
            """
              for x in xs:
                  break
              """
          )
        );
    }
}
