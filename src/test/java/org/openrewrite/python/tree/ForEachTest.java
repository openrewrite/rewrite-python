package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ForEachTest implements RewriteTest {

    @Test
    void forLoop() {
        rewriteRun(
          python(
            """
              for x in xs:
                  pass
              """
          )
        );
    }

    @Test
    void forLoopDestructuring() {
        rewriteRun(
          python(
            """
              for x, y in xs:
                  pass
              """
          )
        );
    }
}
