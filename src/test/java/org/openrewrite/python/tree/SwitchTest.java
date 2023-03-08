package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class SwitchTest implements RewriteTest {

    @Test
    void simple() {
        rewriteRun(
          python(
            """
              match x:
                case 1:
                    pass
                case 2:
                    pass
              """
          )
        );
    }

    @Test
    void wildcard() {
        rewriteRun(
          python(
            """
              match x:
                case 1:
                    pass
                case 2:
                    pass
                case _:
                    pass
              """
          )
        );
    }

    @Test
    void sequence() {
        rewriteRun(
          python(
            """
              match x:
                case [1, 2]:
                    pass
              """
          )
        );
    }

    @Test
    void star() {
        rewriteRun(
          python(
            """
              match x:
                case [1, 2, *rest]:
                    pass
              """
          )
        );
    }

    @Test
    void guard() {
        rewriteRun(
          python(
            """
              match x:
                case [1, 2, *rest] if 42 in rest:
                    pass
              """
          )
        );
    }

    @Test
    void or() {
        rewriteRun(
          python(
            """
              match x:
                case 2 | 3:
                    pass
              """
          )
        );
    }

    @ParameterizedTest
    @ValueSource(strings = {
      "",
      "a",
      "b, c",
      "a, b=c"
    })
    void className(String args) {
        rewriteRun(
          python(
            """
              match x:
                case ClassName(%s):
                    pass
              """.formatted(args)
          )
        );
    }

    @Test
    void mapping() {
        rewriteRun(
          python(
            """
              match x:
                case {"x": x, "y": y, **z}:
                    pass
              """
          )
        );
    }

    @Test
    void value() {
        rewriteRun(
          python(
            """
              match x:
                case value.pattern:
                    pass
              """
          )
        );
    }

    @Test
    void nested() {
        rewriteRun(
          python(
            """
              match x:
                case [int(), str()]:
                    pass
              """
          )
        );
    }

    @Test
    void as() {
        rewriteRun(
          python(
            """
              match x:
                case [int(), str()] as y:
                    pass
              """
          )
        );
    }

    @Test
    void group() {
        rewriteRun(
          python(
            """
              match x:
                case (value.pattern):
                    pass
              """
          )
        );
    }
}
