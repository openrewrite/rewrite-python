package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class AnnotationTest implements RewriteTest {

    @Test
    public void decoratorOnFunction() {
        rewriteRun(python(
          """
            @dec
            def f():
                pass
            """
        ));
    }

    @Test
    public void decoratorOnClass() {
        rewriteRun(python(
          """
            @dec
            class C:
                pass
            """
        ));
    }

    @Test
    public void staticMethodDecoratorOnFunction() {
        rewriteRun(python(
          """
            class C:
                @staticmethod
                def f():
                    pass
            """
        ));
    }

    @ParameterizedTest
    @ValueSource(
      strings = {
        "", "()", "( )",
        "(42)", "(42 )", "( 42 )",
        "(1, 2)", "(1,2)", "(1, 2 )", "( 1, 2 )", "( 1, 2)"
      }
    )
    public void decoratorArguments(String args) {
        rewriteRun(python(
          """
            @dec%s
            def f():
                pass
            """.formatted(args)
        ));
    }

    @ParameterizedTest
    @ValueSource(
      strings = {
        "class C", "def m()"
      }
    )
    public void multipleDecorators(String args) {
        rewriteRun(python(
          """
            @decA
            @decB()
            @decC()
            %s:
                pass
            """.formatted(args)
        ));
    }

}
