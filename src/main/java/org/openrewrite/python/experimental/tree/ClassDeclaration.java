package org.openrewrite.python.experimental.tree;

import lombok.Value;
import org.openrewrite.python.experimental.PythonVisitor;
import org.openrewrite.python.experimental.tree.common.BetweenItemsList;
import org.openrewrite.python.experimental.tree.padding.ColonPadding;
import org.openrewrite.python.experimental.tree.padding.Padding;
import org.openrewrite.python.experimental.tree.padding.WrapPadding;

import java.util.Optional;

@Value
public class ClassDeclaration implements Statement {
    Identifier className;
    Optional<ExtendingPart> extendingPart;
    ColonPadding colonPadding;
    StatementList statementList;

    @Value
    public static class ExtendingPart implements PythonNode {
        Padding prefix;
        Padding beforeFirstBase;
        BetweenItemsList<Expression, WrapPadding> baseClasses;
        Padding afterLastBase;

        @Override
        public void accept(PythonVisitor visitor) {
            visitor.visitExtendingPart(this);
        }
    }


    @Override
    public void accept(PythonVisitor visitor) {
        visitor.visitClassDeclaration(this);
    }
}
