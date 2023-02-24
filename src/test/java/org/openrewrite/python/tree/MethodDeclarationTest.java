package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class MethodDeclarationTest implements RewriteTest {

    @Test
    void functionDefinition() {
        rewriteRun(
          python(
            """
              def foo():
                  pass
              """
          )
        );
    }

    @Test
    void methodDefinition() {
        rewriteRun(
          python(
            """
              class Foo:
                  def foo():
                      pass
              """
          )
        );
    }

    @Test
    void decorator() {
        rewriteRun(
          python(
            """
              @something
              def foo():
                  pass
              """
          )
        );
    }

    @Test
    void decoratorWithParams() {
        rewriteRun(
          python(
            """
              @something(1, 2, 3)
              def foo():
                  pass
              """
          )
        );
    }
}
