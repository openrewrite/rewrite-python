package org.openrewrite.python.internal;

import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiWhiteSpace;
import com.jetbrains.python.PyTokenTypes;
import com.jetbrains.python.psi.*;
import org.openrewrite.FileAttributes;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.*;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.marker.IsElIfBranch;
import org.openrewrite.python.tree.P;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.openrewrite.Tree.randomId;
import static org.openrewrite.marker.Markers.EMPTY;

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
                EMPTY,
                path,
                FileAttributes.fromPath(path),
                charset,
                isCharsetBomMarked,
                null,
                emptyList(),
                emptyList(),
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
                randomId(),
                whitespaceBefore(pyLhs),
                EMPTY,
                lhs,
                JLeftPadded.build(rhs).withBefore(whitespaceBefore(pyRhs)),
                null
        );
    }

    public Statement mapClassDeclarationStatement(PyClass element) {
        J.ClassDeclaration.Kind kind = new J.ClassDeclaration.Kind(
                randomId(),
                Space.EMPTY,
                EMPTY,
                emptyList(),
                J.ClassDeclaration.Kind.Type.Class
        );

        JContainer<TypeTree> implementings = null;
        PyArgumentList pyClassBase = element.getSuperClassExpressionList();
        // if there are no children, there are no paren tokens
        // otherwise we have to render e.g. `class Foo():` even without a base class
        if (pyClassBase != null) {
            if (element.getSuperClassExpressions().length > 0) {
                List<JRightPadded<TypeTree>> superClasses = new ArrayList<>(element.getSuperClassExpressions().length);
                PyExpression[] superClassExpressions = element.getSuperClassExpressions();
                for (PyExpression superClass : superClassExpressions) {
                    if (!(superClass instanceof PyReferenceExpression)) {
                        throw new RuntimeException("cannot support non-constant base classes");
                    }
                    superClasses.add(JRightPadded.build((TypeTree) mapReferenceExpression((PyReferenceExpression) superClass)
                                    .withPrefix(whitespaceBefore(superClass)))
                            .withAfter(whitespaceAfter(superClass)));
                }
                implementings = JContainer.build(superClasses);
            } else {
                implementings = JContainer.build(singletonList(
                        JRightPadded.build(
                                new J.Empty(
                                        randomId(),
                                        whitespaceBefore(pyClassBase.getNode().getLastChildNode().getPsi()),
                                        EMPTY
                                )
                        )));
            }
        }

        return new J.ClassDeclaration(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                emptyList(),
                emptyList(),
                kind,
                expectIdentifier(element.getNameNode()),
                null,
                null,
                null,
                implementings == null ?
                        null :
                        implementings.withBefore(whitespaceBefore(element.getSuperClassExpressionList())),
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
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                new J.ControlParentheses<Expression>(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
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
                    randomId(),
                    Space.EMPTY,
                    Markers.build(singletonList(new IsElIfBranch(randomId()))),
                    new J.ControlParentheses<Expression>(
                            randomId(),
                            Space.EMPTY,
                            EMPTY,
                            JRightPadded.build(ifCondition).withAfter(whitespaceAfter(pyIfCondition))
                    ),
                    JRightPadded.build(ifBody).withAfter(whitespaceAfter(pyIfBody)),
                    mapElsePart(parent, elifIndex + 1)
            );
            return new J.If.Else(
                    randomId(),
                    whitespaceBefore(pyElifPart),
                    Markers.build(singletonList(new IsElIfBranch(randomId()))),
                    JRightPadded.build(nestedIf)
            );
        } else if (parent.getElsePart() != null) {
            PyStatementList pyElseBody = parent.getElsePart().getStatementList();
            return new J.If.Else(
                    randomId(),
                    whitespaceBefore(parent.getElsePart()),
                    EMPTY,
                    JRightPadded.<Statement>build(mapStatementList(pyElseBody))
                            .withAfter(whitespaceAfter(pyElseBody))
            );
        } else {
            return null;
        }
    }

    public P.PassStatement mapPassStatement(PyPassStatement element) {
        return new P.PassStatement(
                randomId(),
                whitespaceBefore(element),
                EMPTY
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
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                JRightPadded.build(false),
                statements,
                whitespaceAfter(element)
        );
    }

    public Expression mapExpression(@Nullable PyExpression element) {
        if (element == null) {
            //noinspection DataFlowIssue
            return null;
        } else if (element instanceof PyBinaryExpression) {
            return mapBinaryExpression((PyBinaryExpression) element);
        } else if (element instanceof PyBoolLiteralExpression) {
            return mapBooleanLiteral((PyBoolLiteralExpression) element);
        } else if (element instanceof PyCallExpression) {
            return mapCallExpression((PyCallExpression) element);
        } else if (element instanceof PyNumericLiteralExpression) {
            return mapNumericLiteral((PyNumericLiteralExpression) element);
        } else if (element instanceof PyPrefixExpression) {
            return mapPrefixExpression((PyPrefixExpression) element);
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

    // FIXME don't use a map here -- use a switch statement computationally cheaper
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
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                lhs,
                JLeftPadded.build(operatorType).withBefore(beforeOperatorSpace),
                rhs,
                null
        );
    }

    private Expression mapPrefixExpression(PyPrefixExpression element) {
        PyElementType op = element.getOperator();
        J.Unary.Type ot;
        JavaType type = null;
        if (op == PyTokenTypes.NOT_KEYWORD) {
            ot = J.Unary.Type.Not;
            type = JavaType.Primitive.Boolean;
        } else if (op == PyTokenTypes.PLUS) {
            ot = J.Unary.Type.Positive;
        } else if (op == PyTokenTypes.MINUS) {
            ot = J.Unary.Type.Negative;
        } else {
            System.err.println("WARNING: unhandled prefix expression of ot " + op);
            return null;
        }
        return new J.Unary(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                JLeftPadded.build(ot),
                mapExpression(element.getOperand()),
                type
        );
    }

    public J.Literal mapBooleanLiteral(PyBoolLiteralExpression element) {
        return new J.Literal(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                element.getValue(),
                element.getText(),
                emptyList(),
                JavaType.Primitive.Boolean
        );
    }

    public J.MethodInvocation mapCallExpression(PyCallExpression element) {
        PyExpression pyCallee = element.getCallee();
        if (pyCallee instanceof PyReferenceExpression) {
            // e.g. `print(42)`
            PyReferenceExpression pyRefExpression = (PyReferenceExpression) pyCallee;
            J.Identifier functionName = mapReferenceExpression(pyRefExpression);

            List<JRightPadded<Expression>> args = emptyList();
            if (element.getArgumentList() != null) {
                args = new ArrayList<>();
                for (PyExpression arg : element.getArgumentList().getArguments()) {
                    args.add(
                            new JRightPadded<>(
                                    mapExpression(arg).withPrefix(whitespaceBefore(arg)),
                                    whitespaceAfter(arg),
                                    EMPTY
                            )
                    );
                }
            }

            return new J.MethodInvocation(
                    randomId(),
                    whitespaceBefore(element),
                    EMPTY,
                    null,
                    null,
                    functionName,
                    JContainer.build(Space.EMPTY, args, EMPTY),
                    null
            );
        } else {
            System.err.println("WARNING: unhandled call expression; callee is not a reference");
        }
        return null;
    }

    public P.ExpressionStatement mapExpressionStatement(PyExpressionStatement element) {
        Expression expression = mapExpression(element.getExpression());
        return new P.ExpressionStatement(randomId(), expression);
    }

    public J.ArrayAccess mapSubscription(PySubscriptionExpression element) {
        PyExpression pyTarget = element.getOperand();
        PyExpression pyIndex = element.getIndexExpression();

        Expression target = mapExpression(pyTarget);
        Expression index = mapExpression(pyIndex);

        return new J.ArrayAccess(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                target,
                new J.ArrayDimension(
                        randomId(),
                        whitespaceAfter(pyTarget),
                        EMPTY,
                        JRightPadded.build(index).withAfter(whitespaceAfter(pyIndex))
                ),
                null
        );
    }

    public J.Literal mapStringLiteral(PyStringLiteralExpression element) {
        return new J.Literal(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                element.getStringValue(),
                element.getText(),
                emptyList(),
                JavaType.Primitive.String
        );
    }

    public J.Identifier mapTargetExpression(PyTargetExpression element) {
        return new J.Identifier(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                element.getName(),
                null,
                null
        );
    }

    public J.Literal mapNumericLiteral(PyNumericLiteralExpression element) {
        return new J.Literal(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                element.getLongValue(),
                element.getText(),
                emptyList(),
                JavaType.Primitive.Long
        );
    }

    public J.Identifier mapReferenceExpression(PyReferenceExpression element) {
        if (element.getQualifier() != null) {
            throw new RuntimeException("unexpected reference qualification");
        }
        return new J.Identifier(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
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
                randomId(),
                whitespaceBefore(node.getPsi()),
                EMPTY,
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
            return Space.build(previous.getText(), emptyList());
        }
        return Space.EMPTY;
    }

    private static Space whitespaceAfter(PsiElement element) {
        PsiElement previous = element.getNextSibling();
        if (previous == null) {
            return Space.EMPTY;
        }
        if (previous instanceof PsiWhiteSpace) {
            return Space.build(previous.getText(), emptyList());
        }
        return Space.EMPTY;
    }

}
