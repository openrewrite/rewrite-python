package org.openrewrite.python.experimental.tree.archetype;

import org.openrewrite.python.experimental.tree.PythonNode;

public interface Archetypal<T extends NodeArchetype> extends PythonNode {
    T asArchetypalKind();
}
