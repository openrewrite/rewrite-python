package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class YieldTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
      "yield x",
      "yield  x",
      "yield x, y",
      "yield  x, y",
      "yield x , y",
      "yield x,  y",
      "yield from x",
      "yield  from x",
      "yield from  x",
    })
    public void yieldStatement(String arg) {
        rewriteRun(python(
          """
            def foo():
                %s
            """.formatted(arg)
        ));
    }

    @ParameterizedTest
    @ValueSource(strings = {
      "yield x",
      "yield  x",
      "yield x, y",
      "yield  x, y",
      "yield x , y",
      "yield x,  y",
      "yield from x",
      "yield  from x",
      "yield from  x",
    })
    public void yieldExpression(String arg) {
        rewriteRun(python(
          """
            def foo():
                it = (%s)
            """.formatted(arg)
        ));
    }

}
