package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class LiteralParsingTest implements RewriteTest {

    @Test
    void booleanLiteralTrue() {
        rewriteRun(python("True"));
    }

    @Test
    void booleanLiteralFalse() {
        rewriteRun(python("False"));
    }

    @Test
    void floatLiteral() {
        rewriteRun(python("42.2"));
    }

    @Test
    void integerLiteral() {
        rewriteRun(python("42"));
    }

    @Test
    void stringLiteralDoubleQuote() {
        rewriteRun(python("\"hello world\""));
    }

    @Test
    void stringLiteralDoubleQuoteWithEscape() {
        rewriteRun(python("\"hello \\\"world\\\"\""));
    }

    @Test
    void stringLiteralSingleQuote() {
        rewriteRun(python("'hello world'"));
    }

    @Test
    void stringLiteralSingleQuoteWithEscape() {
        rewriteRun(python("'hello \\'world\\''"));
    }

}
