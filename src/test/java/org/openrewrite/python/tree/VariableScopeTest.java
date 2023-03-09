package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class VariableScopeTest implements RewriteTest {
    @ParameterizedTest
    @ValueSource(strings = {"nonlocal", "global"})
    public void singleName(String kind) {
        rewriteRun(
          python(
            """
              def foo():
                  %s x
              """.formatted(kind)
          )
        );
    }

    @ParameterizedTest
    @ValueSource(strings = {"nonlocal", "global"})
    public void multipleNames(String kind) {
        rewriteRun(
          python(
            """
              def foo():
                  %s x, y, z
              """.formatted(kind)
          )
        );
    }
}
