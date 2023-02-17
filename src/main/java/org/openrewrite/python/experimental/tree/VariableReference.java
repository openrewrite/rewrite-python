package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;
import org.openrewrite.python.experimental.tree.archetype.Archetypal;
import org.openrewrite.python.experimental.tree.archetype.PassThroughKind;

@Value
public class VariableReference implements Expression, Archetypal<PassThroughKind<Identifier>> {
    Identifier name;

    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitVariableReference(this);
    }


    @Override
    public PassThroughKind<Identifier> asArchetypalKind() {
        return new PassThroughKind<>(name);
    }
}
