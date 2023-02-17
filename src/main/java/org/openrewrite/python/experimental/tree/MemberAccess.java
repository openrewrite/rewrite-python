package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;
import org.openrewrite.python.experimental.tree.archetype.Archetypal;
import org.openrewrite.python.experimental.tree.archetype.BinaryOperatorKind;
import org.openrewrite.python.experimental.tree.padding.Padding;

@Value
public class MemberAccess implements Expression, Archetypal<BinaryOperatorKind<Expression, Identifier>> {
    Expression target;
    Padding afterTarget;
    Padding beforeName;
    Identifier name;

    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitMemberAccess(this);
    }

    public BinaryOperatorKind<Expression, Identifier> asArchetypalKind() {
        return new BinaryOperatorKind<>(target, afterTarget, ".", beforeName, name);
    }
}
