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

public class StubTest implements RewriteTest {

    @Test
    void simpleStub() {
        rewriteRun(
          python("""
            # Variables with annotations do not need to be assigned a value.
            # So by convention, we omit them in the stub file.
            x: int
            
            # Function bodies cannot be completely removed. By convention,
            # we replace them with `...` instead of the `pass` statement.
            def func_1(code: str) -> int: ...
            
            # We can do the same with default arguments.
            def func_2(a: int, b: int = ...) -> int: ...
            """,
            spec -> spec.path("file.pyi")
          )
        );
    }
}
