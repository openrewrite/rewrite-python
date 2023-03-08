package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class BlockTest implements RewriteTest {

    @Test
    public void singleStatement() {
        rewriteRun(python(
          """
            def f():
                pass
            """
        ));
    }

    @Test
    public void singleStatementWithDocstring() {
        rewriteRun(python(
          """
            def f():
                \"""a docstring\"""
                pass
            """
        ));
    }

    @Test
    public void singleStatementWithTrailingComment() {
        rewriteRun(python(
          """
            def f():
                pass  # a comment about the line
            """
        ));
    }

    @Test
    public void multiStatementWithBlankLines() {
        rewriteRun(python(
          """
            def f():
                pass
                
                pass
                
                pass
            """
        ));
    }

    @Test
    public void multiStatementWithTrailingComments() {
        rewriteRun(python(
          """
            def f():
                pass  # a comment about the line
                pass  # a comment about the line
                pass  # a comment about the line
            """
        ));
    }

    @Test
    public void multiStatementWithBetweenComments() {
        rewriteRun(python(
          """
            def f():
                pass
                # a comment on its own line
                # another comment on its own line
                pass
                # a comment on its own line
                # another comment on its own line
                pass
            """
        ));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "\n", "\n\n", "\n\n\n"})
    public void deeplyNested(String eof) {
        rewriteRun(python(
          """
            def f1():
                def f2():
                    pass
                    
                def f3():
                    
                    def f4():
                        pass
                    
                    pass%s""".formatted(eof)
        ));
    }



    @ParameterizedTest
    @ValueSource(strings = {"", "\n", "\n\n", "\n\n\n"})
    public void lineEndingLocations(String eof) {
        rewriteRun(
          python(
            """
              print(1) # a comment
              print(2)
              print(3)
                            
              print(4)  # a comment
              print(5)%s""".formatted(eof)
          )
        );
    }

}
