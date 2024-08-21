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
import org.openrewrite.Issue;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

class VariableScopeTest implements RewriteTest {
    @ParameterizedTest
    @ValueSource(strings = {"nonlocal", "global"})
    void singleName(String kind) {
        rewriteRun(
          python(
            """
              def foo():
                  %s x
              """.formatted(kind)
          )
        );
    }

    @ParameterizedTest
    @ValueSource(strings = {"nonlocal", "global"})
    void multipleNames(String kind) {
        rewriteRun(
          python(
            """
              def foo():
                  %s x, y, z
              """.formatted(kind)
          )
        );
    }

    @Issue("https://github.com/openrewrite/rewrite-python/issues/36")
    @Test
    void assignment() {
        rewriteRun(
          python(
            """
            import pygenie
            
            pygenie.conf.DEFAULT_GENIE_URL = "http://genie:8080"
            """)
        );
    }
}
