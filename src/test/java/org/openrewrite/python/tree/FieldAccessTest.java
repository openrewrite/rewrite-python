package org.openrewrite.python.tree;

import org.intellij.lang.annotations.Language;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class FieldAccessTest implements RewriteTest {

    @ParameterizedTest
    //language=py
    @ValueSource(strings = {
      "a.b", "a. b", "a .b",
      "a.b.c", "a. b.c", "a .b.c"
    })
    void simpleFieldAccess(@Language("py") String arg) {
        rewriteRun(python(arg));
    }

}
