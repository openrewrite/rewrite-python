/*
 * Copyright 2024 the original author or authors.
 * <p>
 * Licensed under the Moderne Source Available License (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * https://docs.moderne.io/licensing/moderne-source-available-license
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

class SliceTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
      ":", "::", " :", ": ", " : ",
      "1:2", "1:2:3",
      "1 :2", "1: 2", "1 : 2",
      "1:2:3",
      "None:None", "None:None:None",
      " None : None ", " None : None : None ",
    })
    void sliceOperator(String arg) {
        rewriteRun(
          python("x[%s]".formatted(arg))
        );
    }
}
