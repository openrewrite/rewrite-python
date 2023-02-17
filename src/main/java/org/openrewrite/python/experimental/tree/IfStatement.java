package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;
import org.openrewrite.python.experimental.tree.common.ItemList;
import org.openrewrite.python.experimental.tree.padding.Padding;

import java.util.Optional;

@Value
public class IfStatement implements PythonNode {
    IfPart ifPart;
    ItemList<ElIfPart> elIfParts;
    Optional<ElsePart> elsePart;

    interface Part extends PythonNode {
        Padding getBeforeColon();
        Padding getAfterColon();
        StatementList getStatementList();
    }

    interface ConditionalPart extends Part {
        Padding getBeforeCondition();
        Expression getCondition();
    }

    @Value
    public static class IfPart implements ConditionalPart {
        Padding beforeCondition;
        Expression condition;
        Padding beforeColon;
        Padding afterColon;
        StatementList statementList;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitIfPart(this);
        }
    }

    @Value
    public static class ElIfPart implements ConditionalPart {
        Padding beforeCondition;
        Expression condition;
        Padding beforeColon;
        Padding afterColon;
        StatementList statementList;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitElIfPart(this);
        }
    }

    @Value
    public static class ElsePart implements Part {
        Padding beforeColon;
        Padding afterColon;
        StatementList statementList;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitElsePart(this);
        }
    }

    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitIfStatement(this);
    }
}
