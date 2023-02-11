package org.openrewrite.python.internal;

import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiWhiteSpace;
import com.jetbrains.python.psi.*;
import org.openrewrite.FileAttributes;
import org.openrewrite.java.tree.*;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.tree.P;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

import static org.openrewrite.Tree.randomId;

public class PsiPythonMapper {

    public P.CompilationUnit mapFile(Path path, String charset, boolean isCharsetBomMarked, PyFile element) {
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
        } else if (element instanceof PyExpressionStatement) {
            return mapExpressionStatement((PyExpressionStatement) element);
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
        if (element instanceof PyCallExpression) {
            return mapCallExpression((PyCallExpression) element);
        } else if (element instanceof PyNumericLiteralExpression) {
            return mapNumericLiteral((PyNumericLiteralExpression) element);
        } else if (element instanceof PyStringLiteralExpression) {
            return mapStringLiteral((PyStringLiteralExpression) element);
        } else if (element instanceof PyTargetExpression) {
            return mapTargetExpression((PyTargetExpression) element);
        }
        System.err.println("WARNING: unhandled expression of type " + element.getClass().getSimpleName());
        return null;
    }

    public Expression expectExpression(PsiElement element) {
        if (!(element instanceof PyExpression)) {
            throw new RuntimeException("expected expression; found: " + element.getClass().getSimpleName());
        }
        return mapExpression((PyExpression) element);
    }

    public J.MethodInvocation mapCallExpression(PyCallExpression element) {
        PyExpression pyCallee = element.getCallee();
        if (pyCallee instanceof PyReferenceExpression) {
            // e.g. `print(42)`
            PyReferenceExpression pyRefExpression = (PyReferenceExpression) pyCallee;
            if (pyRefExpression.getQualifier() != null) {
                throw new RuntimeException("unexpected reference qualification on call expression");
            }
            J.Identifier functionName = new J.Identifier(
                    UUID.randomUUID(),
                    whitespaceBefore(pyRefExpression),
                    Markers.EMPTY,
                    pyRefExpression.getName(),
                    null,
                    null
            );
            List<JRightPadded<Expression>> args = new ArrayList<>();
            for (PyExpression arg : element.getArgumentList().getArguments()) {
                args.add(
                        new JRightPadded<>(
                                mapExpression(arg).withPrefix(whitespaceBefore(arg)),
                                whitespaceAfter(arg),
                                Markers.EMPTY
                        )
                );
            }
            return new J.MethodInvocation(
                    UUID.randomUUID(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    null,
                    null,
                    functionName,
                    JContainer.build(Space.EMPTY, args, Markers.EMPTY),
                    null
            );
        } else {
            System.err.println("WARNING: unhandled call expression; callee is not a reference");
        }
        return null;
    }

    public P.ExpressionStatement mapExpressionStatement(PyExpressionStatement element) {
        Expression expression = mapExpression(element.getExpression());
        return new P.ExpressionStatement(UUID.randomUUID(), expression);
    }

    public J.Literal mapStringLiteral(PyStringLiteralExpression element) {
        return new J.Literal(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                element.getStringValue(),
                element.getText(),
                Collections.emptyList(),
                JavaType.Primitive.String
        );
    }

    public J.Identifier mapTargetExpression(PyTargetExpression element) {
        return new J.Identifier(UUID.randomUUID(), Space.EMPTY, Markers.EMPTY, element.getName(), null, null);
    }

    public J.Literal mapNumericLiteral(PyNumericLiteralExpression element) {
        return new J.Literal(UUID.randomUUID(), Space.EMPTY, Markers.EMPTY, element.getLongValue(), element.getText(), Collections.emptyList(), JavaType.Primitive.Long);
    }

    private J.Identifier expectIdentifier(Expression expression) {
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
