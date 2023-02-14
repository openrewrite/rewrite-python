package org.openrewrite.python.tree;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

/*
    TODO split into separate test files for related functionality (2023-02-10)
 */
public class ParsingTest implements RewriteTest {

    @Test
    void variableReference() {
        rewriteRun(
          python("x")
        );
    }

    @Test
    void variableReferenceNestedSpacing() {
        rewriteRun(
          python("x + y")
        );
    }

    @Test
    void variableReferenceNestedSpacingLhs() {
        rewriteRun(
          python("x +y")
        );
    }

    @Test
    void variableReferenceNestedSpacingRhs() {
        rewriteRun(
          python("x+ y")
        );
    }

    @Test
    void variableDeclNoSpace() {
        rewriteRun(
          python("n=1")
        );
    }

    @Test
    void variableDecl() {
        rewriteRun(
          python("n = 1")
        );
    }

    @Test
    void methodInvocationNoSpace() {
        rewriteRun(
          python("print(42)")
        );
    }

    @Test
    void methodInvocationExtraSpace() {
        rewriteRun(
          python("print( 42 )")
        );
    }

    @Test
    void methodInvocationMultiArg() {
        rewriteRun(
          python("print(1, 2, 3, 4)")
        );
    }

    @Test
    void methodInvocationMultiArgExtraSpaceAround() {
        rewriteRun(
          python("print( 1, 2, 3, 4 )")
        );
    }

    @Test
    void methodInvocationMultiArgExtraSpaceWithin() {
        rewriteRun(
          python("print(1 , 2 , 3 , 4)")
        );
    }

    @Test
    void methodInvocationWithKwarg_FAILS() {
        /*
            This appears as a PyKeywordArgument.
            There may be no way to map this using a raw J.* implementation,
            but I haven't looked into how this is done for Groovy.

            —gary olsen, 2023-02-10
         */
        Assertions.assertThrows(Exception.class, () -> rewriteRun(
          python("print(1, 2, 3, 4, sep='+')")
        ));
    }

    @Test
    void methodInvocationOnQualifiedTarget_FAILS() {
        /*
            This appears as a `qualifier` on `PyReferenceExpression`.
            This should be straightforward to implement but isn't done.

            —gary olsen, 2023-02-10
         */
        Assertions.assertThrows(Exception.class, () -> rewriteRun(
          python("int.bit_length(42)")
        ));
    }

    @Test
    void methodInvocationOnExpressionTarget_FAILS() {
        /*
            Haven't looked into what the PSI looks like for this one.

            —gary olsen, 2023-02-10
         */
        Assertions.assertThrows(Exception.class, () -> rewriteRun(
          python("list().copy()")
        ));
    }

    @Test
    void indexOperator() {
        rewriteRun(
          python("x[0]")
        );
    }

    @Test
    void indexOperatorSpaceBetween() {
        rewriteRun(
          python("x [0]")
        );
    }

    @Test
    void indexOperatorLeftSpace() {
        rewriteRun(
          python("x[ 0]")
        );
    }

    @Test
    void indexOperatorRightSpace() {
        rewriteRun(
          python("x[0 ]")
        );
    }

}
