package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ClassDeclarationTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
      "Foo:",
      "Foo :",
      "Foo(Bar):",
      "Foo (Bar):",
      "Foo(Bar) :",
      "Foo( Bar):",
      "Foo(Bar ):",
      "Foo():",
      "Foo( ):",
      "Foo ():",
      "Foo (Bar1, Bar2):",
    })
    void classDeclaration(String decl) {
        rewriteRun(
          python(
            """
              class %s
                  pass
              """.formatted(decl)
          )
        );
    }
}
