package org.openrewrite.python.experimental.tree.archetype;

import org.openrewrite.python.experimental.tree.PythonNode;

public interface NodeArchetypeVisitor {
    void visitBinaryOperatorKind(BinaryOperatorKind<?, ?> archetype);

    void visitPassThroughKind(PassThroughKind<?> archetype);

    void visitUnaryOperatorKind(UnaryOperatorKind<?> archetype);

    void visitWrappedKind(WrappedKind<?> archetype);
}
