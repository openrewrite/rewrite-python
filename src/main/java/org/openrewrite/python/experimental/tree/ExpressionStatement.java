package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;

@Value
public class ExpressionStatement implements Statement {
    Expression expression;

    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitExpressionStatement(this);
    }
}
