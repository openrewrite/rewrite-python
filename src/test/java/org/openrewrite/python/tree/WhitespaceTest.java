package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.ExecutionContext;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.java.tree.J;
import org.openrewrite.java.tree.Statement;
import org.openrewrite.python.PythonVisitor;
import org.openrewrite.test.RewriteTest;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.openrewrite.python.Assertions.python;
import static org.openrewrite.test.RewriteTest.toRecipe;

class WhitespaceTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
      "",
      " ",
      ";",
      " ;",
      "; ",
      "\n",
      " \n",
      "\n ",
      "# comment",
      " # comment",
      "# comment ",
    })
    void testSingleStatement(String ending) {
        rewriteRun(python("print(42)%s".formatted(ending)));
    }

    @ParameterizedTest
    @ValueSource(strings = {
      ";",
      " ;",
      "; ",
      "\n",
      " \n",
      "# comment\n",
      " # comment\n",
      "# comment \n",
    })
    void testMultiStatement(String ending) {
        rewriteRun(python("print(42)%sprint(2)".formatted(ending)));
    }

    @ParameterizedTest
    @ValueSource(strings = {
      "",
      " ",
      ";",
      " ;",
      "; ",
      "\n",
      " \n",
      "\n ",
      "# comment",
      " # comment",
      "# comment ",
      "\n#comment\n",
      "\n  #comment\n",
    })
    void testSingleLineMultiStatement(String firstLineEnding) {
        rewriteRun(python(
          """
            print(42); print(43) ;print(44)%s
            print(42); print(43) ;print(44) ; 
            """.formatted(firstLineEnding)
        ));
    }


    @ParameterizedTest
    @ValueSource(strings = {
      "",
      " ",
      ";",
      " ;",
      "; ",
      "\n",
      " \n",
      "\n ",
      "# comment",
      " # comment",
      "# comment ",
      "\n#comment\n",
      "\n  #comment\n",
    })
    void testSingleLineMultiStatementInsideBlock(String firstLineEnding) {
        rewriteRun(python(
          """
            def foo():
                print(42); print(43) ;print(44)%s
                print(42); print(43) ;print(44) ; 
            """.formatted(firstLineEnding)
        ));
    }

    @ParameterizedTest
    @ValueSource(strings = {
      "", "\n", "\n\n", "\n\n\n"
    })
    void testEOF(String eofSpace) {
        rewriteRun(python(
          """
            print(1)
            print(2)
            print(3)%s""".formatted(eofSpace)
        ));
    }

    @Test
    void indentPreservationOnModification() {
        rewriteRun(spec -> {
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
                            System.err.println("found class: " + statement);
                            J.Block body = ((J.ClassDeclaration) statement).getBody();
                            for (Statement classStatement : body.getStatements()) {
                                if (classStatement instanceof J.MethodDeclaration) {
                                    System.err.println("found method: " + ((J.MethodDeclaration) classStatement).getSimpleName());
                                    if (existing.add(((J.MethodDeclaration) classStatement).getSimpleName())) {
                                        copied.add(classStatement);
                                    }
                                }
                            }
                        }
                    }
                    System.err.println(copied);
                    return block.withStatements(ListUtils.concatAll(
                      block.getStatements(),
                      copied
                    ));
                }
            }));
        }, python(
          """                
            class A:           
                def f():
                    # a loop
                    while True:
                        pass
                
                def g():
                    pass
            """,
          """
            class A:           
                def f():
                    # a loop
                    while True:
                        pass
                
                def g():
                    pass
            def f():
                # a loop
                while True:
                    pass
            
            def g():
                pass
            """
        ));
    }

}
