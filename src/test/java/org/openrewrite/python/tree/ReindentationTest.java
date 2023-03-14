/*
 * Copyright 2023 the original author or authors.
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
import org.openrewrite.ExecutionContext;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.java.tree.J;
import org.openrewrite.java.tree.Statement;
import org.openrewrite.python.PythonVisitor;
import org.openrewrite.test.RecipeSpec;
import org.openrewrite.test.RewriteTest;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.openrewrite.python.Assertions.python;
import static org.openrewrite.test.RewriteTest.toRecipe;

class ReindentationTest implements RewriteTest {

    @Override
    public void defaults(RecipeSpec spec) {
        spec.recipe(toRecipe(() -> new PythonVisitor<>() {
            @Override
            public J visitBlock(J.Block block, ExecutionContext executionContext) {
                List<Statement> copied = new ArrayList<>();
                Set<String> existing = new HashSet<>();
                for (Statement statement : block.getStatements()) {
                    if (statement instanceof J.MethodDeclaration) {
                        existing.add(((J.MethodDeclaration) statement).getSimpleName());
                    }
                }
                for (Statement statement : block.getStatements()) {
                    if (statement instanceof J.ClassDeclaration) {
                        J.Block body = ((J.ClassDeclaration) statement).getBody();
                        for (Statement classStatement : body.getStatements()) {
                            if (classStatement instanceof J.MethodDeclaration) {
                                if (existing.add(((J.MethodDeclaration) classStatement).getSimpleName())) {
                                    copied.add(classStatement);
                                }
                            }
                        }
                    }
                }
                return block.withStatements(ListUtils.concatAll(
                  block.getStatements(),
                  copied
                ));
            }
        }));
    }

    @Test
    void example1() {
        rewriteRun(python(
          """                
            class A:           
                @decorator
                @anotherdec
                def f():
            # misaligned comment
             # misaligned comment
                    # a loop
                    while True:
                        pass
                
                def g():
                    pass
            """,
          """
            class A:           
                @decorator
                @anotherdec
                def f():
            # misaligned comment
             # misaligned comment
                    # a loop
                    while True:
                        pass
                
                def g():
                    pass
            @decorator
            @anotherdec
            def f():
            # misaligned comment
             # misaligned comment
                # a loop
                while True:
                    pass
            
            def g():
                pass
            """
        ));
    }

    @Test
    void example2() {
        rewriteRun(python(
          """
            class A:
            
                class B:
                    @dec
                    def f():
                        pass
                    
                    @dec
                    @anotherdec
                    def g():
                        pass
                        
                    @dec # trailing
                    @anotherdec
                    def h():
                        pass
                        
                    @dec # trailing
                    # multiline
                    @anotherdec
                    def i():
                        pass
                        
                    @dec # trailing
                         # multiline jagged
                    @anotherdec
                    def i():
                        pass
                        
                    @dec
                    @anotherdec
                    # comment between
                    def k():
                        pass
                        
                    # comment
                    def l():
                        pass
                        
                    # multiline
                    # comment
                    def m():
                        pass
                        
                   # very
                    # jagged
                     # comment
                    def n():
                        pass
            """
        ));
    }

}
