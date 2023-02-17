package org.openrewrite.python.experimental.tree.archetype;

import org.openrewrite.python.experimental.tree.PythonNode;
import org.openrewrite.python.experimental.tree.padding.Padding;

public class UnaryOperatorKind<T extends PythonNode> implements NodeArchetype {
    public enum OperatorPosition {
        PREFIX, SUFFIX
    }

    OperatorPosition position;
    String operator;
    Padding between;
    T operand;

    @Override
    public void accept(NodeArchetypeVisitor visitor) {
        visitor.visitUnaryOperatorKind(this);
    }
}
