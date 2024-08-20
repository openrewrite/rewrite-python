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
import org.junitpioneer.jupiter.ExpectedToFail;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.tree.ParserAssertions.python;

class NewArrayTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
      "[]",
      "[ ]",
      "[1,2,3]",
      "[1, 2, 3]",
      "[ 1, 2, 3 ]",
      "[ 1 , 2 , 3 ]",
      "[1, *xs]",
      "[1, *xs ]",
    })
    void list(String arg) {
        rewriteRun(
          python(
            """
              n = %s
              """.formatted(arg)
          )
        );
    }

    @ParameterizedTest
    @ValueSource(strings = {
      "{}",
      "{ }",
      "{1,2,3}",
      "{1, 2, 3}",
      "{ 1, 2, 3 }",
      "{ 1 , 2 , 3 }",
      "{1, *xs}",
      "{1, * xs}",
      "{1, *xs }",
    })
    void set(String arg) {
        rewriteRun(
          python(
            """
              n = %s
              """.formatted(arg)
          )
        );
    }

    @ExpectedToFail("Requires revisions to mapExpressionsAsRightPadded")
    @Test
    void trailingComma() {
        rewriteRun(
          python(
            """
              value = [
                "v1" ,
                "v2" ,
              ]
              """
          )
        );
    }

    @ExpectedToFail("Requires revisions to mapExpressionsAsRightPadded")
    @Test
    void trailingComments() {
        rewriteRun(
          python(
            """
              value = [
                "v1" , # comment 1
                "v2" , # comment 2
              ]
              """
          )
        );
    }
}
