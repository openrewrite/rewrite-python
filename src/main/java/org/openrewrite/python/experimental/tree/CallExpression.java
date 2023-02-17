package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;
import org.openrewrite.python.experimental.tree.archetype.Archetypal;
import org.openrewrite.python.experimental.tree.archetype.BinaryOperatorKind;
import org.openrewrite.python.experimental.tree.archetype.PassThroughKind;
import org.openrewrite.python.experimental.tree.common.BetweenItemsList;
import org.openrewrite.python.experimental.tree.padding.Padding;
import org.openrewrite.python.experimental.tree.padding.WrapPadding;

@Value
public class CallExpression implements Expression {

    Expression target;
    Padding beforeArgumentList;
    ArgumentList argumentList;

    public interface Argument extends PythonNode {
        Expression getExpression();
    }

    @Value
    public static class PositionalArgument implements Argument, Archetypal<PassThroughKind<Expression>> {
        Expression expression;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitPositionalArgument(this);
        }

        @Override
        public PassThroughKind<Expression> asArchetypalKind() {
            return new PassThroughKind<>(expression);
        }
    }

    @Value
    public static class KeywordArgument implements Argument, Archetypal<BinaryOperatorKind<Identifier, Expression>> {
        Identifier keyword;
        Padding afterKeyword;
        Padding beforeExpression;
        Expression expression;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitKeywordArgument(this);
        }

        @Override
        public BinaryOperatorKind<Identifier, Expression> asArchetypalKind() {
            return new BinaryOperatorKind<>(keyword, afterKeyword, "=", beforeExpression, expression);
        }
    }

    @Value
    public static class ArgumentList implements PythonNode {
        BetweenItemsList<Argument, WrapPadding> arguments;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitArgumentList(this);
        }
    }


    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitCallExpression(this);
    }
}
