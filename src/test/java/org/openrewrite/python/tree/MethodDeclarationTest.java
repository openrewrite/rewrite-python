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
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class MethodDeclarationTest implements RewriteTest {

    @Test
    void functionDefinition() {
        rewriteRun(
          python(
            """
              def foo():
                  pass
              """
          )
        );
    }

    @Test
    void methodDefinition() {
        rewriteRun(
          python(
            """
              class Foo:
                  def foo():
                      pass
              """
          )
        );
    }

    @Test
    void methodDefinitionWithDocstring() {
        rewriteRun(
          python(
            """
              class Foo:
                  def foo():
                      \"""sa docstring comment\"""
                      pass
              """
          )
        );
    }


    @Test
    void decorator() {
        rewriteRun(
          python(
            """
              @something
              def foo():
                  pass
              """
          )
        );
    }

    @Test
    void decoratorWithParams() {
        rewriteRun(
          python(
            """
              @something(1, 2, 3)
              def foo():
                  pass
              """
          )
        );
    }
}
