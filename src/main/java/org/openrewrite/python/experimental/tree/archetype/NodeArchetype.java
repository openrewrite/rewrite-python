package org.openrewrite.python.experimental.tree.archetype;

public interface NodeArchetype {
    void accept(NodeArchetypeVisitor visitor);
}
