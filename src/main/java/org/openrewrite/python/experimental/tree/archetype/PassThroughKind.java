package org.openrewrite.python.experimental.tree.archetype;

import lombok.Value;
import org.openrewrite.python.experimental.tree.PythonNode;

@Value
public class PassThroughKind<T extends PythonNode> implements NodeArchetype {
    T wrapped;

    @Override
    public void accept(NodeArchetypeVisitor visitor) {
        visitor.visitPassThroughKind(this);
    }
}
