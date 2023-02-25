package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ParenthesesTest implements RewriteTest {

    @ParameterizedTest
    //language=py
    @ValueSource(strings = {"(42)", "( 42 )"})
    void parentheses(String expr) {
        rewriteRun(
          python("n = %s".formatted(expr))
        );
    }
}
