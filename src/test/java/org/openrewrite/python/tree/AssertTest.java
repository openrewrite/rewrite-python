package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class AssertTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
      "assert x",
      "assert  x",
      "assert x, y",
      "assert  x, y",
      "assert x , y",
      "assert x,  y",
    })
    public void assert_(String arg) {
        rewriteRun(python(arg));
    }

}
