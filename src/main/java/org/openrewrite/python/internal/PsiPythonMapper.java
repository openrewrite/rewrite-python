package org.openrewrite.python.internal;

import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiWhiteSpace;
import com.jetbrains.python.PyTokenTypes;
import com.jetbrains.python.psi.*;
import org.openrewrite.FileAttributes;
import org.openrewrite.java.tree.*;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.marker.IsElIfBranch;
import org.openrewrite.python.tree.P;

import java.nio.file.Path;
import java.util.*;

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
        } else if (element instanceof PyClass) {
            return mapClassDeclarationStatement((PyClass) element);
        } else if (element instanceof PyExpressionStatement) {
            return mapExpressionStatement((PyExpressionStatement) element);
        } else if (element instanceof PyIfStatement) {
            return mapIfStatement((PyIfStatement) element);
        } else if (element instanceof PyPassStatement) {
            return mapPassStatement((PyPassStatement) element);
        } else if (element instanceof PyStatementList) {
            return mapStatementList((PyStatementList) element);
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

    public Statement mapClassDeclarationStatement(PyClass element) {
        J.ClassDeclaration.Kind kind = new J.ClassDeclaration.Kind(
                UUID.randomUUID(),
                Space.EMPTY,
                Markers.EMPTY,
                Collections.emptyList(),
                J.ClassDeclaration.Kind.Type.Class
        );

        JLeftPadded<TypeTree> extendings = null;
        {
            PyArgumentList pyClassBase = element.getSuperClassExpressionList();
            // if there are no children, there are no paren tokens
            // otherwise we have to render e.g. `class Foo():` even without a base class
            if (pyClassBase != null) {
                if (element.getSuperClassExpressions().length > 0) {
                    PyExpression firstBase = element.getSuperClassExpressions()[0];
                    if (!(firstBase instanceof PyReferenceExpression)) {
                        throw new RuntimeException("cannot support non-constant base classes");
                    }
                    J.Identifier baseIdentifier = mapReferenceExpression((PyReferenceExpression) firstBase)
                            .withPrefix(whitespaceBefore(firstBase));
                    extendings = JLeftPadded.<TypeTree>build(baseIdentifier);
                } else {
                    extendings = JLeftPadded.<TypeTree>build(
                            new J.Empty(
                                    UUID.randomUUID(),
                                    whitespaceBefore(pyClassBase.getNode().getLastChildNode().getPsi()),
                                    Markers.EMPTY
                            )
                    );
                }
            }
        }

        return new J.ClassDeclaration(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                Collections.emptyList(),
                Collections.emptyList(),
                kind,
                expectIdentifier(element.getNameNode()),
                null,
                null,
                extendings,
                null,
                null,
                mapStatementList(element.getStatementList()),
                null
        );
    }

    public Statement mapIfStatement(PyIfStatement element) {
        PyExpression pyIfCondition = element.getIfPart().getCondition();
        PyStatementList pyIfBody = element.getIfPart().getStatementList();

        if (pyIfCondition == null) {
            throw new RuntimeException("if condition is null");
        }

        Expression ifCondition = mapExpression(pyIfCondition);
        Statement ifBody = mapStatement(pyIfBody);
        J.If.Else elsePart = mapElsePart(element, 0);

        return new J.If(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                new J.ControlParentheses<Expression>(
                        UUID.randomUUID(),
                        Space.EMPTY,
                        Markers.EMPTY,
                        JRightPadded.build(ifCondition).withAfter(whitespaceAfter(pyIfCondition))
                ),
                JRightPadded.build(ifBody).withAfter(whitespaceAfter(pyIfBody)),
                elsePart
        );
    }

    /**
     * In Python, if/else alternatives are flattened into a single AST node.
     * To be represented using the `J` classes, each `elif` branch needs to be
     * transformed into an `else` containing a single `if` statement.
     * <p>
     * This method helps transform the original flattened structure into the
     * recursive `J` representation.
     */
    private J.If.Else mapElsePart(PyIfStatement parent, int elifIndex) {
        if (elifIndex < parent.getElifParts().length) {
            PyIfPart pyElifPart = parent.getElifParts()[elifIndex];

            PyExpression pyIfCondition = pyElifPart.getCondition();
            PyStatementList pyIfBody = pyElifPart.getStatementList();

            if (pyIfCondition == null) {
                throw new RuntimeException("if condition is null");
            }

            Expression ifCondition = mapExpression(pyIfCondition);
            Statement ifBody = mapStatement(pyIfBody);

            J.If nestedIf = new J.If(
                    UUID.randomUUID(),
                    Space.EMPTY,
                    Markers.build(Collections.singletonList(new IsElIfBranch(UUID.randomUUID()))),
                    new J.ControlParentheses<Expression>(
                            UUID.randomUUID(),
                            Space.EMPTY,
                            Markers.EMPTY,
                            JRightPadded.build(ifCondition).withAfter(whitespaceAfter(pyIfCondition))
                    ),
                    JRightPadded.build(ifBody).withAfter(whitespaceAfter(pyIfBody)),
                    mapElsePart(parent, elifIndex + 1)
            );
            return new J.If.Else(
                    UUID.randomUUID(),
                    whitespaceBefore(pyElifPart),
                    Markers.build(Collections.singletonList(new IsElIfBranch(UUID.randomUUID()))),
                    JRightPadded.<Statement>build(nestedIf)
            );
        } else if (parent.getElsePart() != null) {
            PyStatementList pyElseBody = parent.getElsePart().getStatementList();
            return new J.If.Else(
                    UUID.randomUUID(),
                    whitespaceBefore(parent.getElsePart()),
                    Markers.EMPTY,
                    JRightPadded.<Statement>build(mapStatementList(pyElseBody))
                            .withAfter(whitespaceAfter(pyElseBody))
            );
        } else {
            return null;
        }
    }

    public P.PassStatement mapPassStatement(PyPassStatement element) {
        return new P.PassStatement(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY
        );
    }

    public J.Block mapStatementList(PyStatementList element) {
        PyStatement[] pyStatements = element.getStatements();
        List<JRightPadded<Statement>> statements = new ArrayList<>(pyStatements.length);
        for (PyStatement pyStatement : pyStatements) {
            Statement statement = mapStatement(pyStatement);
            statements.add(JRightPadded.build(statement).withAfter(whitespaceAfter(pyStatement)));
        }

        return new J.Block(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                JRightPadded.build(false),
                statements,
                whitespaceAfter(element)
        );
    }

    public Expression mapExpression(PyExpression element) {
        if (element instanceof PyBinaryExpression) {
            return mapBinaryExpression((PyBinaryExpression) element);
        } else if (element instanceof PyBoolLiteralExpression) {
            return mapBooleanLiteral((PyBoolLiteralExpression) element);
        } else if (element instanceof PyCallExpression) {
            return mapCallExpression((PyCallExpression) element);
        } else if (element instanceof PyNumericLiteralExpression) {
            return mapNumericLiteral((PyNumericLiteralExpression) element);
        } else if (element instanceof PyReferenceExpression) {
            return mapReferenceExpression((PyReferenceExpression) element);
        } else if (element instanceof PySubscriptionExpression) {
            return mapSubscription((PySubscriptionExpression) element);
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


    private final static Map<PyElementType, J.Binary.Type> binaryOperatorTypeMappings = new HashMap<>();

    static {
        // Comparison
        binaryOperatorTypeMappings.put(PyTokenTypes.LT, J.Binary.Type.LessThan);
        binaryOperatorTypeMappings.put(PyTokenTypes.LE, J.Binary.Type.LessThanOrEqual);
        binaryOperatorTypeMappings.put(PyTokenTypes.GT, J.Binary.Type.GreaterThan);
        binaryOperatorTypeMappings.put(PyTokenTypes.GE, J.Binary.Type.GreaterThanOrEqual);
        binaryOperatorTypeMappings.put(PyTokenTypes.EQEQ, J.Binary.Type.Equal);
        binaryOperatorTypeMappings.put(PyTokenTypes.NE, J.Binary.Type.NotEqual);

        // Arithmetic
        binaryOperatorTypeMappings.put(PyTokenTypes.DIV, J.Binary.Type.Division);
        binaryOperatorTypeMappings.put(PyTokenTypes.MINUS, J.Binary.Type.Subtraction);
        binaryOperatorTypeMappings.put(PyTokenTypes.MULT, J.Binary.Type.Multiplication);
        binaryOperatorTypeMappings.put(PyTokenTypes.PLUS, J.Binary.Type.Addition);
    }

    public J.Binary mapBinaryExpression(PyBinaryExpression element) {
        Expression lhs = mapExpression(element.getLeftExpression());
        Expression rhs = mapExpression(element.getRightExpression());
        Space beforeOperatorSpace = whitespaceAfter(element.getLeftExpression());

        PyElementType pyOperatorType = element.getOperator();
        J.Binary.Type operatorType = binaryOperatorTypeMappings.get(pyOperatorType);

        if (operatorType == null) {
            throw new RuntimeException("unsupported binary expression operator: " + pyOperatorType);
        }


        return new J.Binary(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                lhs,
                JLeftPadded.build(operatorType).withBefore(beforeOperatorSpace),
                rhs,
                null
        );
    }

    public J.Literal mapBooleanLiteral(PyBoolLiteralExpression element) {
        return new J.Literal(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                element.getValue(),
                element.getText(),
                Collections.emptyList(),
                JavaType.Primitive.Boolean
        );
    }

    public J.MethodInvocation mapCallExpression(PyCallExpression element) {
        PyExpression pyCallee = element.getCallee();
        if (pyCallee instanceof PyReferenceExpression) {
            // e.g. `print(42)`
            PyReferenceExpression pyRefExpression = (PyReferenceExpression) pyCallee;
            J.Identifier functionName = mapReferenceExpression(pyRefExpression);

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
                    whitespaceBefore(element),
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

    public J.ArrayAccess mapSubscription(PySubscriptionExpression element) {
        PyExpression pyTarget = element.getOperand();
        PyExpression pyIndex = element.getIndexExpression();

        Expression target = mapExpression(pyTarget);
        Expression index = mapExpression(pyIndex);

        return new J.ArrayAccess(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                target,
                new J.ArrayDimension(
                        UUID.randomUUID(),
                        whitespaceAfter(pyTarget),
                        Markers.EMPTY,
                        JRightPadded.build(index).withAfter(whitespaceAfter(pyIndex))
                ),
                null
        );
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
        return new J.Identifier(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                element.getName(),
                null,
                null
        );
    }

    public J.Literal mapNumericLiteral(PyNumericLiteralExpression element) {
        return new J.Literal(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                element.getLongValue(),
                element.getText(),
                Collections.emptyList(),
                JavaType.Primitive.Long
        );
    }

    public J.Identifier mapReferenceExpression(PyReferenceExpression element) {
        if (element.getQualifier() != null) {
            throw new RuntimeException("unexpected reference qualification");
        }
        return new J.Identifier(
                UUID.randomUUID(),
                whitespaceBefore(element),
                Markers.EMPTY,
                element.getText(),
                null,
                null
        );
    }

    private J.Identifier expectIdentifier(Expression expression) {
        if (expression instanceof J.Identifier) {
            return (J.Identifier) expression;
        }
        throw new RuntimeException("expected Identifier, but found: " + expression.getClass().getSimpleName());
    }

    private J.Identifier expectIdentifier(ASTNode node) {
        if (node.getElementType() != PyTokenTypes.IDENTIFIER) {
            throw new RuntimeException("expected Identifier, but node type was: " + node.getElementType());
        }
        return new J.Identifier(
                UUID.randomUUID(),
                whitespaceBefore(node.getPsi()),
                Markers.EMPTY,
                node.getText(),
                null,
                null
        );
    }

    private J.Identifier expectIdentifier(PsiElement element) {
        return expectIdentifier(element.getNode());
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
