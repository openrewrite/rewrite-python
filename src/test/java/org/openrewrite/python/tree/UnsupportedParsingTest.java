package org.openrewrite.python.tree;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

/**
 * A temporary class to organize "next up" test cases to handle.
 */
public class UnsupportedParsingTest implements RewriteTest {

    //
    //  MODULE IMPORTS
    //

    @Test
    void simpleImport_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("import math")
        ));
    }

    @Test
    void localImport_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("from . import foo")
        ));
    }

    @Test
    void qualifiedImport_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("from math import ceil")
        ));
    }

    @Test
    void simpleImportAlias_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("import math as math2")
        ));
    }

    @Test
    void localImportAlias_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("from . import foo as foo2")
        ));
    }

    @Test
    void qualifiedImportAlias_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("from math import ceil as ceil2")
        ));
    }

    //
    //  CONTAINER-SPECIFIC SYNTAX
    //

    @Test
    void indexOperator_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x[0]")
        ));
    }

    @Test
    void sliceOperator_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x[3:5]")
        ));
    }

    @Test
    void listComprehension_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("[x for x in xs if x]")
        ));
    }

    //
    //  BUILT-IN DATA STRUCTURES
    //

    @Test
    void listExpression_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("xs = [1, 2, 3]")
        ));
    }

    @Test
    void listExpressionEmpty_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("xs = []")
        ));
    }

    @Test
    void tupleExpression_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("xs = (1, 2, 3)")
        ));
    }

    @Test
    void tupleExpressionEmpty_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("xs = ()")
        ));
    }

    @Test
    void tupleExpressionSingle_FAILS() {
        // ()     => tuple
        // (1)    => int
        // (1,)   => tuple      <-- test this case
        // (1, 2) => tuple
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("xs = (1,)")
        ));
    }

    @Test
    void setExpression_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("xs = {1, 2, 3}")
        ));
    }

    @Test
    void dictExpression_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("xs = {\"foo\": \"bar\", \"foo2\": \"bar2\"}")
        ));
    }

    @Test
    void dictExpressionEmpty_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("xs = {}")
        ));
    }

    //
    //  CONTROL FLOW
    //

    @Test
    void pass_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("pass")
        ));
    }

    @Test
    void if_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            if True:
                pass
            """)
        ));
    }

    @Test
    void ifElse_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            if True:
                pass
            else:
                pass
            """)
        ));
    }

    @Test
    void ifElifElse_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            if True:
                pass
            elif False:
                pass
            else:
                pass
            """)
        ));
    }

    @Test
    void forLoop_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            for x in xs:
                pass
            """)
        ));
    }

    @Test
    void forLoopBreak_FAILS() {
        // nonsense program; meant to exclude other syntax elements
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            for x in xs:
                break
            """)
        ));
    }

    @Test
    void forLoopContinue_FAILS() {
        // nonsense program; meant to exclude other syntax elements
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            for x in xs:
                continue
            """)
        ));
    }

    //
    //  ABSTRACTION
    //

    @Test
    void classDefinition_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            class Name:
                pass
            """)
        ));
    }

    @Test
    void functionDefinition_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            def foo():
                pass
            """)
        ));
    }

    @Test
    void methodDefinition_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            class Foo:
                def foo():
                    pass
            """)
        ));
    }

    @Test
    void decorator_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            @something
            def foo():
                pass
            """)
        ));
    }

    @Test
    void decoratorWithParams_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("""
            @something(1, 2, 3)
            def foo():
                pass
            """)
        ));
    }

    //
    //  BOOLEAN OPERATORS
    //

    @Test
    void or_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x or y")
        ));
    }

    @Test
    void and_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x and y")
        ));
    }

    @Test
    void not_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("not y")
        ));
    }

    //
    //  COMPARISON OPERATORS
    //

    @Test
    void is_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x is y")
        ));
    }

    @Test
    void isNot_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x is not y")
        ));
    }

    @Test
    void in_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x in y")
        ));
    }

    @Test
    void notIn_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x not in y")
        ));
    }

    @Test
    void eq_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x == y")
        ));
    }

    @Test
    void neq_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x != y")
        ));
    }

    @Test
    void lt_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x < y")
        ));
    }

    @Test
    void lte_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x <= y")
        ));
    }

    @Test
    void gt_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x > y")
        ));
    }

    @Test
    void gte_FAILS() {
        Assertions.assertThrows(Throwable.class, () -> rewriteRun(
          python("x >= y")
        ));
    }

}
