package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class IfTest implements RewriteTest {

    @Test
    void ifStmt() {
        rewriteRun(
          python(
            """
              if True:
                  pass
              """
          )
        );
    }

    @Test
    void ifElseStmt() {
        rewriteRun(
          python(
            """
              if True:
                  pass
              else:
                  pass
              """
          )
        );
    }

    @Test
    void ifElifElseStmt() {
        rewriteRun(
          python(
            """
              if True:
                  pass
              elif False:
                  pass
              else:
                  pass
              """
          )
        );
    }

    @Test
    void multiElifElseStmt() {
        rewriteRun(
          python(
            """
              if True:
                  pass
              elif False:
                  pass
              elif True:
                  pass
              else:
                  pass
              """
          )
        );
    }

    @Test
    void multiElifStmt() {
        rewriteRun(
          python(
            """
              if True:
                  pass
              elif False:
                  pass
              elif True:
                  pass
              """
          )
        );
    }
}
