package org.openrewrite.python.tree;

import org.intellij.lang.annotations.Language;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class MethodInvocationTest implements RewriteTest {

    @ParameterizedTest
    //language=py
    @ValueSource(strings = {
      "print(42)", "print( 42 )", "print(1, 2, 3, 4)",
      "print( 1, 2, 3, 4 )", "print(1 , 2 , 3 , 4)",
      "print(1, 2, 3, 4, sep='+')"
    })
    void print(@Language("py") String print) {
        rewriteRun(python(print));
    }

    @Test
    void qualifiedTarget() {
        /*
            This appears as a `qualifier` on `PyReferenceExpression`.
            This should be straightforward to implement but isn't done.
         */
        rewriteRun(python("int.bit_length(42)"));
    }

    @Test
    void methodInvocationOnExpressionTarget() {
        rewriteRun(python("list().copy()"));
    }
}
