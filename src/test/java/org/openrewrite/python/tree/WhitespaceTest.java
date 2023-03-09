package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

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
            "\n ",
            "# comment\n",
            " # comment\n",
            "# comment \n",
            "# comment\n ",
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

}
