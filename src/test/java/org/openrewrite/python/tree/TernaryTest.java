package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class TernaryTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
        "x = 3 if True else 1",
        "x = 3  if True else 1",
        "x = 3 if  True else 1",
        "x = 3 if True  else 1",
        "x = 3 if True else  1",
    })
    public void test(String expr) {
        rewriteRun(python(expr));
    }

}
