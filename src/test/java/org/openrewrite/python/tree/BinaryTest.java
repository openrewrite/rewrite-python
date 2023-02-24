package org.openrewrite.python.tree;

import org.intellij.lang.annotations.Language;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class BinaryTest implements RewriteTest {

    @ParameterizedTest
    //language=py
    @ValueSource(strings = {
      "1+2",
      "1+ 2",
      "1 +2",
    })
    void binaryOperatorSpacing(@Language("py") String expr) {
        rewriteRun(python(expr));
    }

    @ParameterizedTest
    @ValueSource(strings = {"-", "+", "*", "/"})
    void arithmeticOperator(String op) {
        rewriteRun(python("1 %s 2".formatted(op)));
    }

    @ParameterizedTest
    @ValueSource(strings = {"==", "!=", "<", ">", "<=", ">="})
    void comparisonOperator(String op) {
        rewriteRun(python("1 %s 2".formatted(op)));
    }

    @ParameterizedTest
    @ValueSource(strings = {"or", "and", "is", "is not", "in", "not in"})
    void booleanOperator(String op) {
        rewriteRun(python("x %s y".formatted(op)));
    }
}
