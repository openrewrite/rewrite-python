package org.openrewrite.python.internal;

import com.intellij.extapi.psi.ASTWrapperPsiElement;
import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiWhiteSpace;
import com.jetbrains.python.psi.PyAssignmentStatement;
import com.jetbrains.python.psi.PyExpression;
import com.jetbrains.python.psi.PyNumericLiteralExpression;
import com.jetbrains.python.psi.PyTargetExpression;
import org.openrewrite.FileAttributes;
import org.openrewrite.java.tree.*;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.internal.IntelliJUtils;
import org.openrewrite.python.tree.P;

import java.nio.file.Path;
import java.util.*;

import static org.openrewrite.Tree.randomId;

public class PsiPythonMapper {

    public P.CompilationUnit mapFile(Path path, String charset, boolean isCharsetBomMarked, ASTWrapperPsiElement element) {
        new IntelliJUtils.PsiPrinter().print(element.getNode());
        List<Statement> statements = new ArrayList<>();
        for (ASTNode child : element.getNode().getChildren(null)) {
            Statement statement = mapStatement(child.getPsi());
            if (statement != null) {
                statements.add(statement);
            }
        }
        return new P.CompilationUnit(
                randomId(),
                Space.EMPTY,
                Markers.EMPTY,
                path,
                FileAttributes.fromPath(path),
                charset,
                isCharsetBomMarked,
                null,
                Collections.emptyList(),
                Collections.emptyList(),
                Space.EMPTY
        ).withStatements(statements);
    }

    public Statement mapStatement(PsiElement element) {
        if (element instanceof PyAssignmentStatement) {
            return mapAssignmentStatement((PyAssignmentStatement) element);
        }
        System.err.println("WARNING: unhandled statement of type " + element.getClass().getSimpleName());
        return null;
    }

    public Statement mapAssignmentStatement(PyAssignmentStatement element) {
        PyExpression pyLhs = element.getLeftHandSideExpression();
        PyExpression pyRhs = element.getAssignedValue();

        J.Identifier lhs = expectIdentifier(mapExpression(pyLhs));
        Expression rhs = mapExpression(pyRhs).withPrefix(whitespaceBefore(pyRhs));

        return new J.Assignment(
                UUID.randomUUID(),
                whitespaceBefore(pyLhs),
                Markers.EMPTY,
                lhs,
                JLeftPadded.build(rhs).withBefore(whitespaceBefore(pyRhs)),
                null
        );
    }

    public Expression mapExpression(PyExpression element) {
        if (element instanceof PyNumericLiteralExpression) {
            return mapNumericLiteral((PyNumericLiteralExpression) element);
        } else if (element instanceof PyTargetExpression) {
            return mapTargetExpression((PyTargetExpression) element);
        }
        System.err.println("WARNING: unhandled expression of type " + element.getClass().getSimpleName());
        return null;
    }

    public J.Identifier mapTargetExpression(PyTargetExpression element) {
        return new J.Identifier(UUID.randomUUID(), Space.EMPTY, Markers.EMPTY, element.getName(), null, null);
    }

    public J.Literal mapNumericLiteral(PyNumericLiteralExpression element) {
        return new J.Literal(UUID.randomUUID(), Space.EMPTY, Markers.EMPTY, element.getLongValue(), element.getText(), Collections.emptyList(), JavaType.Primitive.Long);
    }

    private static J.Identifier expectIdentifier(Expression expression) {
        if (expression instanceof J.Identifier) {
            return (J.Identifier) expression;
        }
        throw new RuntimeException("expected Identifier, but found: " + expression.getClass().getSimpleName());
    }

    private static Space whitespaceBefore(PsiElement element) {
        PsiElement previous = element.getPrevSibling();
        if (previous == null) {
            return Space.EMPTY;
        }
        if (previous instanceof PsiWhiteSpace) {
            return Space.build(previous.getText(), Collections.emptyList());
        }
        return Space.EMPTY;
    }

    private static Space whitespaceAfter(PsiElement element) {
        PsiElement previous = element.getNextSibling();
        if (previous == null) {
            return Space.EMPTY;
        }
        if (previous instanceof PsiWhiteSpace) {
            return Space.build(previous.getText(), Collections.emptyList());
        }
        return Space.EMPTY;
    }

}
