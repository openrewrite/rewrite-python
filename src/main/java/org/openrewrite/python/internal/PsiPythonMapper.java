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
import com.intellij.psi.PsiComment;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiNamedElement;
import com.intellij.psi.PsiWhiteSpace;
import com.intellij.psi.util.QualifiedName;
import com.jetbrains.python.PyTokenTypes;
import com.jetbrains.python.psi.*;
import org.openrewrite.FileAttributes;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.marker.OmitParentheses;
import org.openrewrite.java.tree.*;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.marker.BuiltinDesugar;
import org.openrewrite.python.marker.ImplicitNone;
import org.openrewrite.python.marker.MagicMethodDesugar;
import org.openrewrite.python.tree.Py;
import org.openrewrite.python.tree.PyComment;

import java.nio.file.Path;
import java.util.*;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static java.util.Objects.requireNonNull;
import static org.openrewrite.Tree.randomId;
import static org.openrewrite.marker.Markers.EMPTY;
import static org.openrewrite.python.internal.PsiUtils.*;

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
        } else if (element instanceof PyFromImportStatement) {
            return mapFromImportStatement((PyFromImportStatement) element);
        } else if (element instanceof PyFunction) {
            return mapMethodDeclaration((PyFunction) element);
        } else if (element instanceof PyIfStatement) {
            return mapIfStatement((PyIfStatement) element);
        } else if (element instanceof PyImportStatement) {
            return mapImportStatement((PyImportStatement) element);
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

    private J.Import mapImportElements(PyImportStatementBase element, @Nullable Expression importSource) {
        if (element.getImportElements().length != 1) {
            throw new UnsupportedOperationException("no support for multi-import statements yet");
        }
        PyImportElement pyImportElement = element.getImportElements()[0];

        PsiElement importKeyword = findChildToken(element, PyTokenTypes.IMPORT_KEYWORD);

        Expression importNameExpr = mapExpression(requireNonNull(pyImportElement.getImportReferenceExpression()));
        if (!(importNameExpr instanceof J.Identifier)) {
            throw new UnsupportedOperationException("no support for qualified import targets in imports");
        }
        //  from math import ceil      or      import ceil
        //                  ^^^^^                    ^^^^^
        J.Identifier importName = (J.Identifier) importNameExpr.withPrefix(spaceAfter(importKeyword));


        J.FieldAccess fieldAccess;
        if (importSource == null) {
            fieldAccess = new J.FieldAccess(
                    randomId(),
                    Space.EMPTY,
                    EMPTY,
                    importName,
                    JLeftPadded.build(
                                    new J.Identifier(randomId(), Space.EMPTY, EMPTY, "", null, null)
                            )
                            .withBefore(spaceBefore(importKeyword)),
                    null
            );
        } else {
            fieldAccess = new J.FieldAccess(
                    randomId(),
                    Space.EMPTY,
                    EMPTY,
                    importSource,
                    JLeftPadded.build(importName)
                            .withBefore(spaceBefore(importKeyword)),
                    null
            );
        }

        PyTargetExpression pyAlias = pyImportElement.getAsNameElement();
        JLeftPadded<J.Identifier> alias = null;
        if (pyAlias != null) {
            PsiElement asKeyword = findChildToken(pyImportElement, PyTokenTypes.AS_KEYWORD);
            J.Identifier aliasId = expectIdentifier(mapExpression(pyAlias));
            alias = JLeftPadded.build(
                    aliasId.withPrefix(spaceAfter(asKeyword))
            ).withBefore(spaceBefore(asKeyword));
        }

        return new J.Import(
                randomId(),
                spaceBefore(element),
                EMPTY,
                JLeftPadded.build(false),
                fieldAccess,
                alias
        );
    }

    private J.Import mapImportStatement(PyImportStatement element) {
        return mapImportElements(element, null);
    }

    private J.Import mapFromImportStatement(PyFromImportStatement element) {
        if (element.getImportElements().length != 1) {
            throw new UnsupportedOperationException("no support for multi-import statements yet");
        }
        PsiElement fromKeyword = findChildToken(element, PyTokenTypes.FROM_KEYWORD);
        Expression fromModuleExpr = element.getImportSource() == null ? null : mapReferenceExpression(element.getImportSource());

        Expression fromModuleDots = null;
        int relativeLevel = element.getRelativeLevel();
        if (fromModuleExpr == null) {
            relativeLevel++;
        }
        for (int i = 0; i < relativeLevel; i++) {
            if (fromModuleDots == null) {
                fromModuleDots = new J.Empty(randomId(), Space.EMPTY, EMPTY);
            } else {
                fromModuleDots = new J.FieldAccess(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        fromModuleDots,
                        JLeftPadded.build(
                                new J.Identifier(randomId(), Space.EMPTY, EMPTY, "", null, null)
                        ),
                        null
                );
            }
        }

        //  from math import ceil
        //      ^^^^^
        Expression importSource;
        if (fromModuleDots == null && fromModuleExpr == null) {
            throw new IllegalStateException("attempting to map import with no source");
        }
        if (fromModuleDots != null && fromModuleExpr == null) {
            importSource = fromModuleDots;
        } else if (fromModuleDots == null) {
            importSource = fromModuleExpr;
        } else {
            importSource = fromModuleDots;
            Stack<J.FieldAccess> fieldAccessStack = new Stack<>();
            J.Identifier originalTarget = null;
            while (originalTarget == null) {
                if (fromModuleExpr instanceof J.FieldAccess) {
                    J.FieldAccess fieldAccess = (J.FieldAccess) fromModuleExpr;
                    fieldAccessStack.add(fieldAccess);
                    fromModuleExpr = fieldAccess.getTarget();
                } else if (fromModuleExpr instanceof J.Identifier) {
                    originalTarget = (J.Identifier) fromModuleExpr;
                } else {
                    throw new IllegalStateException(String.format(
                            "didn't expect a %s in an import qualifier",
                            fromModuleExpr.getClass()
                    ));
                }
            }
            importSource = new J.FieldAccess(
                    randomId(),
                    Space.EMPTY,
                    EMPTY,
                    importSource,
                    JLeftPadded.build(originalTarget),
                    null
            );
            while (!fieldAccessStack.isEmpty()) {
                J.FieldAccess oldFieldAccess = fieldAccessStack.pop();
                importSource = oldFieldAccess.withTarget(importSource);
            }
        }
        importSource = importSource.withPrefix(spaceAfter(fromKeyword));


        return mapImportElements(element, importSource);
    }

    private Statement mapReturnStatement(PyReturnStatement element) {
        return new J.Return(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpression(element.getExpression())
        );
    }

    private Statement mapWhile(PyWhileStatement element) {
        return new J.WhileLoop(
                randomId(),
                spaceBefore(element),
                EMPTY,
                new J.ControlParentheses<>(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        JRightPadded.build(mapExpression(element.getWhilePart().getCondition()))
                ),
                JRightPadded.build(mapCompoundBlock(element.getWhilePart()))
        );
    }

    private Statement mapContinueStatement(PyContinueStatement element) {
        return new J.Continue(
                randomId(),
                spaceBefore(element),
                EMPTY,
                null
        );
    }

    private Statement mapBreakStatement(PyBreakStatement element) {
        return new J.Break(
                randomId(),
                spaceBefore(element),
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
                spaceBefore(element),
                EMPTY,
                new J.ForEachLoop.Control(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        JRightPadded.build(target)
                                .withAfter(spaceAfter(forPart.getTarget())),
                        JRightPadded.build(mapExpression(forPart.getSource()))
                ),
                JRightPadded.build(mapCompoundBlock(forPart))
        );
    }

    private J.VariableDeclarations mapTargetExpressionAsVariableDeclarations(PyTargetExpression element) {
        return new J.VariableDeclarations(
                randomId(),
                spaceBefore(element),
                EMPTY,
                emptyList(),
                emptyList(),
                null,
                null,
                emptyList(),
                singletonList(
                        JRightPadded.build(new J.VariableDeclarations.NamedVariable(
                                randomId(),
                                spaceBefore(element.getNameIdentifier()),
                                EMPTY,
                                expectIdentifier(element.getNameIdentifier()),
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
                    spaceBefore(nv),
                    EMPTY,
                    mapIdentifier((PsiNamedElement) nv).withPrefix(Space.EMPTY),
                    emptyList(),
                    null,
                    null
            )).withAfter(spaceBefore(nv.getNextSibling())));
        }

        return new J.VariableDeclarations(
                randomId(),
                spaceBefore(element),
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
                spaceBefore(element),
                EMPTY,
                mapDecoratorList(element.getDecoratorList()),
                emptyList(),
                null,
                new J.Empty(
                        randomId(),
                        spaceBefore(maybeFindChildToken(element, PyTokenTypes.DEF_KEYWORD)),
                        EMPTY
                ),
                new J.MethodDeclaration.IdentifierWithAnnotations(
                        mapIdentifier(element).withPrefix(spaceBefore(element.getNameIdentifier())),
                        emptyList()
                ),
                JContainer.empty(),
                null,
                mapCompoundBlock(element),
                null,
                null
        );
    }

    public Statement mapAssignmentStatement(PyAssignmentStatement element) {
        PyExpression pyLhs = element.getLeftHandSideExpression();
        PyExpression pyRhs = element.getAssignedValue();

        J.Identifier lhs = expectIdentifier(mapExpression(pyLhs));
        Expression rhs = mapExpression(pyRhs).withPrefix(spaceBefore(pyRhs));

        return new J.Assignment(
                randomId(),
                spaceBefore(element),
                EMPTY,
                lhs,
                JLeftPadded.build(rhs).withBefore(spaceBefore(pyRhs)),
                null
        );
    }

    public Statement mapClassDeclarationStatement(PyClass element) {
        PsiElement classKeyword = maybeFindChildToken(element, PyTokenTypes.CLASS_KEYWORD);
        J.ClassDeclaration.Kind kind = new J.ClassDeclaration.Kind(
                randomId(),
                spaceBefore(classKeyword),
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
                    superClasses.add(
                            JRightPadded.<TypeTree>build(
                                            mapReferenceExpression((PyReferenceExpression) superClass)
                                                    .withPrefix(spaceBefore(superClass))
                                    )
                                    .withAfter(spaceAfter(superClass))
                    );
                }
                implementings = JContainer.build(superClasses);
            } else {
                implementings = JContainer.build(singletonList(
                        JRightPadded.build(
                                new J.Empty(
                                        randomId(),
                                        spaceBefore(pyClassBase.getNode().getLastChildNode().getPsi()),
                                        EMPTY
                                )
                        )));
            }
        } else {
            implementings = JContainer.empty();
            implementings = implementings.withMarkers(
                    implementings.getMarkers().add(new OmitParentheses(randomId()))
            );
        }

        List<J.Annotation> decorators = mapDecoratorList(element.getDecoratorList());
        if (!decorators.isEmpty()) {
            kind = kind.withAnnotations(decorators);
        }

        return new J.ClassDeclaration(
                randomId(),
                spaceBefore(element),
                EMPTY,
                emptyList(),
                emptyList(),
                kind,
                expectIdentifier(element.getNameNode()),
                null,
                null,
                null,
                implementings.withBefore(spaceBefore(element.getSuperClassExpressionList())),
                null,
                mapCompoundBlock(element),
                null
        );
    }

    public J.Annotation mapDecorator(PyDecorator pyDecorator) {
        J.Identifier name = new J.Identifier(
                randomId(),
                Space.EMPTY,
                EMPTY,
                expectSimpleName(pyDecorator.getQualifiedName()),
                null,
                null
        );

        JContainer<Expression> arguments = mapArgumentList(pyDecorator.getArgumentList());

        return new J.Annotation(
                randomId(),
                spaceBefore(pyDecorator),
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

        Statement ifBody = mapStatement(pyIfBody);
        J.If.Else elsePart = mapElsePart(element, 0);

        return new J.If(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpressionAsControlParentheses(pyIfCondition),
                JRightPadded.build(ifBody).withAfter(spaceAfter(pyIfBody)),
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

            Statement ifBody = mapStatement(pyIfBody);

            J.If nestedIf = new J.If(
                    randomId(),
                    Space.EMPTY,
                    EMPTY,
                    mapExpressionAsControlParentheses(pyIfCondition),
                    JRightPadded.build(ifBody).withAfter(spaceAfter(pyIfBody)),
                    mapElsePart(parent, elifIndex + 1)
            );
            return new J.If.Else(
                    randomId(),
                    spaceBefore(pyElifPart),
                    EMPTY,
                    JRightPadded.build(nestedIf)
            );
        } else if (parent.getElsePart() != null) {
            return new J.If.Else(
                    randomId(),
                    spaceBefore(parent.getElsePart()),
                    EMPTY,
                    mapRightPaddedCompoundBlock(parent.getElsePart())
            );
        } else {
            return null;
        }
    }

    public Py.PassStatement mapPassStatement(PyPassStatement element) {
        return new Py.PassStatement(
                randomId(),
                spaceBefore(element),
                EMPTY
        );
    }

    public J.Block mapBlock(PyStatementList element, Space blockPrefix) {
        PyStatement[] pyStatements = element.getStatements();
        List<JRightPadded<Statement>> statements = new ArrayList<>(pyStatements.length);

        Space nextPrefix = spaceBefore(element);
        for (PyStatement pyStatement : pyStatements) {
            Statement statement = mapStatement(pyStatement).withPrefix(nextPrefix);
            // the PSI model stores end-of-line comments as *children* of the statement
            Space trailingSpace = trailingSpace(pyStatement);
            statements.add(JRightPadded.build(statement).withAfter(trailingSpace));
            nextPrefix = spaceAfter(pyStatement);
        }

        return new J.Block(
                randomId(),
                blockPrefix,
                EMPTY,
                JRightPadded.build(false),
                statements,
                spaceAfter(element)
        );
    }

    /**
     * Maps the statement list of a Python "compound block" as a J.Block.
     * <p>
     * Python's compound blocks are those that have colons followed by an indented block of statements.
     * The returned J.Block represents these statements, as well as the preceding colon and its prefix space.
     * <p>
     * In general, if you want to map the body of a compound block, use this method.
     */
    public J.Block mapCompoundBlock(PyStatementListContainer pyElement) {
        return mapBlock(
                pyElement.getStatementList(),
                spaceBefore(
                        findPreviousSiblingToken(pyElement.getStatementList(), PyTokenTypes.COLON)
                )
        );
    }

    /**
     * Like {@link #mapCompoundBlock}, but also consumes space following with element's statement list.
     */
    public JRightPadded<Statement> mapRightPaddedCompoundBlock(PyStatementListContainer pyElement) {
        return JRightPadded.<Statement>build(mapBlock(
                pyElement.getStatementList(),
                spaceBefore(
                        findPreviousSiblingToken(pyElement.getStatementList(), PyTokenTypes.COLON)
                )
        )).withAfter(spaceAfter(pyElement));
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
        } else if (element instanceof PyNoneLiteralExpression) {
            return mapNoneLiteral((PyNoneLiteralExpression) element);
        } else if (element instanceof PyNumericLiteralExpression) {
            return mapNumericLiteral((PyNumericLiteralExpression) element);
        } else if (element instanceof PyParenthesizedExpression) {
            return mapParenthesizedExpression((PyParenthesizedExpression) element);
        } else if (element instanceof PyPrefixExpression) {
            return mapPrefixExpression((PyPrefixExpression) element);
        } else if (element instanceof PyReferenceExpression) {
            return mapReferenceExpression((PyReferenceExpression) element);
        } else if (element instanceof PySetLiteralExpression) {
            return mapSetLiteral((PySetLiteralExpression) element);
        } else if (element instanceof PySliceExpression) {
            return mapSliceExpression((PySliceExpression) element);
        } else if (element instanceof PySubscriptionExpression) {
            return mapSubscription((PySubscriptionExpression) element);
        } else if (element instanceof PyStringLiteralExpression) {
            return mapStringLiteral((PyStringLiteralExpression) element);
        } else if (element instanceof PyTargetExpression) {
            return mapIdentifier((PyTargetExpression) element);
        } else if (element instanceof PyTupleExpression) {
            return mapTupleLiteral((PyTupleExpression) element);
        }
        System.err.println("WARNING: unhandled expression of type " + element.getClass().getSimpleName());
        return null;
    }

    /**
     * Wraps an expression in J.ControlParentheses, which are used in J.If, J.While, etc.
     * <p>
     * Consumes the space on both sides of the expression.
     */
    private J.ControlParentheses<Expression> mapExpressionAsControlParentheses(PyExpression pyExpression) {
        return new J.ControlParentheses<>(
                randomId(),
                Space.EMPTY,
                EMPTY,
                mapExpressionAsRightPadded(pyExpression)
        );
    }

    /**
     * Wraps an expression in JRightPadded, consuming space on both sides of the expression.
     */
    private JRightPadded<Expression> mapExpressionAsRightPadded(PyExpression pyExpression) {
        Expression expression = mapExpression(pyExpression);
        return JRightPadded.build(expression).withAfter(spaceAfter(pyExpression));
    }

    private Expression mapDictLiteralExpression(PyDictLiteralExpression element) {
        List<JRightPadded<Py.KeyValue>> elements = new ArrayList<>(element.getElements().length);
        for (PyKeyValueExpression e : element.getElements()) {
            elements.add(JRightPadded.build(mapKeyValueExpression(e)).withAfter(spaceAfter(e)));
        }
        return new Py.DictLiteral(
                randomId(),
                spaceBefore(element),
                EMPTY,
                JContainer.build(elements),
                null
        );
    }

    private Py.KeyValue mapKeyValueExpression(PyKeyValueExpression element) {
        return new Py.KeyValue(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpressionAsRightPadded(element.getKey()),
                mapExpression(element.getValue()),
                null
        );
    }

    private Expression mapSequenceExpressionAsArray(PySequenceExpression element) {
        List<JRightPadded<Expression>> exprs;
        if (element.getElements().length == 0) {
            Space space = Space.EMPTY;
            if (element.getNode().getChildren(null).length > 0) {
                PsiElement lastChild = element.getNode().getLastChildNode().getPsi();
                if (lastChild instanceof PsiWhiteSpace) {
                    space = trailingSpace(element);
                } else {
                    space = spaceBefore(lastChild);
                }
            }
            exprs = singletonList(JRightPadded.<Expression>build(
                    new J.Empty(randomId(), Space.EMPTY, EMPTY)
            ).withAfter(space));
        } else {
            exprs = new ArrayList<>(element.getElements().length);
            for (PyExpression pyExpression : element.getElements()) {
                exprs.add(mapExpressionAsRightPadded(pyExpression));
            }
        }
        return new J.NewArray(
                randomId(),
                spaceBefore(element),
                EMPTY,
                null,
                emptyList(),
                JContainer.build(exprs),
                null
        );
    }

    private Expression mapListLiteral(PyListLiteralExpression element) {
        return mapSequenceExpressionAsArray(element);
    }

    private Expression mapSetLiteral(PySetLiteralExpression element) {
        J.Identifier builtins = makeBuiltinsIdentifier();
        JContainer<Expression> args = JContainer.build(singletonList(
                JRightPadded.build(mapSequenceExpressionAsArray(element))
        )).withBefore(spaceBefore(element));
        return new J.MethodInvocation(
                randomId(),
                Space.EMPTY,
                Markers.build(singletonList(new BuiltinDesugar(randomId()))),
                JRightPadded.build(builtins),
                null,
                new J.Identifier(randomId(), Space.EMPTY, EMPTY, "set", null, null),
                args,
                null
        );
    }

    private Expression mapTupleLiteral(PyTupleExpression element) {
        J.Identifier builtins = makeBuiltinsIdentifier();
        JContainer<Expression> args = JContainer.build(singletonList(
                JRightPadded.build(mapSequenceExpressionAsArray(element))
        )).withBefore(spaceBefore(element));
        return new J.MethodInvocation(
                randomId(),
                Space.EMPTY,
                Markers.build(singletonList(new BuiltinDesugar(randomId()))),
                JRightPadded.build(builtins),
                null,
                new J.Identifier(randomId(), Space.EMPTY, EMPTY, "tuple", null, null),
                args,
                null
        );
    }

    private Expression mapKeywordArgument(PyKeywordArgument element) {
        return new J.Assignment(
                randomId(),
                spaceBefore(element),
                EMPTY,
                expectIdentifier(element.getKeywordNode()),
                JLeftPadded.build(mapExpression(requireNonNull(element.getValueExpression())))
                        .withBefore(spaceAfter(element.getKeywordNode().getPsi())),
                null
        );
    }

    private Expression mapParenthesizedExpression(PyParenthesizedExpression element) {
        if (element.getContainedExpression() instanceof PyTupleExpression) {
            return mapTupleLiteral((PyTupleExpression) element.getContainedExpression())
                    .withPrefix(spaceBefore(element));
        }
        return new J.Parentheses<>(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpressionAsRightPadded(requireNonNull(element.getContainedExpression()))
        );
    }

    private static final Map<PyElementType, String> binaryOperatorSpecialMethods;

    static {
        Map<PyElementType, String> map = new HashMap<>();
        map.put(PyTokenTypes.EQEQ, "__eq__");
        map.put(PyTokenTypes.NE, "__ne__");
        map.put(PyTokenTypes.IN_KEYWORD, "__contains__");
        binaryOperatorSpecialMethods = Collections.unmodifiableMap(map);
    }

    private static final Map<PyElementType, J.Binary.Type> binaryOperatorMapping;

    static {
        Map<PyElementType, J.Binary.Type> map = new HashMap<>();
        map.put(PyTokenTypes.LT, J.Binary.Type.LessThan);
        map.put(PyTokenTypes.LE, J.Binary.Type.LessThanOrEqual);
        map.put(PyTokenTypes.GT, J.Binary.Type.GreaterThan);
        map.put(PyTokenTypes.GE, J.Binary.Type.GreaterThanOrEqual);
        map.put(PyTokenTypes.IS_KEYWORD, J.Binary.Type.Equal);
        map.put(PyTokenTypes.DIV, J.Binary.Type.Division);
        map.put(PyTokenTypes.MINUS, J.Binary.Type.Subtraction);
        map.put(PyTokenTypes.MULT, J.Binary.Type.Multiplication);
        map.put(PyTokenTypes.PLUS, J.Binary.Type.Addition);
        map.put(PyTokenTypes.OR_KEYWORD, J.Binary.Type.Or);
        map.put(PyTokenTypes.AND_KEYWORD, J.Binary.Type.And);
        binaryOperatorMapping = Collections.unmodifiableMap(map);
    }

    public Expression mapBinaryExpression(PyBinaryExpression element) {
        // if there are multiple tokens in the operator, `psiOperator` is just the *first* one
        PsiElement psiOperator = requireNonNull(element.getPsiOperator());
        if (matchesTokenSequence(psiOperator, PyTokenTypes.IS_KEYWORD, PyTokenTypes.NOT_KEYWORD)) {
            return mapBinaryExpressionAsOperator(element, J.Binary.Type.NotEqual);
        } else if (matchesTokenSequence(psiOperator, PyTokenTypes.NOT_KEYWORD, PyTokenTypes.IN_KEYWORD)) {
            // a very special case, as there is no magic method for "not in"
            // instead, wrap the "in" expression in a "not"
            Expression containsMethodCall =
                    mapBinaryExpressionAsMagicMethod(element, "__contains__").withPrefix(Space.EMPTY);
            return new J.Unary(
                    randomId(),
                    spaceBefore(element),
                    Markers.build(singletonList(new MagicMethodDesugar(randomId()))),
                    JLeftPadded.build(J.Unary.Type.Not),
                    new J.Parentheses<>(
                            randomId(),
                            Space.EMPTY,
                            EMPTY,
                            JRightPadded.build(containsMethodCall)
                    ),
                    null
            );
        }

        // TODO check that the operator is exactly one token long

        PyElementType pyOperatorType = element.getOperator();

        J.Binary.Type operatorType = binaryOperatorMapping.get(pyOperatorType);
        if (operatorType != null) {
            return mapBinaryExpressionAsOperator(element, operatorType);
        }

        String magicMethod = binaryOperatorSpecialMethods.get(pyOperatorType);
        if (magicMethod != null) {
            return mapBinaryExpressionAsMagicMethod(element, magicMethod);
        }

        throw new IllegalArgumentException("unsupported binary operator type " + pyOperatorType);
    }

    public Expression mapBinaryExpressionAsOperator(PyBinaryExpression element, J.Binary.Type operatorType) {
        PyExpression lhs = requireNonNull(element.getLeftExpression());
        PyExpression rhs = requireNonNull(element.getRightExpression());
        Space beforeOperatorSpace = spaceAfter(element.getLeftExpression());

        return new J.Binary(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpression(lhs),
                JLeftPadded.build(operatorType).withBefore(beforeOperatorSpace),
                mapExpression(rhs),
                null
        );
    }

    public Expression mapBinaryExpressionAsMagicMethod(PyBinaryExpression element, String magicMethod) {
        boolean isReversed = PythonOperatorLookup.doesMagicMethodReverseOperands(magicMethod);
        PyExpression originalLhs = element.getLeftExpression();
        PyExpression originalRhs = element.getRightExpression();

        PyExpression pyLhs = requireNonNull(isReversed ? element.getRightExpression() : element.getLeftExpression());
        PyExpression pyRhs = requireNonNull(element.getOppositeExpression(pyLhs));

        // The space around the operator is "owned" by the operator, regardless of where it came from.
        Space beforeOperator = spaceAfter(originalLhs);
        Space afterOperator = spaceBefore(originalRhs);

        Expression lhs = mapExpression(pyLhs).withPrefix(Space.EMPTY);
        Expression rhs = mapExpression(pyRhs).withPrefix(afterOperator);

        JRightPadded<Expression> paddedLhs = JRightPadded.build(lhs).withAfter(beforeOperator);
        JRightPadded<Expression> paddedRhs = JRightPadded.build(rhs);

        return new J.MethodInvocation(
                randomId(),
                spaceBefore(element),
                Markers.build(singletonList(new MagicMethodDesugar(randomId()))),
                paddedLhs,
                null,
                new J.Identifier(randomId(), Space.EMPTY, EMPTY, magicMethod, null, null),
                JContainer.build(
                        Space.EMPTY,
                        singletonList(paddedRhs),
                        EMPTY
                ),
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
                spaceBefore(element),
                EMPTY,
                JLeftPadded.build(ot),
                mapExpression(element.getOperand()),
                type
        );
    }

    public J.Literal mapBooleanLiteral(PyBoolLiteralExpression element) {
        return new J.Literal(
                randomId(),
                spaceBefore(element),
                EMPTY,
                element.getValue(),
                element.getText(),
                emptyList(),
                JavaType.Primitive.Boolean
        );
    }

    public J.Literal mapNoneLiteral(PyNoneLiteralExpression element) {
        return new J.Literal(
                randomId(),
                spaceBefore(element),
                EMPTY,
                null,
                "null",
                null,
                JavaType.Primitive.Null
        );
    }

    public @Nullable JContainer<Expression> mapArgumentList(@Nullable PyArgumentList pyArgumentList) {
        if (pyArgumentList == null) {
            return null;
        }

        if (pyArgumentList.getArguments().length == 0) {
            return JContainer.<Expression>build(singletonList(
                    JRightPadded.build(
                            new J.Empty(
                                    randomId(),
                                    spaceBefore(maybeFindChildToken(pyArgumentList, PyTokenTypes.RPAR)),
                                    EMPTY
                            )
                    )
            )).withBefore(spaceBefore(pyArgumentList));
        } else {
            List<JRightPadded<Expression>> expressions = new ArrayList<>(
                    pyArgumentList.getArguments().length
            );
            for (PyExpression arg : pyArgumentList.getArguments()) {
                expressions.add(mapExpressionAsRightPadded(arg));
            }
            return JContainer.build(expressions).withBefore(spaceBefore(pyArgumentList));
        }
    }

    public J.MethodInvocation mapCallExpression(PyCallExpression element) {
        // DO NOT USE `element.getCallee()`; it unwraps parentheses!
        PyExpression pyCallee = (PyExpression)element.getFirstChild();

        Expression callee = mapExpression(pyCallee);
        PyArgumentList pyArgumentList = element.getArgumentList();

        Markers markers = EMPTY;
        J.Identifier functionName;
        @Nullable JRightPadded<Expression> select;

        if (callee instanceof J.Identifier) {
            // e.g. `print(42)`
            functionName = (J.Identifier) callee;
            select = null;
        } else if (callee instanceof J.FieldAccess) {
            // e.g. `math.sin(2)` or `(..complicated..).foo()`
            J.FieldAccess fieldAccess = (J.FieldAccess) callee;
            functionName = fieldAccess.getName();
            select = JRightPadded.build(fieldAccess.getTarget())
                    .withAfter(fieldAccess.getPadding().getName().getBefore());
        } else {
            // e.g. `(list([1,2,3]).count)(1)`
            markers = Markers.build(singletonList(
                    new MagicMethodDesugar(randomId())
            ));
            functionName = new J.Identifier(
                    randomId(),
                    Space.EMPTY,
                    EMPTY,
                    "__call__",
                    null,
                    null
            );
            // don't include "after" space because it would duplicate the arg list prefix
            select = JRightPadded.build(callee);
        }

        return new J.MethodInvocation(
                randomId(),
                spaceBefore(element),
                markers,
                select,
                null,
                functionName,
                requireNonNull(mapArgumentList(pyArgumentList))
                        .withBefore(spaceBefore(pyArgumentList)),
                null
        );
    }

    public Py.ExpressionStatement mapExpressionStatement(PyExpressionStatement element) {
        Expression expression = mapExpression(element.getExpression());
        return new Py.ExpressionStatement(randomId(), expression);
    }

    public J.ArrayAccess mapSliceExpression(PySliceExpression element) {
        PyExpression pyTarget = requireNonNull(element.getOperand());
        PySliceItem pySlice = requireNonNull(element.getSliceItem());

        J.Identifier builtins = makeBuiltinsIdentifier();

        List<@Nullable PyExpression> pyArgs = new ArrayList<>();
        {
            boolean lastPartWasColon = false;
            for (ASTNode slicePartNode : pySlice.getNode().getChildren(null)) {
                PsiElement slicePart = slicePartNode.getPsi();
                if (slicePart instanceof PyExpression) {
                    pyArgs.add((PyExpression) slicePart);
                    lastPartWasColon = false;
                } else {
                    lastPartWasColon = true;
                }
            }
            if (lastPartWasColon) {
                pyArgs.add(null);
            }
        }

        List<JRightPadded<Expression>> args = new ArrayList<>(pyArgs.size());
        for (PyExpression pyExpression : pyArgs) {
            if (pyExpression instanceof PyEmptyExpression || pyExpression == null) {
                J.Literal none = new J.Literal(
                        randomId(),
                        spaceBefore(pyExpression),
                        Markers.build(singletonList(new ImplicitNone(randomId()))),
                        null,
                        "null",
                        null,
                        JavaType.Primitive.Null
                );
                args.add(JRightPadded.<Expression>build(none).withAfter(spaceAfter(pyExpression)));
            } else {
                args.add(mapExpressionAsRightPadded(pyExpression));
            }
        }

        args = ListUtils.mapLast(args, padded -> padded.withAfter(spaceAfter(pySlice)));

        J.MethodInvocation sliceCall = new J.MethodInvocation(
                randomId(),
                Space.EMPTY,
                Markers.build(singletonList(new BuiltinDesugar(randomId()))),
                JRightPadded.build(builtins),
                null,
                new J.Identifier(randomId(), Space.EMPTY, EMPTY, "slice", null, null),
                JContainer.build(args).withBefore(spaceBefore(pySlice)),
                null
        );

        return new J.ArrayAccess(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpression(pyTarget),
                new J.ArrayDimension(
                        randomId(),
                        spaceAfter(pyTarget),
                        EMPTY,
                        JRightPadded.build(sliceCall)
                ),
                null
        );
    }

    public J.ArrayAccess mapSubscription(PySubscriptionExpression element) {
        PyExpression pyTarget = requireNonNull(element.getOperand());
        PyExpression pyIndex = requireNonNull(element.getIndexExpression());

        return new J.ArrayAccess(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpression(pyTarget),
                new J.ArrayDimension(
                        randomId(),
                        spaceAfter(pyTarget),
                        EMPTY,
                        mapExpressionAsRightPadded(pyIndex)
                ),
                null
        );
    }

    public J.Literal mapStringLiteral(PyStringLiteralExpression element) {
        return new J.Literal(
                randomId(),
                spaceBefore(element),
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
                spaceBefore(element),
                EMPTY,
                requireNonNull(element.getName()),
                null,
                null
        );
    }

    public J.Literal mapNumericLiteral(PyNumericLiteralExpression element) {
        return new J.Literal(
                randomId(),
                spaceBefore(element),
                EMPTY,
                element.getLongValue(),
                element.getText(),
                emptyList(),
                JavaType.Primitive.Long
        );
    }

    public Expression mapReferenceExpression(PyReferenceExpression element) {
        J.Identifier nameId = new J.Identifier(
                randomId(),
                spaceBefore(element.getNameElement().getPsi()),
                EMPTY,
                element.getName(),
                null,
                null
        );

        if (element.getQualifier() == null) {
            return nameId.withPrefix(spaceBefore(element));
        }

        return new J.FieldAccess(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpression(element.getQualifier()),
                JLeftPadded.build(nameId)
                        .withBefore(spaceAfter(element.getQualifier())),
                null
        );
    }

    private J.Identifier expectIdentifier(Expression expression) {
        if (expression instanceof J.Identifier) {
            return (J.Identifier) expression;
        }
        throw new RuntimeException("expected Identifier, but found: " + expression.getClass().getSimpleName());
    }

    private J.Identifier expectIdentifier(@Nullable PsiElement element) {
        if (element == null) {
            throw new RuntimeException("expected Identifier, but element was null");
        }
        return expectIdentifier(element.getNode());
    }

    private J.Identifier expectIdentifier(@Nullable ASTNode node) {
        if (node == null) {
            throw new RuntimeException("expected Identifier, but element was null");
        }
        if (node.getElementType() != PyTokenTypes.IDENTIFIER) {
            throw new RuntimeException("expected Identifier, but node type was: " + node.getElementType());
        }
        return new J.Identifier(
                randomId(),
                spaceBefore(node.getPsi()),
                EMPTY,
                node.getText(),
                null,
                null
        );
    }

    private J.Identifier makeBuiltinsIdentifier() {
        return new J.Identifier(randomId(), Space.EMPTY, EMPTY, "__builtins__", null, null);
    }

    private String expectSimpleName(@Nullable QualifiedName qualifiedName) {
        if (qualifiedName == null) {
            throw new RuntimeException("expected QualifiedName, but element was null");
        }
        if (qualifiedName.getComponentCount() != 1) {
            throw new UnsupportedOperationException("only simple names are supported; found: " + qualifiedName.toString());
        }
        //noinspection DataFlowIssue
        return qualifiedName.getLastComponent();
    }

    /**
     * Collects all continuous space (whitespace and comments) that immediately precedes an element as a sibling.
     * This method will skip zero-length placeholder elements before looking for whitespace.
     */
    private static Space spaceBefore(@Nullable PsiElement element) {
        if (element == null) {
            return Space.EMPTY;
        }

        PsiElement end = element.getPrevSibling();
        while (end != null && isHiddenElement(end)) {
            end = end.getPrevSibling();
        }
        if (!isWhitespaceOrComment(end)) {
            return Space.EMPTY;
        }

        PsiElement begin = end;
        while (isWhitespaceOrComment(begin.getPrevSibling())) {
            begin = begin.getPrevSibling();
        }

        return mergeSpace(begin, end);
    }

    /**
     * Collects all continuous space (whitespace and comments) that immediately follows an element as a sibling.
     * This method will skip zero-length placeholder elements before looking for whitespace.
     */
    private static Space spaceAfter(@Nullable PsiElement element) {
        if (element == null) {
            return Space.EMPTY;
        }

        PsiElement begin = element.getNextSibling();
        while (begin != null && isHiddenElement(begin)) {
            begin = begin.getNextSibling();
        }
        if (!isWhitespaceOrComment(begin)) {
            return Space.EMPTY;
        }

        PsiElement end = begin;
        while (isWhitespaceOrComment(end.getNextSibling())) {
            end = end.getNextSibling();
        }

        return mergeSpace(begin, end);
    }

    /**
     * Collects trailing space <b>inside</b> of an element.
     * <p>
     * The PSI model for some elements (including statements) stores whitespace following an element inside of that
     * element, up to the first newline. This includes trailing comments.
     */
    private static Space trailingSpace(@Nullable PsiElement element) {
        if (element == null) {
            return Space.EMPTY;
        }

        PsiElement end = element.getLastChild();
        if (!isWhitespaceOrComment(end)) {
            return Space.EMPTY;
        }

        PsiElement begin = end;
        while (isWhitespaceOrComment(begin.getPrevSibling())) {
            begin = begin.getPrevSibling();
        }

        return mergeSpace(begin, end);
    }

    private static Space mergeSpace(PsiElement firstSpaceOrComment, PsiElement lastSpaceOrComment) {
        PsiUtils.PsiElementCursor psiElementCursor = PsiUtils.elementsBetween(firstSpaceOrComment, lastSpaceOrComment);

        final String prefix = psiElementCursor.consumeWhitespace();

        List<Comment> comments = null;
        while (!psiElementCursor.isPastEnd()) {
            if (comments == null) {
                comments = new ArrayList<>();
            }
            String commentText = psiElementCursor.consumeExpectingType(PsiComment.class).getText();
            final String suffix = psiElementCursor.consumeWhitespace();

            if (!commentText.startsWith("#")) {
                throw new IllegalStateException(
                        String.format(
                                "expected Python comment to start with `#`; found: `%s`",
                                commentText.charAt(0)
                        )
                );
            }
            commentText = commentText.substring(1);

            comments.add(new PyComment(commentText, suffix, EMPTY));
        }

        return Space.build(prefix, comments == null ? emptyList() : comments);
    }

    private static boolean isWhitespaceOrComment(@Nullable PsiElement element) {
        return element instanceof PsiComment || element instanceof PsiWhiteSpace;
    }
}
