package org.openrewrite.python.experimental.tree.archetype;

import lombok.Value;
import org.openrewrite.python.experimental.tree.PythonNode;
import org.openrewrite.python.experimental.tree.padding.Padding;

@Value
public class WrappedKind<T extends PythonNode> implements NodeArchetype {
    Padding before;
    T wrapped;
    Padding after;

    @Override
    public void accept(NodeArchetypeVisitor visitor) {
        visitor.visitWrappedKind(this);
    }
}
