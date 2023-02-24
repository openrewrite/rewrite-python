package org.openrewrite.python.tree;

import org.intellij.lang.annotations.Language;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ArrayAccessTest implements RewriteTest {

    @ParameterizedTest
    //language=py
    @ValueSource(strings = {"x[0]", "x [0]", "x[ 0]", "x[0 ]"})
    void arrayAccess(@Language("py") String access) {
        rewriteRun(python(access));
    }
}
