package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class AwaitTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
      "await x",
      "await  x"
    })
    public void await(String arg) {
        rewriteRun(python(arg));
    }

}
