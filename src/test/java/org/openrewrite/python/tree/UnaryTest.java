package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class UnaryTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {"not ", "+", "-"})
    void unary(String op) {
        rewriteRun(
          python("%sy".formatted(op))
        );
    }
}
