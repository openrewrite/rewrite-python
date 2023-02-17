package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;

public interface Literal<T> extends Expression {
    T getValue();

    @Value
    class StringLiteral implements Literal<String> {
        public enum QuoteKind {
            SINGLE("'"),
            DOUBLE("\"");

            public final String text;

            QuoteKind(String text) {
                this.text = text;
            }
        }

        QuoteKind quoteKind;
        String raw;
        String value;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitStringLiteral(this);
        }
    }

    @Value
    class NumericLiteral implements Literal<Number> {
        String raw;
        Number value;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitNumericLiteral(this);
        }
    }

    @Value
    class BooleanLiteral implements Literal<Boolean> {
        Boolean value;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitBooleanLiteral(this);
        }
    }
}
