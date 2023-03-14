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
