/*
 * Copyright 2021 the original author or authors.
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * https://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.openrewrite.python.internal;

import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiNamedElement;
import com.intellij.psi.PsiWhiteSpace;
import com.intellij.psi.impl.source.tree.LeafPsiElement;
import com.intellij.psi.util.QualifiedName;
import com.jetbrains.python.PyTokenTypes;
import com.jetbrains.python.psi.*;
import org.openrewrite.FileAttributes;
import org.openrewrite.Tree;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.marker.OmitParentheses;
import org.openrewrite.java.tree.*;
import org.openrewrite.python.tree.Py;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.function.Predicate;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static java.util.Objects.requireNonNull;
import static org.openrewrite.Tree.randomId;
import static org.openrewrite.marker.Markers.EMPTY;

public class PsiPythonMapper {

    public Py.CompilationUnit mapFile(Path path, String charset, boolean isCharsetBomMarked, PyFile element) {
        new IntelliJUtils.PsiPrinter().print(element.getNode());
        List<Statement> statements = new ArrayList<>();
        for (ASTNode child : element.getNode().getChildren(null)) {
            Statement statement = mapStatement(child.getPsi());
            if (statement != null) {
                statements.add(statement);
            }
        }
        return new Py.CompilationUnit(
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
        } else if (element instanceof PyBreakStatement) {
            return mapBreakStatement((PyBreakStatement) element);
        } else if (element instanceof PyContinueStatement) {
            return mapContinueStatement((PyContinueStatement) element);
        } else if (element instanceof PyClass) {
            return mapClassDeclarationStatement((PyClass) element);
        } else if (element instanceof PyExpressionStatement) {
            return mapExpressionStatement((PyExpressionStatement) element);
        } else if (element instanceof PyForStatement) {
            return mapForStatement((PyForStatement) element);
        } else if (element instanceof PyFunction) {
            return mapMethodDeclaration((PyFunction) element);
        } else if (element instanceof PyIfStatement) {
            return mapIfStatement((PyIfStatement) element);
        } else if (element instanceof PyPassStatement) {
            return mapPassStatement((PyPassStatement) element);
        } else if (element instanceof PyReturnStatement) {
            return mapReturnStatement((PyReturnStatement) element);
        } else if (element instanceof PyStatementList) {
            return mapBlock((PyStatementList) element, Space.EMPTY);
        } else if (element instanceof PyWhileStatement) {
            return mapWhile((PyWhileStatement) element);
        }
        System.err.println("WARNING: unhandled statement of type " + element.getClass().getSimpleName());
        return null;
    }

    private Statement mapReturnStatement(PyReturnStatement element) {
        return new J.Return(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                mapExpression(element.getExpression())
        );
    }

    private Statement mapWhile(PyWhileStatement element) {
        return new J.WhileLoop(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                new J.ControlParentheses<>(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        JRightPadded.build(mapExpression(element.getWhilePart().getCondition()))
                ),
                JRightPadded.build(mapBlock(element.getWhilePart().getStatementList(),
                        whitespaceBefore(findFirstPrevSibling(element.getWhilePart().getStatementList(),
                                e -> e instanceof LeafPsiElement && ((LeafPsiElement) e).getElementType() == PyTokenTypes.COLON))))
        );
    }

    private Statement mapContinueStatement(PyContinueStatement element) {
        return new J.Continue(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                null
        );
    }

    private Statement mapBreakStatement(PyBreakStatement element) {
        return new J.Break(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                null
        );
    }

    private Statement mapForStatement(PyForStatement element) {
        PyForPart forPart = element.getForPart();
        J.VariableDeclarations target;
        if (forPart.getTarget() instanceof PyTupleExpression) {
            target = mapTupleAsVariableDeclarations((PyTupleExpression) forPart.getTarget());
        } else if (forPart.getTarget() instanceof PyTargetExpression) {
            target = mapTargetExpressionAsVariableDeclarations((PyTargetExpression) forPart.getTarget());
        } else {
            System.err.println("WARNING: unhandled for loop target of type " + forPart.getTarget().getClass().getSimpleName());
            return null;
        }

        return new J.ForEachLoop(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                new J.ForEachLoop.Control(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        JRightPadded.build(target)
                                .withAfter(whitespaceBefore(forPart.getTarget().getNextSibling())),
                        JRightPadded.build(mapExpression(forPart.getSource()))
                ),
                JRightPadded.build(mapBlock(forPart.getStatementList(),
                        whitespaceBefore(findFirstPrevSibling(forPart.getStatementList(),
                                e -> e instanceof LeafPsiElement && ((LeafPsiElement) e).getElementType() == PyTokenTypes.COLON))))
        );
    }

    private J.VariableDeclarations mapTargetExpressionAsVariableDeclarations(PyTargetExpression element) {
        return new J.VariableDeclarations(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                emptyList(),
                emptyList(),
                null,
                null,
                emptyList(),
                singletonList(
                        JRightPadded.build(new J.VariableDeclarations.NamedVariable(
                                randomId(),
                                whitespaceBefore(element.getNameIdentifier()),
                                EMPTY,
                                new J.Identifier(
                                        randomId(),
                                        whitespaceBefore(element.getNameIdentifier()),
                                        EMPTY,
                                        requireNonNull(element.getName()),
                                        null,
                                        null
                                ),
                                emptyList(),
                                null,
                                null
                        ))
                )
        );
    }

    private J.VariableDeclarations mapTupleAsVariableDeclarations(PyTupleExpression element) {
        List<JRightPadded<J.VariableDeclarations.NamedVariable>> namedVariables = new ArrayList<>(element.getElements().length);
        PyExpression[] elements = element.getElements();
        for (PyExpression nv : elements) {
            namedVariables.add(JRightPadded.build(new J.VariableDeclarations.NamedVariable(
                    randomId(),
                    whitespaceBefore(nv),
                    EMPTY,
                    mapIdentifier((PsiNamedElement) nv).withPrefix(Space.EMPTY),
                    emptyList(),
                    null,
                    null
            )).withAfter(whitespaceBefore(nv.getNextSibling())));
        }

        return new J.VariableDeclarations(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                emptyList(),
                emptyList(),
                null,
                null,
                emptyList(),
                namedVariables
        );
    }

    private Statement mapMethodDeclaration(PyFunction element) {
        return new J.MethodDeclaration(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                mapDecoratorList(element.getDecoratorList()),
                emptyList(),
                null,
                new J.Empty(
                        Tree.randomId(),
                        whitespaceBefore(findToken(element, PyTokenTypes.DEF_KEYWORD)),
                        EMPTY
                ),
                new J.MethodDeclaration.IdentifierWithAnnotations(
                        mapIdentifier(element).withPrefix(whitespaceBefore(element.getNameIdentifier())),
                        emptyList()
                ),
                JContainer.empty(),
                null,
                mapBlock(element.getStatementList(),
                        whitespaceBefore(findFirstPrevSibling(element.getStatementList(),
                                e -> e instanceof LeafPsiElement && ((LeafPsiElement) e).getElementType() == PyTokenTypes.COLON))),
                null,
                null
        );
    }

    public Statement mapAssignmentStatement(PyAssignmentStatement element) {
        PyExpression pyLhs = element.getLeftHandSideExpression();
        PyExpression pyRhs = element.getAssignedValue();

        J.Identifier lhs = expectIdentifier(mapExpression(pyLhs));
        Expression rhs = mapExpression(pyRhs).withPrefix(whitespaceBefore(pyRhs));

        return new J.Assignment(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                lhs,
                JLeftPadded.build(rhs).withBefore(whitespaceBefore(pyRhs)),
                null
        );
    }

    public Statement mapClassDeclarationStatement(PyClass element) {
        PsiElement classKeyword = findToken(element, PyTokenTypes.CLASS_KEYWORD);
        J.ClassDeclaration.Kind kind = new J.ClassDeclaration.Kind(
                randomId(),
                whitespaceBefore(classKeyword),
                EMPTY,
                emptyList(),
                J.ClassDeclaration.Kind.Type.Class
        );

        JContainer<TypeTree> implementings;
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
        } else {
            implementings = JContainer.empty();
            implementings = implementings.withMarkers(implementings.getMarkers().add(new OmitParentheses(randomId())));
        }

        List<J.Annotation> decorators = mapDecoratorList(element.getDecoratorList());
        if (!decorators.isEmpty()) {
            kind = kind.withAnnotations(decorators);
        }

        Space blockPrefix = Space.EMPTY;
        PsiElement beforeColon = findFirstPrevSibling(element.getStatementList(), e -> e instanceof LeafPsiElement && ((LeafPsiElement) e).getElementType() == PyTokenTypes.COLON)
                .getPrevSibling();
        if ((beforeColon instanceof PyArgumentList && element.getSuperClassExpressionList() == null) || beforeColon instanceof PsiWhiteSpace) {
            blockPrefix = whitespaceBefore(beforeColon);
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
                implementings.withBefore(whitespaceBefore(element.getSuperClassExpressionList())),
                null,
                mapBlock(element.getStatementList(), blockPrefix),
                null
        );
    }

    public J.Annotation mapDecorator(PyDecorator pyDecorator) {
        J.Identifier name = new J.Identifier(
                Tree.randomId(),
                Space.EMPTY,
                EMPTY,
                expectSimpleName(pyDecorator.getQualifiedName()),
                null,
                null
        );

        JContainer<Expression> arguments = mapArgumentList(pyDecorator.getArgumentList());

//        PyArgumentList pyArgumentList = pyDecorator.getArgumentList();
//        if (pyArgumentList != null) {
//            if (pyArgumentList.getArguments().length == 0) {
//                arguments = JContainer.build(singletonList(
//                        JRightPadded.build(
//                                new J.Empty(
//                                        randomId(),
//                                        whitespaceBefore(
//                                                findKeyword(pyArgumentList, PyTokenTypes.RPAR)
//                                        ),
//                                        EMPTY
//                                )
//                        )
//                ));
//            } else {
//                List<JRightPadded<Expression>> expressions = new ArrayList<>(pyArgumentList.getArguments().length);
//                for (PyExpression expression : pyArgumentList.getArguments()) {
//                    expressions.add(JRightPadded.build(mapExpression(expression)));
//                }
//                arguments = JContainer.build(expressions);
//            }
//        }
        return new J.Annotation(
                Tree.randomId(),
                whitespaceBefore(pyDecorator),
                EMPTY,
                name,
                arguments
        );
    }

    public List<J.Annotation> mapDecoratorList(@Nullable PyDecoratorList pyDecoratorList) {
        if (pyDecoratorList == null || pyDecoratorList.getDecorators().length == 0) {
            return emptyList();
        }
        PyDecorator[] pyDecorators = pyDecoratorList.getDecorators();
        List<J.Annotation> decorators = new ArrayList<>(pyDecorators.length);
        for (PyDecorator pyDecorator : pyDecorators) {
            decorators.add(mapDecorator(pyDecorator));
        }
        return decorators;
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
                new J.ControlParentheses<>(
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
                    EMPTY,
                    new J.ControlParentheses<>(
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
                    EMPTY,
                    JRightPadded.build(nestedIf)
            );
        } else if (parent.getElsePart() != null) {
            PyStatementList pyElseBody = parent.getElsePart().getStatementList();
            return new J.If.Else(
                    randomId(),
                    whitespaceBefore(parent.getElsePart()),
                    EMPTY,
                    JRightPadded.<Statement>build(mapBlock(pyElseBody,
                                    whitespaceBefore(findFirstPrevSibling(parent.getElsePart().getStatementList(),
                                            e -> e instanceof LeafPsiElement && ((LeafPsiElement) e).getElementType() == PyTokenTypes.COLON))))
                            .withAfter(whitespaceAfter(pyElseBody))
            );
        } else {
            return null;
        }
    }

    public Py.PassStatement mapPassStatement(PyPassStatement element) {
        return new Py.PassStatement(
                randomId(),
                whitespaceBefore(element),
                EMPTY
        );
    }

    public J.Block mapBlock(PyStatementList element, Space blockPrefix) {
        PyStatement[] pyStatements = element.getStatements();
        List<JRightPadded<Statement>> statements = new ArrayList<>(pyStatements.length);
        for (PyStatement pyStatement : pyStatements) {
            Statement statement = mapStatement(pyStatement);
            statements.add(JRightPadded.build(statement).withAfter(whitespaceAfter(pyStatement)));
        }
        return new J.Block(
                randomId(),
                blockPrefix,
                EMPTY,
                JRightPadded.build(false),
                ListUtils.mapFirst(statements, first -> first.withElement(first.getElement().withPrefix(whitespaceBefore(element)))),
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
        } else if (element instanceof PyDictLiteralExpression) {
            return mapDictLiteralExpression((PyDictLiteralExpression) element);
        } else if (element instanceof PyKeyValueExpression) {
            return mapKeyValueExpression((PyKeyValueExpression) element);
        } else if (element instanceof PyKeywordArgument) {
            return mapKeywordArgument((PyKeywordArgument) element);
        } else if (element instanceof PyListLiteralExpression) {
            return mapListLiteral((PyListLiteralExpression) element);
        } else if (element instanceof PyNumericLiteralExpression) {
            return mapNumericLiteral((PyNumericLiteralExpression) element);
        } else if (element instanceof PyParenthesizedExpression) {
            return mapParenthesizedExpression((PyParenthesizedExpression) element);
        } else if (element instanceof PyPrefixExpression) {
            return mapPrefixExpression((PyPrefixExpression) element);
        } else if (element instanceof PyReferenceExpression) {
            return mapReferenceExpression((PyReferenceExpression) element);
        } else if (element instanceof PySubscriptionExpression) {
            return mapSubscription((PySubscriptionExpression) element);
        } else if (element instanceof PyStringLiteralExpression) {
            return mapStringLiteral((PyStringLiteralExpression) element);
        } else if (element instanceof PyTargetExpression) {
            return mapIdentifier((PyTargetExpression) element);
        }
        System.err.println("WARNING: unhandled expression of type " + element.getClass().getSimpleName());
        return null;
    }

    private Expression mapDictLiteralExpression(PyDictLiteralExpression element) {
        List<JRightPadded<Py.KeyValue>> elements = new ArrayList<>(element.getElements().length);
        for (PyKeyValueExpression e : element.getElements()) {
            elements.add(JRightPadded.build(mapKeyValueExpression(e)).withAfter(whitespaceAfter(e)));
        }
        return new Py.DictLiteral(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                JContainer.build(elements),
                null
        );
    }

    private Py.KeyValue mapKeyValueExpression(PyKeyValueExpression element) {
        return new Py.KeyValue(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                JRightPadded.build(mapExpression(element.getKey())).withAfter(whitespaceAfter(element.getKey())),
                mapExpression(element.getValue()),
                null
        );
    }

    private Expression mapListLiteral(PyListLiteralExpression element) {
        List<JRightPadded<Expression>> exprs = new ArrayList<>(element.getElements().length);
        for (PyExpression pyExpression : element.getElements()) {
            exprs.add(JRightPadded.build(mapExpression(pyExpression))
                    .withAfter(whitespaceAfter(pyExpression)));
        }
        return new J.NewArray(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                null,
                emptyList(),
                JContainer.build(exprs),
                null
        );
    }

    private Expression mapKeywordArgument(PyKeywordArgument element) {
        return new J.Assignment(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                new J.Identifier(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        requireNonNull(element.getKeyword()),
                        null,
                        null
                ),
                JLeftPadded.build(mapExpression(element.getValueExpression()))
                        .withBefore(whitespaceBefore(element.getValueExpression())),
                null
        );
    }

    private Expression mapParenthesizedExpression(PyParenthesizedExpression element) {
        return new J.Parentheses<>(
                randomId(),
                whitespaceBefore(element),
                EMPTY,
                JRightPadded.build(mapExpression(element.getContainedExpression()))
                        .withAfter(whitespaceAfter(element.getContainedExpression()))
        );
    }

    public J.Binary mapBinaryExpression(PyBinaryExpression element) {
        Expression lhs = mapExpression(element.getLeftExpression());
        Expression rhs = mapExpression(element.getRightExpression());
        Space beforeOperatorSpace = whitespaceAfter(element.getLeftExpression());

        J.Binary.Type operatorType;
        PyElementType pyOperatorType = element.getOperator();
        if (pyOperatorType == PyTokenTypes.LT) {
            operatorType = J.Binary.Type.LessThan;
        } else if (pyOperatorType == PyTokenTypes.LE) {
            operatorType = J.Binary.Type.LessThanOrEqual;
        } else if (pyOperatorType == PyTokenTypes.GT) {
            operatorType = J.Binary.Type.GreaterThan;
        } else if (pyOperatorType == PyTokenTypes.GE) {
            operatorType = J.Binary.Type.GreaterThanOrEqual;
        } else if (pyOperatorType == PyTokenTypes.EQEQ) {
            operatorType = J.Binary.Type.Equal;
        } else if (pyOperatorType == PyTokenTypes.NE) {
            operatorType = J.Binary.Type.NotEqual;
        } else if (pyOperatorType == PyTokenTypes.DIV) {
            operatorType = J.Binary.Type.Division;
        } else if (pyOperatorType == PyTokenTypes.MINUS) {
            operatorType = J.Binary.Type.Subtraction;
        } else if (pyOperatorType == PyTokenTypes.MULT) {
            operatorType = J.Binary.Type.Multiplication;
        } else if (pyOperatorType == PyTokenTypes.PLUS) {
            operatorType = J.Binary.Type.Addition;
        } else if (pyOperatorType == PyTokenTypes.OR_KEYWORD) {
            operatorType = J.Binary.Type.Or;
        } else if (pyOperatorType == PyTokenTypes.AND_KEYWORD) {
            operatorType = J.Binary.Type.And;
        } else {
            System.err.println("WARNING: unhandled binary operator type " + pyOperatorType);
            return null;
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
        } else if (op == PyTokenTypes.TILDE) {
            ot = J.Unary.Type.Complement;
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

    public JContainer<Expression> mapArgumentList(@Nullable PyArgumentList pyArgumentList) {
        if (pyArgumentList == null) {
            return null;
        }

        if (pyArgumentList.getArguments().length == 0) {
            return JContainer.build(singletonList(
                    JRightPadded.build(
                            new J.Empty(
                                    Tree.randomId(),
                                    whitespaceBefore(findToken(pyArgumentList, PyTokenTypes.RPAR)),
                                    EMPTY
                            )
                    )
            ));
        } else {
            List<JRightPadded<Expression>> expressions = new ArrayList<>(
                    pyArgumentList.getArguments().length
            );
            for (PyExpression arg : pyArgumentList.getArguments()) {
                expressions.add(
                        new JRightPadded<>(
                                mapExpression(arg).withPrefix(whitespaceBefore(arg)),
                                whitespaceAfter(arg),
                                EMPTY
                        )
                );
            }
            return JContainer.build(expressions);
        }
    }

    public J.MethodInvocation mapCallExpression(PyCallExpression element) {
        PyExpression pyCallee = element.getCallee();
        if (pyCallee instanceof PyReferenceExpression) {
            // e.g. `print(42)`
            PyReferenceExpression pyRefExpression = (PyReferenceExpression) pyCallee;
            J.Identifier functionName = mapReferenceExpression(pyRefExpression);

            return new J.MethodInvocation(
                    randomId(),
                    whitespaceBefore(element),
                    EMPTY,
                    null,
                    null,
                    functionName,
                    mapArgumentList(element.getArgumentList()),
                    null
            );
        } else {
            System.err.println("WARNING: unhandled call expression; callee is not a reference");
        }
        return null;
    }

    public Py.ExpressionStatement mapExpressionStatement(PyExpressionStatement element) {
        Expression expression = mapExpression(element.getExpression());
        return new Py.ExpressionStatement(randomId(), expression);
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

    public J.Identifier mapIdentifier(PsiNamedElement element) {
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

    private String expectSimpleName(QualifiedName qualifiedName) {
        if (qualifiedName.getComponentCount() != 1) {
            throw new UnsupportedOperationException("only simple names are supported; found: " + qualifiedName.toString());
        }
        return qualifiedName.getLastComponent();
    }

    private static Space whitespaceBefore(@Nullable PsiElement element) {
        if (element == null) {
            return Space.EMPTY;
        } else if (element instanceof PsiWhiteSpace) {
            return Space.build(element.getText(), emptyList());
        }

        PsiElement previous = element.getPrevSibling();
        if (previous == null) {
            return Space.EMPTY;
        }
        if (previous instanceof PsiWhiteSpace) {
            return Space.build(previous.getText(), emptyList());
        }

        return Space.EMPTY;
    }

    private static Space whitespaceAfter(@Nullable PsiElement element) {
        if (element == null) {
            return Space.EMPTY;
        } else if (element instanceof PsiWhiteSpace) {
            return Space.build(element.getText(), emptyList());
        }

        PsiElement previous = element.getNextSibling();
        if (previous == null) {
            return Space.EMPTY;
        }
        if (previous instanceof PsiWhiteSpace) {
            return Space.build(previous.getText(), emptyList());
        }

        return Space.EMPTY;
    }

    private static PsiElement findFirstPrevSibling(PsiElement element, Predicate<PsiElement> match) {
        PsiElement prev = element.getPrevSibling();
        while (prev != null) {
            if (match.test(prev)) {
                return prev;
            }
            prev = prev.getPrevSibling();
        }
        throw new IllegalStateException("Expected to find a previous sibling match but found none");
    }

    private static @Nullable PsiElement findToken(PsiElement parent, PyElementType elementType) {
        ASTNode node = parent.getNode().findChildByType(elementType);
        if (node == null) {
            return null;
        }
        return node.getPsi();
    }
}
