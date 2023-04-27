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

import static org.openrewrite.python.tree.ParserAssertions.python;
class ClassDeclarationTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
      "Foo:",
      "Foo :",
      "Foo(Bar):",
      "Foo (Bar):",
      "Foo(Bar) :",
      "Foo( Bar):",
      "Foo(Bar ):",
      "Foo():",
      "Foo( ):",
      "Foo ():",
      "Foo (Bar1, Bar2):",
    })
    void classDeclaration(String decl) {
        rewriteRun(
          python(
            """
              class %s
                  pass
              """.formatted(decl)
          )
        );
    }

    @Test
    void testSpaceBetweenClasses() {
        rewriteRun(
          python(
            """
              class Foo:
                pass
              
              
              class Bar:
                pass
              """
          )
        );
    }

    @Test
    void testNestedClasses() {
        rewriteRun(
          python(
            """
              class A:
              
                class B:
                  pass
              """
          )
        );
    }
}
