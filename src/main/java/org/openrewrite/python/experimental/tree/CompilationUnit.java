package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;
import org.openrewrite.python.experimental.tree.common.ItemList;

@Value
public class CompilationUnit implements PythonNode {
    ItemList<Statement> statements;

    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitCompilationUnit(this);
    }
}
