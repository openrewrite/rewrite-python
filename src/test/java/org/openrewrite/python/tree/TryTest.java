package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class TryTest implements RewriteTest {

    @ParameterizedTest
    @CsvSource(textBlock = """
      "" ,       ""
      " ",       ""
      "" ,       " "
      "" ,       " TypeError"
      "" ,       " TypeError "
      "" ,       " TypeError as e"
      "" ,       " TypeError  as e"
      "" ,       " TypeError as  e"
      "" ,       " TypeError as e "
      "" ,       "* TypeError"
      "" ,       " * TypeError"
      "" ,       "*  TypeError"
      "" ,       "* TypeError as e"
      "" ,       "*  TypeError as e"
      "" ,       "*TypeError"
      "" ,       " *TypeError"
    """, quoteCharacter = '"')
    public void testTryExcept(String afterTry, String afterExcept) {
        rewriteRun(python(
          """
            try%s:
                pass
            except%s:
                pass
            """.formatted(afterTry, afterExcept)
        ));
    }

    @ParameterizedTest
    @CsvSource(textBlock = """
      " TypeError"          , " OSError"
      " TypeError "          , " OSError"
      " TypeError"          , " OSError "
    """, quoteCharacter = '"')
    public void testTryMultiExcept(String afterFirstExcept, String afterSecondExcept) {
        rewriteRun(python(
          """
            try:
                pass
            except%s:
                pass
            except%s:
                pass
            """.formatted(afterFirstExcept, afterSecondExcept)
        ));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", " "})
    public void testTryFinally(String afterFinally) {
        rewriteRun(python(
          """
            try:
                pass
            finally%s:
                pass
            """.formatted(afterFinally)
        ));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", " "})
    public void testTryExceptFinally(String afterFinally) {
        rewriteRun(python(
          """
            try:
                pass
            except:
                pass
            finally%s:
                pass
            """.formatted(afterFinally)
        ));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", " "})
    public void testElse(String afterElse) {
        rewriteRun(python(
          """
            try:
                pass
            except:
                pass
            else%s:
                pass
            finally:
                pass
            """.formatted(afterElse)
        ));
    }

}

