package org.openrewrite.python.experimental.tree.archetype;

import lombok.Value;
import org.openrewrite.python.experimental.tree.PythonNode;
import org.openrewrite.python.experimental.tree.padding.Padding;

@Value
public class BinaryOperatorKind<TLeft extends PythonNode, TRight extends PythonNode> implements NodeArchetype {
    TLeft left;
    Padding beforeOperator;
    String operator;
    Padding afterOperator;
    TRight right;

    @Override
    public void accept(NodeArchetypeVisitor visitor) {
        visitor.visitBinaryOperatorKind(this);
    }
}
