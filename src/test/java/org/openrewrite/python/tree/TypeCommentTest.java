package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class TypeCommentTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
        "->str",
        "-> str",
        " -> str",
        "->  str",
        "-> str ",
    })
    void functionReturnType(String type) {
        rewriteRun(
          python(
            """
              def x()%s:
                 pass
              """.formatted(type)
          )
        );
    }

    @ParameterizedTest
    @ValueSource(strings = {
      ":str",
      " :str",
      ": str",
      ":str ",
    })
    void functionParamType(String type) {
        rewriteRun(
          python(
            """
              def x(a%s):
                 pass
              """.formatted(type)
          )
        );
    }

    @ParameterizedTest
    @ValueSource(strings = {
      ":str",
      " :str",
      ": str",
      ":str ",
    })
    void functionArgsParamType(String type) {
        rewriteRun(
          python(
            """
              def x(*a%s):
                 pass
              """.formatted(type)
          )
        );
    }

    @Test
    void variables() {
        rewriteRun(
          python(
            """
              a: None = None
              a = None
              a: str = "hello"
              """
          )
        );
    }


}
