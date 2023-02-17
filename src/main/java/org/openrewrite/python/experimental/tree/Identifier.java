package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;

@Value
public class Identifier implements PythonNode {
    String text;

    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitIdentifier(this);
    }

    @Override
    public String toString() {
        return "Identifier(" + text + ")";
    }
}
