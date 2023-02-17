package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;
import org.openrewrite.python.experimental.tree.archetype.Archetypal;
import org.openrewrite.python.experimental.tree.archetype.BinaryOperatorKind;
import org.openrewrite.python.experimental.tree.padding.Padding;

@Value
public class BinaryOperatorExpression implements Expression, Archetypal<BinaryOperatorKind<Expression, Expression>> {
    Expression left;
    Padding beforeOperator;
    Operator operator;
    Padding afterOperator;
    Expression right;

    public enum OperatorClass {
        ARITHMETIC,
        LOGICAL,
        COMPARISON
    }

    public enum Operator {
        ADD("+", OperatorClass.ARITHMETIC),
        SUBTRACT("-", OperatorClass.ARITHMETIC),
        MULTIPLY("*", OperatorClass.ARITHMETIC),
        DIVIDE("/", OperatorClass.ARITHMETIC),
        AND("and", OperatorClass.LOGICAL),
        OR("or", OperatorClass.LOGICAL),
        EQUAL("==", OperatorClass.COMPARISON),
        NOT_EQUAL("!=", OperatorClass.COMPARISON),
        LESS_THAN("<", OperatorClass.COMPARISON),
        LESS_THAN_EQUAL("<=", OperatorClass.COMPARISON),
        GREATER_THAN(">", OperatorClass.COMPARISON),
        GREATER_THAN_EQUAL("<", OperatorClass.COMPARISON);

        public final String text;
        public final OperatorClass operatorClass;

        Operator(String text, OperatorClass operatorClass) {
            this.text = text;
            this.operatorClass = operatorClass;
        }
    }

    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitBinaryOperatorExpression(this);
    }

    @Override
    public BinaryOperatorKind<Expression, Expression> asArchetypalKind() {
        return new BinaryOperatorKind<>(left, beforeOperator, operator.text, afterOperator, right);
    }
}
