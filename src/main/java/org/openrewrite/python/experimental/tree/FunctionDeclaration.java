package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;
import org.openrewrite.python.experimental.tree.common.BetweenItemsList;
import org.openrewrite.python.experimental.tree.padding.Padding;
import org.openrewrite.python.experimental.tree.padding.WrapPadding;

@Value
public class FunctionDeclaration implements Statement {
    Identifier functionName;
    BetweenItemsList<Parameter, WrapPadding> parameters;
    Padding beforeColon;
    Padding afterColon;
    StatementList statementList;

    public interface Parameter extends PythonNode {
        Identifier getParameterName();

        void acceptParameterVisitor(ParameterVisitor visitor);

        @Override
        default void accept(PythonVisitor visitor) {
            acceptParameterVisitor(visitor);
        }
    }

    public interface ParameterVisitor {
        void visitSimpleParameter(SimpleParameter parameter);
        void visitDefaultParameter(DefaultParameter parameter);
        void visitArgsParameter(ArgsParameter parameter);
        void visitKeywordArgsParameter(KeywordArgsParameter parameter);
    }

    @Value
    public static class SimpleParameter implements Parameter {
        Identifier parameterName;

        @Override
        public void acceptParameterVisitor(ParameterVisitor visitor) {
            visitor.visitSimpleParameter(this);
        }
    }

    @Value
    public static class DefaultParameter implements Parameter {
        Identifier parameterName;
        Padding beforeEquals;
        Padding afterEquals;
        Expression defaultValue;

        @Override
        public void acceptParameterVisitor(ParameterVisitor visitor) {
            visitor.visitDefaultParameter(this);
        }
    }

    @Value
    public static class ArgsParameter implements Parameter {
        Padding afterStar;
        Identifier parameterName;

        @Override
        public void acceptParameterVisitor(ParameterVisitor visitor) {
            visitor.visitArgsParameter(this);
        }
    }

    @Value
    public static class KeywordArgsParameter implements Parameter {
        Padding afterDoubleStar;
        Identifier parameterName;

        @Override
        public void acceptParameterVisitor(ParameterVisitor visitor) {
            visitor.visitKeywordArgsParameter(this);
        }
    }

    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitFunctionDeclaration(this);
    }
}
