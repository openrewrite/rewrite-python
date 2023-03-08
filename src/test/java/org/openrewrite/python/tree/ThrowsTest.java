package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ThrowsTest implements RewriteTest {

    @Test
    void raise() {
        rewriteRun(
          python("raise")
        );
    }

    @ParameterizedTest
    @ValueSource(strings = {
      "x", " x"
    })
    void raiseError(String expr) {
        rewriteRun(
          python(
            """
              raise %s
              """.formatted(expr)
          )
        );
    }

    @ParameterizedTest
    @ValueSource(strings = {
      "x from None",
      " x from None",
      "x  from None",
      "x from  None",
    })
    void raiseErrorFrom(String expr) {
        rewriteRun(
          python(
            """
              raise %s
              """.formatted(expr)
          )
        );
    }

}
