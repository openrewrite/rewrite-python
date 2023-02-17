package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;
import org.openrewrite.python.experimental.tree.common.BetweenItemsList;
import org.openrewrite.python.experimental.tree.padding.BlankLines;
import org.openrewrite.python.experimental.tree.padding.Indent;

@Value
public class StatementList implements PythonNode {
    Indent indent;
    BetweenItemsList<Statement, BlankLines> statements;

    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitStatementList(this);
    }
}
