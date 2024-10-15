/*
 * Copyright 2021 the original author or authors.
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * https://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

class TryTest implements RewriteTest {

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
    void tryExcept(String afterTry, String afterExcept) {
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
    void tryMultiExcept(String afterFirstExcept, String afterSecondExcept) {
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
    void tryFinally(String afterFinally) {
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
    void tryExceptFinally(String afterFinally) {
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
    void testElse(String afterElse) {
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
