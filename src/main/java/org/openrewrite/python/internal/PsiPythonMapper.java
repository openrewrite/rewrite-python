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
import com.intellij.psi.impl.source.tree.LeafPsiElement;
import com.intellij.psi.util.QualifiedName;
import com.jetbrains.python.PyTokenTypes;
import com.jetbrains.python.psi.*;
import org.jetbrains.annotations.NotNull;
import org.openrewrite.FileAttributes;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.TreeVisitingPrinter;
import org.openrewrite.java.marker.OmitParentheses;
import org.openrewrite.java.tree.*;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.marker.*;
import org.openrewrite.python.tree.Py;
import org.openrewrite.python.tree.PyComment;

import java.nio.file.Path;
import java.util.*;
import java.util.function.BiFunction;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static java.util.Objects.requireNonNull;
import static org.openrewrite.Tree.randomId;
import static org.openrewrite.marker.Markers.EMPTY;
import static org.openrewrite.python.internal.PsiUtils.*;

public class PsiPythonMapper {

    public Py.CompilationUnit mapSource(String sourceText, Path path, String charset, boolean isCharsetBomMarked) {
        boolean addedNewline = false;
        if (!sourceText.endsWith("\n")) {
            addedNewline = true;
            sourceText = sourceText + "\n";
        }

        PyFile pyFile = IntelliJUtils.parsePythonSource(sourceText);
        Py.CompilationUnit compilationUnit = mapFile(pyFile, path, charset, isCharsetBomMarked);
        if (addedNewline) {
            System.err.println("ADDED NEWLINE");
            compilationUnit = compilationUnit.withMarkers(
                    compilationUnit.getMarkers().add(
                            new SuppressNewline(randomId())
                    )
            );
        }

        System.err.println(TreeVisitingPrinter.printTreeAll(compilationUnit));

        return compilationUnit;
    }

    public Py.CompilationUnit mapFile(PyFile element, Path path, String charset, boolean isCharsetBomMarked) {
        new IntelliJUtils.PsiPrinter().print(element.getNode());
        PsiPaddingCursor paddingCursor = new PsiPaddingCursor();
        paddingCursor.resetTo(element.getNode().getFirstChildNode().getPsi());
        List<Statement> statements = singletonList(
                mapBlock(element, null, element.getStatements(), paddingCursor)
        );

        Markers markers = EMPTY;
        if (!element.getText().endsWith("\n")) {
            markers = Markers.build(singletonList(new SuppressNewline(randomId())));
        }

        Space eof = paddingCursor.consumeRemainingAndExpectEOF();

        return new Py.CompilationUnit(
                randomId(),
                Space.EMPTY,
                markers,
                path,
                FileAttributes.fromPath(path),
                charset,
                isCharsetBomMarked,
                null,
                emptyList(),
                emptyList(),
                eof
        ).withStatements(statements);
    }

    public List<Statement> mapStatement(PsiElement element, PsiPaddingCursor paddingCursor) {
        System.err.format("MAPPING %s AT %d; CURSOR IS AT %d\n", element.getNode().getElementType(), element.getNode().getStartOffset(), paddingCursor.offsetInFile());
        try {
            if (element instanceof PyClass) {
                return singletonList(mapClassDeclarationStatement((PyClass) element, paddingCursor));
            } else if (element instanceof PyForStatement) {
                return singletonList(mapForStatement((PyForStatement) element, paddingCursor));
            } else if (element instanceof PyFunction) {
                return singletonList(mapMethodDeclaration((PyFunction) element, paddingCursor));
            } else if (element instanceof PyIfStatement) {
                return singletonList(mapIfStatement((PyIfStatement) element, paddingCursor));
            } else if (element instanceof PyMatchStatement) {
                return singletonList(mapMatchStatement((PyMatchStatement) element, paddingCursor));
            } else if (element instanceof PyTryExceptStatement) {
                return singletonList(mapTry((PyTryExceptStatement) element, paddingCursor));
            } else if (element instanceof PyWhileStatement) {
                return singletonList(mapWhile((PyWhileStatement) element, paddingCursor));
            } else if (element instanceof PyWithStatement) {
                return singletonList(mapWithStatement((PyWithStatement) element, paddingCursor));
            } else {
                return mapSimpleStatement(element);
            }
        } finally {
            System.err.format("AFTER STATEMENT AT %d, CURSOR IS AT %d\n", element.getNode().getStartOffset(), paddingCursor.offsetInFile());
        }
    }

    private List<Statement> mapSimpleStatement(PsiElement element) {
        if (element instanceof PyAssertStatement) {
            return singletonList(mapAssertStatement((PyAssertStatement) element));
        } else if (element instanceof PyAssignmentStatement) {
            return singletonList(mapAssignmentStatement((PyAssignmentStatement) element));
        } else if (element instanceof PyBreakStatement) {
            return singletonList(mapBreakStatement((PyBreakStatement) element));
        } else if (element instanceof PyContinueStatement) {
            return singletonList(mapContinueStatement((PyContinueStatement) element));
        } else if (element instanceof PyDelStatement) {
            return singletonList(mapDelStatement((PyDelStatement) element));
        } else if (element instanceof PyExpressionStatement) {
            return singletonList(mapExpressionStatement((PyExpressionStatement) element));
        } else if (element instanceof PyFromImportStatement) {
            return mapFromImportStatement((PyFromImportStatement) element);
        } else if (element instanceof PyGlobalStatement) {
            return singletonList(mapVariableScopeStatement((PyGlobalStatement) element));
        } else if (element instanceof PyImportStatement) {
            return mapImportStatement((PyImportStatement) element);
        } else if (element instanceof PyNonlocalStatement) {
            return singletonList(mapVariableScopeStatement((PyNonlocalStatement) element));
        } else if (element instanceof PyPassStatement) {
            return singletonList(mapPassStatement((PyPassStatement) element));
        } else if (element instanceof PyRaiseStatement) {
            return singletonList(mapRaiseStatement((PyRaiseStatement) element));
        } else if (element instanceof PyReturnStatement) {
            return singletonList(mapReturnStatement((PyReturnStatement) element));
        }
        throw new IllegalArgumentException("unhandled statement of type " + element.getClass().getSimpleName());
    }

    private J.Throw mapRaiseStatement(PyRaiseStatement element) {
        if (element.getExpressions().length > 2) {
            throw new IllegalArgumentException(
                    "no support for a `raise` statement with >1 expression"
            );
        }


        Expression expression;
        if (element.getExpressions().length == 0) {
            expression = new J.Empty(
                    randomId(),
                    Space.EMPTY,
                    EMPTY
            );
        } else {
            expression = mapExpression(element.getExpressions()[0]);
            if (element.getExpressions().length == 2) {
                JLeftPadded<Expression> from = JLeftPadded.<Expression>build(
                                mapExpression(element.getExpressions()[1])
                                        .withPrefix(spaceBefore(element.getExpressions()[1]))
                        )
                        .withBefore(spaceAfter(element.getExpressions()[0]));

                expression = new Py.ErrorFromExpression(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        expression,
                        from,
                        null
                );
            }
        }

        return new J.Throw(
                randomId(),
                Space.EMPTY,
                EMPTY,
                expression
        );
    }

    private Py.VariableScopeStatement mapVariableScopeStatement(PyGlobalStatement element) {
        return mapVariableScopeStatement(element, Py.VariableScopeStatement.Kind.GLOBAL);
    }

    private Py.VariableScopeStatement mapVariableScopeStatement(PyNonlocalStatement element) {
        return mapVariableScopeStatement(element, Py.VariableScopeStatement.Kind.NONLOCAL);
    }

    private Py.VariableScopeStatement mapVariableScopeStatement(PyStatement element, Py.VariableScopeStatement.Kind kind) {
        List<JRightPadded<J.Identifier>> names = new ArrayList<>();
        for (PsiElement child : element.getChildren()) {
            if (child instanceof PyTargetExpression) {
                J.Identifier identifier = expectIdentifier(child).withPrefix(spaceBefore(child));
                names.add(JRightPadded.build(identifier).withAfter(spaceAfter(child)));
            }
        }
        return new Py.VariableScopeStatement(
                randomId(),
                Space.EMPTY,
                EMPTY,
                kind,
                names
        );
    }

    private List<Statement> mapImportElements(PyImportStatementBase element, @Nullable Expression importSource) {
        List<Statement> imports = new ArrayList<>(element.getImportElements().length);
        for (PyImportElement pyImportElement : element.getImportElements()) {
            imports.add(mapImportElement(pyImportElement, element, importSource));
        }
        if (imports.size() > 1) {
            UUID groupId = randomId();
            imports = ListUtils.map(
                    imports,
                    impoort -> impoort.withMarkers(impoort.getMarkers().add(new GroupedStatement(randomId(), groupId)))
            );
        }

        PsiElement openParen = maybeFindChildToken(element, PyTokenTypes.LPAR);
        PsiElement closeParen = maybeFindChildToken(element, PyTokenTypes.RPAR);
        if (openParen != null && closeParen != null) {
            imports = ListUtils.map(
                    imports,
                    statement -> {
                        statement = PythonExtraPadding.set(
                                statement,
                                PythonExtraPadding.Location.IMPORT_PARENS_PREFIX, spaceBefore(openParen)
                        );
                        statement = PythonExtraPadding.set(
                                statement,
                                PythonExtraPadding.Location.IMPORT_PARENS_SUFFIX, spaceBefore(closeParen)
                        );
                        return statement;
                    }
            );
        }

        return imports;
    }

    private J.Import mapImportElement(PyImportElement element, PyImportStatementBase parent, @Nullable Expression importSource) {
        PsiElement importKeyword = findChildToken(parent, PyTokenTypes.IMPORT_KEYWORD);

        Expression importNameExpr = mapExpression(requireNonNull(element.getImportReferenceExpression()));
        if (!(importNameExpr instanceof J.Identifier)) {
            throw new UnsupportedOperationException("no support for qualified import targets in imports");
        }

        //  from math import ceil      or      import ceil
        //                  ^^^^^                    ^^^^^
        J.Identifier importName = (J.Identifier) importNameExpr.withPrefix(spaceBefore(element));


        J.FieldAccess fieldAccess;
        if (importSource == null) {
            // import ...
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
            // from math import ...
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

        PyTargetExpression pyAlias = element.getAsNameElement();
        JLeftPadded<J.Identifier> alias = null;
        if (pyAlias != null) {
            PsiElement asKeyword = findChildToken(element, PyTokenTypes.AS_KEYWORD);
            J.Identifier aliasId = expectIdentifier(mapExpression(pyAlias));
            alias = JLeftPadded.build(
                    aliasId.withPrefix(spaceAfter(asKeyword))
            ).withBefore(spaceBefore(asKeyword));
        }

        return new J.Import(
                randomId(),
                Space.EMPTY,
                EMPTY,
                JLeftPadded.build(false),
                fieldAccess,
                alias
        );
    }

    private List<Statement> mapImportStatement(PyImportStatement element) {
        return mapImportElements(element, null);
    }

    private List<Statement> mapFromImportStatement(PyFromImportStatement element) {
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

    private Statement mapMatchStatement(PyMatchStatement element, PsiPaddingCursor paddingCursor) {
        JRightPadded<Expression> subject = mapExpressionAsRightPadded(requireNonNull(element.getSubject()));
        J.Block block = this.mapBlock(
                element,
                findChildToken(element, PyTokenTypes.COLON),
                element.getCaseClauses(),
                paddingCursor,
                (clause, cur) -> singletonList(mapCaseClause(clause, cur))
        );
        return new J.Switch(
                randomId(),
                Space.EMPTY,
                EMPTY,
                new J.ControlParentheses<>(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        subject
                ),
                block
        );
    }

    private Statement mapCaseClause(PyCaseClause element, PsiPaddingCursor paddingCursor) {
        Space prefix = paddingCursor.consumeRemainingAndExpect(element);

        JRightPadded<Expression> pattern;
        if (element.getGuardCondition() != null) {
            pattern = JRightPadded.build(
                    new Py.MatchCase(
                            randomId(),
                            Space.EMPTY,
                            EMPTY,
                            mapPattern(requireNonNull(element.getPattern())),
                            JLeftPadded.build(mapExpression(element.getGuardCondition()))
                                    .withBefore(spaceBefore(findChildToken(element, PyTokenTypes.IF_KEYWORD))),
                            null
                    )
            );
        } else {
            pattern = mapExpressionAsRightPadded(requireNonNull(element.getPattern()));
        }

        J.Block block = mapCompoundBlock(element, paddingCursor);
        return new J.Case(
                randomId(),
                prefix,
                EMPTY,
                J.Case.Type.Statement,
                JContainer.build(singletonList(pattern)),
                JContainer.empty(),
                JRightPadded.build(block)
        );
    }


    private Statement mapWhile(PyWhileStatement element, PsiPaddingCursor paddingCursor) {
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
                JRightPadded.build(mapCompoundBlock(element.getWhilePart(), paddingCursor))
        );
    }

    private Statement mapTry(PyTryExceptStatement element, PsiPaddingCursor paddingCursor) {
        Space tryPrefix = paddingCursor.consumeRemainingAndExpect(element);
        J.Block tryBlock = mapCompoundBlock(element.getTryPart(), paddingCursor);

        List<J.Try.Catch> catches = emptyList();
        if (element.getExceptParts().length > 0) {
            catches = new ArrayList<>(element.getExceptParts().length);
            for (PyExceptPart pyExceptPart : element.getExceptParts()) {
                catches.add(mapExcept(pyExceptPart, paddingCursor));
            }
        }

        if (element.getElsePart() != null) {
            /*
                Python has a bizarre try/catch component: the "else" clause.

                    try:
                        pass
                    except:
                        pass
                    else:
                        <else-stmts>

                 This is semantically *identical* to:

                    try:
                        pass
                        <else-stmts>
                    except:
                        pass:

                If an "else" block is present, we can make it the last statement
                in the "try" block. Blocks cannot be arbitrarily nested in Python,
                so this uniquely identifies the clause for printing, while statement
                processing visitors will be unaffected.
             */
            Space elsePrefix = paddingCursor.consumeRemainingAndExpect(element.getElsePart());
            tryBlock = tryBlock.getPadding().withStatements(
                    ListUtils.concat(
                            tryBlock.getPadding().getStatements(),
                            JRightPadded.<Statement>build(
                                    mapCompoundBlock(element.getElsePart(), paddingCursor)
                            ).withAfter(elsePrefix)
                    )
            );
        }

        JLeftPadded<J.Block> finallie = null;
        if (element.getFinallyPart() != null) {
            Space finallyPrefix = paddingCursor.consumeRemainingAndExpect(element.getFinallyPart());
            finallie = JLeftPadded.build(
                    mapCompoundBlock(element.getFinallyPart(), paddingCursor)
            ).withBefore(finallyPrefix);
        }

        return new J.Try(
                randomId(),
                tryPrefix,
                EMPTY,
                null,
                tryBlock,
                catches,
                finallie
        );
    }

    private J.Try.Catch mapExcept(PyExceptPart element, PsiPaddingCursor paddingCursor) {
        Space exceptPrefix = paddingCursor.consumeRemainingAndExpect(element);

        List<JRightPadded<J.VariableDeclarations.NamedVariable>> parameters = emptyList();
        PyExpression pyExceptClass = element.getExceptClass();
        PyExpression pyTarget = element.getTarget();

        TypeTree typeExpression = null;
        if (pyExceptClass != null) {
            String name = "";
            if (pyTarget != null) {
                name = pyTarget.getText();
            }

            typeExpression = new Py.ExceptionType(
                    randomId(),
                    spaceAfter(findChildToken(element, PyTokenTypes.EXCEPT_KEYWORD)),
                    EMPTY,
                    null,
                    element.isStar(),
                    mapExpression(pyExceptClass)
                            .withPrefix(
                                    element.isStar()
                                            ? spaceBefore(pyExceptClass)
                                            : Space.EMPTY
                            )
            );

            parameters = singletonList(JRightPadded.build(
                    new J.VariableDeclarations.NamedVariable(
                            randomId(),
                            spaceAfter(pyExceptClass),
                            EMPTY,
                            new J.Identifier(
                                    randomId(),
                                    spaceBefore(pyTarget),
                                    EMPTY,
                                    name,
                                    null,
                                    null
                            ),
                            emptyList(),
                            null,
                            null
                    )
            ));
        }
        return new J.Try.Catch(
                randomId(),
                exceptPrefix,
                EMPTY,
                new J.ControlParentheses<>(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        JRightPadded.build(
                                new J.VariableDeclarations(
                                        randomId(),
                                        Space.EMPTY,
                                        EMPTY,
                                        emptyList(),
                                        emptyList(),
                                        typeExpression,
                                        null,
                                        emptyList(),
                                        parameters
                                )
                        )
                ),
                mapCompoundBlock(element, paddingCursor)
        );
    }

    private Statement mapWithStatement(PyWithStatement element, PsiPaddingCursor paddingCursor) {
        List<JRightPadded<J.Try.Resource>> resources = new ArrayList<>(element.getWithItems().length);
        /*
            Example code:

                with A() as a , B() as b:
                    pass
         */
        for (PyWithItem pyWithItem : element.getWithItems()) {
            /*
                Example:

                +------+-----------------------------------------------------------------+
                |      |                           JRightPadded                          |
                |      +-------------------------------------------------------+---------+
                |      |                       "element"                       | "after" |
                |      +-------------------------------------------------------+---------+
                |      |                     J.Try.Resource                    |         |
                |      +----------+--------------------------------------------+         |
                |      | "prefix" |            "variableDeclaration"           |         |
                |      +----------+--------------------------------------------+         |
                |      |          |                J.Assignment                |         |
                |      |          +----------------------+----+----------------+         |
                |      |          |     "assignment"     |    |   "variable"   |         |
                |      |          +----------------------+    +----------------+         |
                |      |          |      JLeftPadded     |    |   Expression   |         |
                |      |          +-----------+----------+    +----------+-----+         |
                |      |          | "element" | "before" |    | "prefix" | ... |         |
                +------+----------+-----------+----------+    +----------+-----+---------+
                | with |          |    A()    |          | as |          |  a  |         |
                +------+----------+-----------+----------+----+----------+-----+---------+

             */
            PsiElement asToken = findChildToken(pyWithItem, PyTokenTypes.AS_KEYWORD);

            Expression variable = mapExpression(pyWithItem.getTarget())
                    .withPrefix(spaceAfter(asToken));

            JLeftPadded<Expression> assignment = JLeftPadded.<Expression>build(
                    mapExpression(pyWithItem.getExpression()).withPrefix(Space.EMPTY)
            ).withBefore(spaceBefore(asToken));

            J.Try.Resource resource = new J.Try.Resource(
                    randomId(),
                    spaceBefore(pyWithItem),
                    EMPTY,
                    new J.Assignment(
                            randomId(),
                            Space.EMPTY,
                            EMPTY,
                            variable,
                            assignment,
                            null
                    ),
                    false
            );
            resources.add(
                    JRightPadded.build(resource)
                            .withAfter(spaceAfter(pyWithItem))
            );
        }

        // any space that comes before the colon is owned by the block
        resources = ListUtils.mapLast(
                resources,
                resource -> resource.withAfter(Space.EMPTY)
        );

        return new J.Try(
                randomId(),
                Space.EMPTY,
                EMPTY,
                JContainer.build(resources),
                mapCompoundBlock(element, paddingCursor),
                emptyList(),
                null
        );
    }

    private Statement mapContinueStatement(PyContinueStatement element) {
        return new J.Continue(
                randomId(),
                Space.EMPTY,
                EMPTY,
                null
        );
    }

    private Statement mapBreakStatement(PyBreakStatement element) {
        return new J.Break(
                randomId(),
                Space.EMPTY,
                EMPTY,
                null
        );
    }

    private Statement mapForStatement(PyForStatement element, PsiPaddingCursor paddingCursor) {
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
                JRightPadded.build(mapCompoundBlock(forPart, paddingCursor))
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

    private Statement mapMethodDeclaration(PyFunction element, PsiPaddingCursor paddingCursor) {
        PyParameter @NotNull [] pyParameters = element.getParameterList().getParameters();
        List<JRightPadded<Statement>> params = new ArrayList<>(pyParameters.length);
        for (PyParameter pyParam : pyParameters) {
            params.add(
                    JRightPadded.<Statement>build(
                            mapFunctionParameter(pyParam).withPrefix(spaceBefore(pyParam))
                    ).withAfter(spaceAfter(pyParam))
            );
        }

        return new J.MethodDeclaration(
                randomId(),
                Space.EMPTY,
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
                JContainer.build(params),
                null,
                mapCompoundBlock(element, paddingCursor),
                null,
                null
        );
    }

    private Statement mapFunctionParameter(PyElement element) {
        if (element instanceof PyNamedParameter) {
            PyNamedParameter namedParameter = (PyNamedParameter) element;
            J.Identifier identifier = expectIdentifier(namedParameter.getNameIdentifier());
            JLeftPadded<Expression> defaultValue = null;
            if (namedParameter.hasDefaultValue()) {
                defaultValue = JLeftPadded.build(
                        mapExpression(namedParameter.getDefaultValue())
                ).withBefore(spaceBefore(namedParameter.getDefaultValue()));
            }


            if (namedParameter.isKeywordContainer()) {
                return new Py.ExpressionStatement(
                        randomId(),
                        new Py.SpecialParameter(
                                randomId(),
                                spaceBefore(element),
                                EMPTY,
                                Py.SpecialParameter.Kind.KWARGS,
                                identifier,
                                null
                        )
                );
            } else if (namedParameter.isPositionalContainer()) {
                return new Py.ExpressionStatement(
                        randomId(),
                        new Py.SpecialParameter(
                                randomId(),
                                spaceBefore(element),
                                EMPTY,
                                Py.SpecialParameter.Kind.ARGS,
                                identifier,
                                null
                        )
                );
            } else if (defaultValue == null) {
                return new Py.ExpressionStatement(
                        randomId(),
                        identifier
                );
            } else {
                return new Py.ExpressionStatement(
                        randomId(),
                        new J.Assignment(
                                randomId(),
                                Space.EMPTY,
                                EMPTY,
                                identifier,
                                defaultValue,
                                null
                        )
                );
            }
        } else {
            throw new IllegalArgumentException(String.format(
                    "can't treat " + element.getNode().getElementType() + " as a function parameter"
            ));
        }
    }

    public Statement mapAssertStatement(PyAssertStatement element) {
        return new Py.AssertStatement(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpressionsAsRightPadded(element.getArguments())
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

    public Statement mapClassDeclarationStatement(PyClass element, PsiPaddingCursor paddingCursor) {
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
                mapCompoundBlock(element, paddingCursor),
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

    public Statement mapDelStatement(PyDelStatement element) {
        return new Py.DelStatement(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpressionsAsRightPadded(element.getTargets())
        );
    }

    public Statement mapIfStatement(PyIfStatement element, PsiPaddingCursor paddingCursor) {
        PyExpression pyIfCondition = element.getIfPart().getCondition();
        if (pyIfCondition == null) {
            throw new RuntimeException("if condition is null");
        }

        Statement ifBody = mapCompoundBlock(element.getIfPart(), paddingCursor);
        J.If.Else elsePart = mapElsePart(element, 0, paddingCursor);

        return new J.If(
                randomId(),
                Space.EMPTY,
                EMPTY,
                mapExpressionAsControlParentheses(pyIfCondition),
                JRightPadded.build(ifBody),
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
    private J.If.Else mapElsePart(PyIfStatement parent, int elifIndex, PsiPaddingCursor paddingCursor) {
        if (elifIndex < parent.getElifParts().length) {
            PyIfPart pyElifPart = parent.getElifParts()[elifIndex];

            PyExpression pyIfCondition = pyElifPart.getCondition();
            if (pyIfCondition == null) {
                throw new RuntimeException("if condition is null");
            }

            Space prefix = paddingCursor.consumeRemainingAndExpect(pyElifPart);
            J.Block thenPart = mapCompoundBlock(pyElifPart, paddingCursor);
            J.If.Else elsePart = mapElsePart(parent, elifIndex + 1, paddingCursor);

            J.If nestedIf = new J.If(
                    randomId(),
                    Space.EMPTY,
                    EMPTY,
                    mapExpressionAsControlParentheses(pyIfCondition),
                    JRightPadded.build(thenPart),
                    elsePart
            );
            return new J.If.Else(
                    randomId(),
                    prefix,
                    EMPTY,
                    JRightPadded.build(nestedIf)
            );
        } else if (parent.getElsePart() != null) {
            Space prefix = paddingCursor.consumeRemainingAndExpect(parent.getElsePart());
            J.Block elsePart = mapCompoundBlock(parent.getElsePart(), paddingCursor);
            return new J.If.Else(
                    randomId(),
                    prefix,
                    EMPTY,
                    JRightPadded.build(elsePart)
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

    public <T extends PyStatement> J.Block mapBlock(
            PsiElement container,
            @Nullable PsiElement colonToken,
            List<T> pyStatements,
            PsiPaddingCursor paddingCursor
    ) {
        return mapBlock(container, colonToken, pyStatements, paddingCursor, this::mapStatement);
    }

    public <T extends PsiElement> J.Block mapBlock(
            PsiElement container,
            @Nullable PsiElement colonToken,
            List<T> pyStatements,
            PsiPaddingCursor paddingCursor,
            BiFunction<T, PsiPaddingCursor, List<? extends Statement>> mapFn
    ) {
        System.err.format("MAPPING BLOCK AT %d, CURSOR IS AT %d\n", container.getNode().getStartOffset(), paddingCursor.offsetInFile());
//        if (!isCompoundStatement(container)) {
//            throw new IllegalArgumentException(String.format(
//                    "Element of type %s cannot be mapped as a block because its type is not registered in " +
//                            "`isCompoundStatement`. This method ensures that whitespace consumption rules " +
//                            "are kept in sync when compound statements are nested.",
//                    container.getNode().getElementType()
//            ));
//        }

        List<JRightPadded<Statement>> statements = new ArrayList<>(pyStatements.size());

//        final PyStatement finalPyStatementInBlock = pyStatements.get(pyStatements.size() - 1);

        if (colonToken != null) {
            paddingCursor.resetToSpaceAfter(colonToken);
        }
        Space blockPrefix = paddingCursor.consumeUntilNewline();

        for (T pyStatement : pyStatements) {
            Space prefix = paddingCursor.consumeRemainingAndExpect(pyStatement);
            List<? extends Statement> mapped = mapFn.apply(pyStatement, paddingCursor);

            Space after;
            @Nullable JRightPadded<Statement> emptyStatement = null;
            if (paddingCursor.isPast(pyStatement)) {
                // compound statement
                after = Space.EMPTY;
            } else {
                // simple statement
                PsiElement semicolon = maybeFindChildToken(pyStatement, PyTokenTypes.SEMICOLON);
                if (semicolon != null) {
                    paddingCursor.resetToSpaceBefore(semicolon);
                    after = paddingCursor.consumeRemainingAndExpect(semicolon);
                    paddingCursor.resetToSpaceAfter(semicolon);
                    emptyStatement = paddingCursor.consumeUntilNewlineOrReset(
                            newlineAfterSemicolon ->
                                    JRightPadded.<Statement>build(
                                            new J.Empty(
                                                    randomId(),
                                                    Space.EMPTY,
                                                    EMPTY
                                            )
                                    ).withAfter(newlineAfterSemicolon)
                    );
                } else {
                    paddingCursor.resetToTrailingSpaceWithin(pyStatement);
                    after = paddingCursor.consumeUntilNewline();
                }
            }


            /*
              There is usually only one statement returned.
              In the unusual case that there's more than one, every statement gets the same padding.
            */
            for (Statement statement : mapped) {
                statement = statement.withPrefix(prefix);
                statements.add(JRightPadded.build(statement).withAfter(after));
            }

            if (emptyStatement != null) {
                statements.add(emptyStatement);
            }
        }

        Markers markers = EMPTY;
        {
            Space spaceBeforeColon = spaceBefore(colonToken);
            if (!spaceBeforeColon.isEmpty()) {
                markers = Markers.build(singletonList(new PythonExtraPadding(
                        randomId(),
                        PythonExtraPadding.Location.BEFORE_COMPOUND_BLOCK_COLON,
                        spaceBeforeColon
                )));
            }
        }

        return new J.Block(
                randomId(),
                blockPrefix,
                markers,
                JRightPadded.build(false),
                statements,
                Space.EMPTY
        );
    }


    /**
     * Maps the statement list of a Python "compound block" as a J.Block.
     * <br/>
     * Python's compound blocks are those that have colons followed by an indented block of statements.
     * The returned J.Block represents these statements, as well as the preceding colon.
     * <br/>
     * In general, if you want to map the body of a compound block, use this method.
     */
    public J.Block mapCompoundBlock(PyStatementListContainer pyElement, PsiPaddingCursor paddingCursor) {
        return mapBlock(
                pyElement,
                findChildToken(pyElement, PyTokenTypes.COLON),
                Arrays.asList(pyElement.getStatementList().getStatements()),
                paddingCursor
        );
    }

    public Expression mapExpression(@Nullable PsiElement element) {
        if (element == null) {
            //noinspection DataFlowIssue
            return null;
        }

        if (element instanceof LeafPsiElement && isLeafToken(element, PyTokenTypes.IDENTIFIER)) {
            return expectIdentifier(element);
        }

        if (element instanceof PyPattern) {
            return mapPattern((PyPattern) element);
        }

        if (element instanceof PyBinaryExpression) {
            return mapBinaryExpression((PyBinaryExpression) element);
        } else if (element instanceof PyBoolLiteralExpression) {
            return mapBooleanLiteral((PyBoolLiteralExpression) element);
        } else if (element instanceof PyCallExpression) {
            return mapCallExpression((PyCallExpression) element);
        } else if (element instanceof PyComprehensionElement) {
            return mapComprehensionElement((PyComprehensionElement) element);
        } else if (element instanceof PyDictLiteralExpression) {
            return mapDictLiteralExpression((PyDictLiteralExpression) element);
        } else if (element instanceof PyKeyValueExpression) {
            return mapKeyValueExpression((PyKeyValueExpression) element);
        } else if (element instanceof PyKeywordArgument) {
            return mapKeywordArgument((PyKeywordArgument) element);
        } else if (element instanceof PyLambdaExpression) {
            return mapLambdaExpression((PyLambdaExpression) element);
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
        } else if (element instanceof PyYieldExpression) {
            return mapYieldExpression((PyYieldExpression) element);
        }
        System.err.println("WARNING: unhandled expression of type " + element.getClass().getSimpleName());
        return null;
    }

    private Py.MatchCase.Pattern mapPattern(PyPattern pattern) {
        JContainer<Expression> children;
        Py.MatchCase.Pattern.Kind kind;
        if (pattern instanceof PyAsPattern) {
            kind = Py.MatchCase.Pattern.Kind.AS;
            children = JContainer.build(
                    mapExpressionsAsRightPadded(pattern.getChildren())
            );
        } else if (pattern instanceof PyCapturePattern) {
            kind = Py.MatchCase.Pattern.Kind.CAPTURE;
            children = JContainer.build(
                    mapExpressionsAsRightPadded(pattern.getChildren())
            );
        } else if (pattern instanceof PyClassPattern) {
            kind = Py.MatchCase.Pattern.Kind.CLASS;
            JRightPadded<Expression> className = mapExpressionAsRightPadded(pattern.getChildren()[0]);
            PyPatternArgumentList pyArgList = (PyPatternArgumentList) pattern.getChildren()[1];
            List<JRightPadded<Expression>> args = mapExpressionsAsRightPadded(
                    pyArgList.getChildren()
            );
            children = JContainer.build(ListUtils.concat(className, args));
        } else if (pattern instanceof PyDoubleStarPattern) {
            kind = Py.MatchCase.Pattern.Kind.DOUBLE_STAR;
            children = JContainer.build(
                    spaceAfter(findChildToken(pattern, PyTokenTypes.EXP)),
                    mapExpressionsAsRightPadded(pattern.getChildren()),
                    EMPTY
            );
        } else if (pattern instanceof PyGroupPattern) {
            kind = Py.MatchCase.Pattern.Kind.GROUP;
            children = JContainer.build(
                    mapExpressionsAsRightPadded(pattern.getChildren())
            );
        } else if (pattern instanceof PyKeyValuePattern) {
            kind = Py.MatchCase.Pattern.Kind.KEY_VALUE;
            children = JContainer.build(
                    mapExpressionsAsRightPadded(pattern.getChildren())
            );
        } else if (pattern instanceof PyKeywordPattern) {
            kind = Py.MatchCase.Pattern.Kind.KEYWORD;
            PyKeywordPattern keywordPattern = (PyKeywordPattern) pattern;
            children = JContainer.build(
                    mapExpressionsAsRightPadded(new PsiElement[]{
                            keywordPattern.getKeywordElement(),
                            keywordPattern.getValuePattern()
                    })
            );
        } else if (pattern instanceof PyLiteralPattern) {
            kind = Py.MatchCase.Pattern.Kind.LITERAL;
            children = JContainer.build(
                    singletonList(
                            mapExpressionAsRightPadded(((PyLiteralPattern) pattern).getExpression())
                    )
            );
        } else if (pattern instanceof PyMappingPattern) {
            kind = Py.MatchCase.Pattern.Kind.MAPPING;
            children = JContainer.build(
                    mapExpressionsAsRightPadded(pattern.getChildren())
            );
        } else if (pattern instanceof PyOrPattern) {
            kind = Py.MatchCase.Pattern.Kind.OR;
            children = JContainer.build(
                    mapExpressionsAsRightPadded(pattern.getChildren())
            );
        } else if (pattern instanceof PySequencePattern) {
            kind = Py.MatchCase.Pattern.Kind.SEQUENCE;
            children = JContainer.build(
                    spaceAfter(findChildToken(pattern, PyTokenTypes.LBRACKET)),
                    mapExpressionsAsRightPadded(pattern.getChildren()),
                    EMPTY
            );
        } else if (pattern instanceof PySingleStarPattern) {
            kind = Py.MatchCase.Pattern.Kind.STAR;
            children = JContainer.build(
                    spaceAfter(findChildToken(pattern, PyTokenTypes.MULT)),
                    mapExpressionsAsRightPadded(pattern.getChildren()),
                    EMPTY
            );
        } else if (pattern instanceof PyValuePattern) {
            kind = Py.MatchCase.Pattern.Kind.VALUE;
            children = JContainer.build(
                    mapExpressionsAsRightPadded(pattern.getChildren())
            );
        } else if (pattern instanceof PyWildcardPattern) {
            kind = Py.MatchCase.Pattern.Kind.WILDCARD;
            children = JContainer.empty();
        } else {
            System.err.println("WARNING: unhandled pattern of type " + pattern.getClass().getSimpleName());
            return null;
        }

        return new Py.MatchCase.Pattern(
                randomId(),
                spaceBefore(pattern),
                EMPTY,
                kind,
                children,
                null
        );
    }

    private J.Lambda mapLambdaExpression(PyLambdaExpression pyExpression) {
        PyParameterList pyParams = pyExpression.getParameterList();
        List<JRightPadded<J>> params = new ArrayList<>(pyParams.getParameters().length);
        for (PyParameter pyParam : pyParams.getParameters()) {
            params.add(JRightPadded.<J>build(
                    mapFunctionParameter(pyParam).withPrefix(spaceBefore(pyParam))
            ).withAfter(spaceAfter(pyParam)));
        }

        return new J.Lambda(
                randomId(),
                spaceBefore(pyExpression),
                EMPTY,
                new J.Lambda.Parameters(
                        randomId(),
                        spaceBefore(pyParams),
                        EMPTY,
                        false,
                        params
                ),
                spaceAfter(pyParams),
                mapExpression(pyExpression.getBody()),
                null
        );
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
    private JRightPadded<Expression> mapExpressionAsRightPadded(PsiElement pyExpression) {
        Expression expression = mapExpression(pyExpression);
        return JRightPadded.build(expression).withAfter(spaceAfter(pyExpression));
    }

    private List<JRightPadded<Expression>> mapExpressionsAsRightPadded(PsiElement[] pyExpressions) {
        if (pyExpressions.length == 0) {
            return emptyList();
        }
        List<JRightPadded<Expression>> expressions = new ArrayList<>(pyExpressions.length);
        for (PsiElement pyExpression : pyExpressions) {
            Expression expression = mapExpression(pyExpression);
            expressions.add(
                    JRightPadded.build(expression).withAfter(spaceAfter(pyExpression))
            );
        }
        return expressions;
    }

    private Expression mapDictLiteralExpression(PyDictLiteralExpression element) {
        List<JRightPadded<Py.KeyValue>> elements = new ArrayList<>(element.getElements().length);
        for (PyKeyValueExpression e : element.getElements()) {
            elements.add(JRightPadded.build(mapKeyValueExpression(e)).withAfter(spaceAfter(e)));
        }
        Expression literal = new Py.DictLiteral(
                randomId(),
                spaceBefore(element),
                EMPTY,
                JContainer.build(elements),
                null
        );
        if (elements.isEmpty()) {
            literal = PythonExtraPadding.set(
                    literal,
                    PythonExtraPadding.Location.EMPTY_INITIALIZER,
                    spaceAfter(findChildToken(element, PyTokenTypes.LBRACE))
            );
        }
        return literal;
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
            exprs = mapExpressionsAsRightPadded(element.getElements());
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

    public Expression mapComprehensionElement(PyComprehensionElement element) {
        Py.ComprehensionExpression.Kind kind;
        if (element instanceof PyListCompExpression) {
            kind = Py.ComprehensionExpression.Kind.LIST;
        } else if (element instanceof PySetCompExpression) {
            kind = Py.ComprehensionExpression.Kind.SET;
        } else if (element instanceof PyDictCompExpression) {
            kind = Py.ComprehensionExpression.Kind.DICT;
        } else if (element instanceof PyGeneratorExpression) {
            kind = Py.ComprehensionExpression.Kind.GENERATOR;
        } else {
            throw new IllegalArgumentException(String.format(
                    "unknown comprehension type: %s",
                    element.getNode().getElementType()
            ));
        }
        List<Py.ComprehensionExpression.Clause> clauses = new ArrayList<>();
        for (PyComprehensionComponent ifOrFor : element.getComponents()) {
            if (ifOrFor instanceof PyComprehensionForComponent) {
                PyComprehensionForComponent pyFor = (PyComprehensionForComponent) ifOrFor;
                PsiElement forKeyword = findPreviousSiblingToken(pyFor.getIteratorVariable(), PyTokenTypes.FOR_KEYWORD);
                PsiElement inKeyword = findPreviousSiblingToken(pyFor.getIteratedList(), PyTokenTypes.IN_KEYWORD);
                Expression iteratorVariable = mapExpression(pyFor.getIteratorVariable());
                Expression iteratedList = mapExpression(pyFor.getIteratedList());
                clauses.add(new Py.ComprehensionExpression.Clause(
                        randomId(),
                        spaceBefore(forKeyword),
                        EMPTY,
                        iteratorVariable,
                        JLeftPadded.build(iteratedList).withBefore(spaceBefore(inKeyword)),
                        null
                ));
            } else if (ifOrFor instanceof PyComprehensionIfComponent) {
                PyComprehensionIfComponent pyif = (PyComprehensionIfComponent) ifOrFor;
                PsiElement ifKeyword = findPreviousSiblingToken(pyif.getTest(), PyTokenTypes.IF_KEYWORD);
                Py.ComprehensionExpression.Condition condition = new Py.ComprehensionExpression.Condition(
                        randomId(),
                        spaceBefore(ifKeyword),
                        EMPTY,
                        mapExpression(pyif.getTest())
                );
                clauses = ListUtils.mapLast(
                        clauses,
                        clause -> clause.withConditions(ListUtils.concat(clause.getConditions(), condition))
                );
            } else {
                throw new IllegalStateException("expected comprehension component to be an `if` or a `for`");
            }
        }

        PsiElement closing = element.getNode().getLastChildNode().getPsi();

        return new Py.ComprehensionExpression(
                randomId(),
                Space.EMPTY,
                EMPTY,
                kind,
                mapExpression(element.getResultExpression()),
                clauses,
                spaceBefore(closing),
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

    private Expression mapYieldExpression(PyYieldExpression element) {
        JLeftPadded<Boolean> from;
        if (element.isDelegating()) {
            PsiElement fromKeyword = findChildToken(element, PyTokenTypes.FROM_KEYWORD);
            from = JLeftPadded.build(true).withBefore(spaceBefore(fromKeyword));
        } else {
            from = JLeftPadded.build(false);
        }

        PyExpression pyExpression = requireNonNull(element.getExpression());
        List<JRightPadded<Expression>> expressions;
        if (pyExpression instanceof PyTupleExpression) {
            expressions = mapExpressionsAsRightPadded(((PyTupleExpression) pyExpression).getElements());
            expressions = ListUtils.mapFirst(
                    expressions,
                    expr -> expr.withElement(expr.getElement().withPrefix(spaceBefore(pyExpression)))
            );
        } else {
            expressions = singletonList(mapExpressionAsRightPadded(pyExpression));
        }

        return new Py.YieldExpression(
                randomId(),
                spaceBefore(element),
                EMPTY,
                from,
                expressions,
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
            return PythonExtraPadding.set(
                    mapBinaryExpressionAsOperator(element, J.Binary.Type.NotEqual),
                    PythonExtraPadding.Location.WITHIN_OPERATOR_NAME,
                    spaceAfter(psiOperator)
            );
        } else if (matchesTokenSequence(psiOperator, PyTokenTypes.NOT_KEYWORD, PyTokenTypes.IN_KEYWORD)) {
            // a very special case, as there is no magic method for "not in"
            // instead, wrap the "in" expression in a "not"
            Expression containsMethodCall = PythonExtraPadding.set(
                    mapBinaryExpressionAsMagicMethod(element, "__contains__").withPrefix(Space.EMPTY),
                    PythonExtraPadding.Location.WITHIN_OPERATOR_NAME,
                    spaceAfter(psiOperator)
            );
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

        if (op == PyTokenTypes.AWAIT_KEYWORD) {
            return new Py.AwaitExpression(
                    randomId(),
                    spaceBefore(element),
                    EMPTY,
                    mapExpression(element.getOperand()),
                    null
            );
        }

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
            List<JRightPadded<Expression>> expressions = mapExpressionsAsRightPadded(pyArgumentList.getArguments());
            return JContainer.build(expressions).withBefore(spaceBefore(pyArgumentList));
        }
    }

    public J.MethodInvocation mapCallExpression(PyCallExpression element) {
        // DO NOT USE `element.getCallee()`; it unwraps parentheses!
        PyExpression pyCallee = (PyExpression) element.getFirstChild();

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

    private boolean isCompoundStatement(PsiElement element) {
        return element instanceof PyStatementListContainer
                || element instanceof PyFile;
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
        ASTNode node;
        if (element instanceof PyTargetExpression) {
            if (element.getNode().getChildren(null).length != 1) {
                throw new RuntimeException("expected Identifier, but found a TargetExpression with " + element.getChildren().length + " children");
            }
            node = element.getNode().getFirstChildNode();
        } else {
            node = element.getNode();
        }
        return expectIdentifier(node);
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

    private static Space concatSpace(Space first, Space second) {
        if (first.isEmpty()) return second;
        if (second.isEmpty()) return first;

        String whitespace = first.getWhitespace();
        List<Comment> comments = first.getComments();
        if (!second.getWhitespace().isEmpty()) {
            comments = ListUtils.mapLast(
                    comments,
                    comment -> comment.withSuffix(
                            comment.getSuffix() + second.getWhitespace()
                    )
            );
        }
        comments = ListUtils.concatAll(comments, second.getComments());

        return Space.build(whitespace, comments);
    }

    private static Space[] splitSpaceAtFirst(Space space, String splitAt) {
        final int whitespaceSplitIndex = space.getWhitespace().indexOf(splitAt);
        if (whitespaceSplitIndex >= 0) {
            Space before = Space.build(space.getWhitespace().substring(0, whitespaceSplitIndex + 1), emptyList());
            Space after = space.withWhitespace(
                    space.getWhitespace().substring(whitespaceSplitIndex + 1)
            );
            return new Space[]{before, after};
        } else {
            List<Comment> comments = space.getComments();
            for (int commentIndex = 0; commentIndex < comments.size(); commentIndex++) {
                Comment comment = comments.get(commentIndex);
                final int commentSplitIndex = comment.getSuffix().indexOf(splitAt);
                if (commentSplitIndex >= 0) {
                    Space after = space.withComments(
                            ListUtils.mapLast(
                                    comments.subList(0, commentIndex + 1),
                                    last -> last.withSuffix(last.getSuffix().substring(0, commentSplitIndex + 1))
                            ));
                    Space before = Space.build(
                            comment.getSuffix().substring(commentSplitIndex + 1),
                            comments.subList(commentIndex + 1, comments.size())
                    );
                    return new Space[]{before, after};
                }
            }
        }

        System.err.println(space);

        return new Space[]{space};
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

    private static Space appendWhitespace(Space space, String whitespace) {
        if (!space.getComments().isEmpty()) {
            return space.withComments(
                    ListUtils.mapFirst(
                            space.getComments(),
                            comment -> comment.withSuffix(comment.getSuffix() + whitespace)
                    )
            );
        } else {
            return space.withWhitespace(
                    space.getWhitespace() + whitespace
            );
        }
    }

    private static boolean isWhitespaceOrComment(@Nullable PsiElement element) {
        return element instanceof PsiComment || element instanceof PsiWhiteSpace;
    }
}
