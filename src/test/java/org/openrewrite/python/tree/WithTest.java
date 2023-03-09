package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class WithTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings={
      "A() as a",
      "A()  as a",
      "A() as  a",
      "A() as a ",
      "A() as a, B() as b",
      "A()  as a, B() as b",
      "A() as  a, B() as b",
      "A() as a , B() as b",
      "A() as a,  B() as b",
      "A() as a, B()  as b",
      "A() as a, B() as  b",
      "A() as a, B() as b ",
    })
    public void test(String vars) {
        rewriteRun(python(
          """
            with %s:
                pass
            """.formatted(vars)
        ));
    }

}
