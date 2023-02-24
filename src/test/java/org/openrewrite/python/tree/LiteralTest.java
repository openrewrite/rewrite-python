package org.openrewrite.python.tree;

import org.intellij.lang.annotations.Language;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class LiteralTest implements RewriteTest {

    @ParameterizedTest
    //language=py
    @ValueSource(strings = {
      "True", "False", "42.2", "42", "\"hello world\"",
      "\"hello \\\"world\\\"\"", "'hello world'",
      "'hello \\'world\\''"
    })
    void literals(@Language("py") String lit) {
        rewriteRun(python(lit));
    }
}
