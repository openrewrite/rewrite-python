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
import com.intellij.psi.tree.IElementType;
import com.intellij.psi.util.QualifiedName;
import com.jetbrains.python.PyTokenTypes;
import com.jetbrains.python.psi.*;
import lombok.Value;
import org.jetbrains.annotations.NotNull;
import org.openrewrite.FileAttributes;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.marker.OmitParentheses;
import org.openrewrite.java.tree.*;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.marker.*;
import org.openrewrite.python.tree.Py;
import org.openrewrite.python.tree.PySpace;

import java.nio.charset.Charset;
import java.nio.file.Path;
import java.util.*;
import java.util.function.BiFunction;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static java.util.Objects.requireNonNull;
import static org.openrewrite.Tree.randomId;
import static org.openrewrite.marker.Markers.EMPTY;
import static org.openrewrite.python.internal.PsiUtils.*;
import static org.openrewrite.python.tree.PySpace.appendWhitespace;
import static org.openrewrite.python.tree.PySpace.deindent;

public class PsiPythonMapper {

    private final Path path;
    private final Charset charset;
    private final boolean isCharsetBomMarked;
    private final LanguageLevel languageLevel;

    public PsiPythonMapper(Path path,
                           Charset charset,
                           boolean isCharsetBomMarked,
                           LanguageLevel languageLevel) {
        this.path = path;
        this.charset = charset;
        this.isCharsetBomMarked = isCharsetBomMarked;
        this.languageLevel = languageLevel;
    }

    @Value
    public static class BlockContext {
        String fullIndent;
        boolean isInline;
        PsiPaddingCursor paddingCursor;

        public static BlockContext root(PyFile element) {
            PsiPaddingCursor paddingCursor = new PsiPaddingCursor(element);
            paddingCursor.resetTo(element.getNode().getFirstChildNode().getPsi());
            return new BlockContext("", false, paddingCursor);
        }

        public Space nextStatementPrefix() {
            return nextStatementPrefix(null);
        }

        public Space nextStatementPrefix(@Nullable PsiElement expected) {
            Space prefix = expected == null
                    ? paddingCursor.consumeRemaining()
                    : paddingCursor.consumeRemainingAndExpect(expected);
            return deindent(
                    prefix,
                    fullIndent,
                    PySpace.IndentStartMode.LINE_START,
                    PySpace.IndentEndMode.STATEMENT_START
            );
        }
    }

    public Py.CompilationUnit mapSource(String sourceText) {
        boolean addedNewline = false;
        if (!sourceText.endsWith("\n")) {
            addedNewline = true;
            sourceText = sourceText + "\n";
        }

        PyFile pyFile = IntelliJUtils.parsePythonSource(path.toString(), sourceText, languageLevel);
        if (pyFile == null) {
            throw new IllegalStateException("Unexpected null PyFile on source: " + path);
        }

        Py.CompilationUnit compilationUnit = mapFile(pyFile);
        if (addedNewline) {
            compilationUnit = compilationUnit.withMarkers(
                    compilationUnit.getMarkers().add(
                            new SuppressNewline(randomId())
                    )
            );
        }
        return compilationUnit;
    }

    public Py.CompilationUnit mapFile(PyFile element) {
        // Uncomment when doing development if you want a PSI tree to print out
        //  new IntelliJUtils.PsiPrinter().print(element.getNode());
        BlockContext ctx = BlockContext.root(element);
        List<Statement> statements = singletonList(
                mapBlock(element, null, element.getStatements(), ctx)
        );

        Markers markers = EMPTY;
        if (!element.getText().endsWith("\n")) {
            markers = Markers.build(singletonList(new SuppressNewline(randomId())));
        }

        Space eof = ctx.paddingCursor.consumeRemainingAndExpectEOF();

        return new Py.CompilationUnit(
                randomId(),
                Space.EMPTY,
                markers,
                path,
                FileAttributes.fromPath(path),
                charset.name(),
                isCharsetBomMarked,
                null,
                emptyList(),
                emptyList(),
                eof
        ).withStatements(statements);
    }

    public List<Statement> mapStatement(PsiElement element, BlockContext ctx) {
        try {
            if (element instanceof PyClass) {
                return singletonList(mapClassDeclarationStatement((PyClass) element, ctx));
            } else if (element instanceof PyForStatement) {
                return singletonList(mapForStatement((PyForStatement) element, ctx));
            } else if (element instanceof PyFunction) {
                return singletonList(mapFunction((PyFunction) element, ctx));
            } else if (element instanceof PyIfStatement) {
                return singletonList(mapIfStatement((PyIfStatement) element, ctx));
            } else if (element instanceof PyMatchStatement) {
                return singletonList(mapMatchStatement((PyMatchStatement) element, ctx));
            } else if (element instanceof PyTryExceptStatement) {
                return singletonList(mapTry((PyTryExceptStatement) element, ctx));
            } else if (element instanceof PyWhileStatement) {
                return singletonList(mapWhile((PyWhileStatement) element, ctx));
            } else if (element instanceof PyWithStatement) {
                return singletonList(mapWithStatement((PyWithStatement) element, ctx));
            }
        } catch (Exception e) {
            throw new RuntimeException(
                    String.format(
                            "error processing compound statement of type %s in:\n--\n%s\n--",
                            element.getClass().getSimpleName(),
                            element.getText()
                    ),
                    e
            );
        }

        return mapSimpleStatement(element);
    }

    private List<Statement> mapSimpleStatement(PsiElement element) {
        try {
            if (element instanceof PyAugAssignmentStatement) {
                return singletonList(mapAugAssignmentStatement((PyAugAssignmentStatement) element));
            } else if (element instanceof PyAssertStatement) {
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
            } else if (element instanceof PyPrintStatement) {
                return singletonList(mapPrintStatement((PyPrintStatement) element));
            } else if (element instanceof PyRaiseStatement) {
                return singletonList(mapRaiseStatement((PyRaiseStatement) element));
            } else if (element instanceof PyReturnStatement) {
                return singletonList(mapReturnStatement((PyReturnStatement) element));
            } else if (element instanceof PyTypeDeclarationStatement) {
                return singletonList(mapTypeDeclarationStatement((PyTypeDeclarationStatement) element));
            } else {
                throw new IllegalArgumentException("unknown PSI element type " + element.getNode().getElementType());
            }
        } catch (Exception e) {
            throw new RuntimeException(
                    String.format(
                            "error processing compound statement of type %s in:\n--\n%s\n--",
                            element.getClass().getSimpleName(),
                            element.getText()
                    ),
                    e
            );
        }
    }

    private J.VariableDeclarations mapTypeDeclarationStatement(PyTypeDeclarationStatement element) {
        return new J.VariableDeclarations(
                randomId(),
                Space.EMPTY,
                EMPTY,
                emptyList(),
                emptyList(),
                mapTypeHint(Objects.requireNonNull(element.getAnnotation())),
                null,
                emptyList(),
                singletonList(JRightPadded.build(new J.VariableDeclarations.NamedVariable(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        expectIdentifier(element.getTarget()),
                        emptyList(),
                        null,
                        null
                )))
        );
    }

    private J.MethodInvocation mapPrintStatement(PyPrintStatement element) {
        PsiElement print = findChildToken(element, PyTokenTypes.PRINT_KEYWORD);
        Markers markers = EMPTY.addIfAbsent(new OmitParentheses(randomId()));

        JContainer<Expression> args = JContainer.build(Space.EMPTY, element.getChildren().length == 0 ?
                singletonList(JRightPadded.build(new J.Empty(randomId(), Space.EMPTY, EMPTY))) :
                mapExpressionsAsRightPadded(element.getChildren()), EMPTY);

        return new J.MethodInvocation(
                randomId(),
                spaceBefore(print),
                markers,
                null,
                null,
                new J.Identifier(randomId(), Space.EMPTY, EMPTY, print.getText(), null, null),
                args,
                null
        );
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
                    import_ -> import_.withMarkers(import_.getMarkers().add(new GroupedStatement(randomId(), groupId)))
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
                        statement = statement.withMarkers(statement.getMarkers().addIfAbsent(new ImportParens(randomId())));
                        return statement;
                    }
            );
        }

        return imports;
    }

    private J.Import mapImportElement(PyImportElement element, PyImportStatementBase parent, @Nullable Expression importSource) {
        PsiElement importKeyword = findChildToken(parent, PyTokenTypes.IMPORT_KEYWORD);

        //  from math import ceil      or      import ceil
        //                  ^^^^^                    ^^^^^
        NameTree importNameExpr = mapQualifiedNameAsNameTree(
                requireNonNull(element.getImportReferenceExpression()).asQualifiedName()
        ).withPrefix(spaceBefore(element));

        J.FieldAccess fieldAccess;
        if (importSource == null) {
            // import ...
            fieldAccess = new J.FieldAccess(
                    randomId(),
                    Space.EMPTY,
                    EMPTY,
                    (Expression) importNameExpr,
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
                    JLeftPadded.build((J.Identifier) importNameExpr)
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

    private Statement mapMatchStatement(PyMatchStatement element, BlockContext ctx) {
        Space prefix = ctx.nextStatementPrefix(element);
        JRightPadded<Expression> subject = mapExpressionAsRightPadded(requireNonNull(element.getSubject()));
        J.Block block = this.mapBlock(
                element,
                findChildToken(element, PyTokenTypes.COLON),
                element.getCaseClauses(),
                ctx,
                (clause, innerCtx) -> singletonList(mapCaseClause(clause, innerCtx))
        );
        return new J.Switch(
                randomId(),
                prefix,
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

    private Statement mapCaseClause(PyCaseClause element, BlockContext ctx) {
        Space prefix = ctx.nextStatementPrefix(element);

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

        J.Block block = mapCompoundBlock(element, ctx);
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


    private Statement mapWhile(PyWhileStatement element, BlockContext ctx) {
        Space prefix = ctx.nextStatementPrefix(element);
        return new J.WhileLoop(
                randomId(),
                prefix,
                EMPTY,
                new J.ControlParentheses<>(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        JRightPadded.build(mapExpression(element.getWhilePart().getCondition()))
                ),
                JRightPadded.build(mapCompoundBlock(element.getWhilePart(), ctx))
        );
    }

    private Statement mapTry(PyTryExceptStatement element, BlockContext ctx) {
        Space tryPrefix = ctx.nextStatementPrefix(element);
        J.Block tryBlock = mapCompoundBlock(element.getTryPart(), ctx);

        List<J.Try.Catch> catches = emptyList();
        if (element.getExceptParts().length > 0) {
            catches = new ArrayList<>(element.getExceptParts().length);
            for (PyExceptPart pyExceptPart : element.getExceptParts()) {
                catches.add(mapExcept(pyExceptPart, ctx));
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
            Space elsePrefix = ctx.nextStatementPrefix(element.getElsePart());
            tryBlock = tryBlock.getPadding().withStatements(
                    ListUtils.concat(
                            tryBlock.getPadding().getStatements(),
                            JRightPadded.<Statement>build(
                                    mapCompoundBlock(element.getElsePart(), ctx)
                            ).withAfter(elsePrefix)
                    )
            );
        }

        JLeftPadded<J.Block> finally_ = null;
        if (element.getFinallyPart() != null) {
            Space finallyPrefix = ctx.nextStatementPrefix(element.getFinallyPart());
            finally_ = JLeftPadded.build(
                    mapCompoundBlock(element.getFinallyPart(), ctx)
            ).withBefore(finallyPrefix);
        }

        return new J.Try(
                randomId(),
                tryPrefix,
                EMPTY,
                null,
                tryBlock,
                catches,
                finally_
        );
    }

    private J.Try.Catch mapExcept(PyExceptPart element, BlockContext ctx) {
        Space exceptPrefix = ctx.nextStatementPrefix(element);

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
                mapCompoundBlock(element, ctx)
        );
    }

    private Statement mapWithStatement(PyWithStatement element, BlockContext ctx) {
        Space statementPrefix = ctx.nextStatementPrefix();

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
            @Nullable PsiElement asToken = maybeFindChildToken(pyWithItem, PyTokenTypes.AS_KEYWORD);

            Expression variable;
            if (pyWithItem.getTarget() != null) {
                variable = mapExpression(pyWithItem.getTarget())
                        .withPrefix(spaceAfter(asToken));
            } else {
                variable = new J.Empty(randomId(), Space.EMPTY, EMPTY);
            }

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
                statementPrefix,
                EMPTY,
                JContainer.build(resources),
                mapCompoundBlock(element, ctx),
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

    private Statement mapForStatement(PyForStatement element, BlockContext ctx) {
        Space prefix = ctx.nextStatementPrefix(element);
        PyForPart forPart = element.getForPart();
        J.VariableDeclarations target = mapAsVariableDeclarations(requireNonNull(forPart.getTarget()));

        final Statement loop = new J.ForEachLoop(
                randomId(),
                prefix,
                EMPTY,
                new J.ForEachLoop.Control(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        JRightPadded.build(target)
                                .withAfter(spaceAfter(forPart.getTarget())),
                        JRightPadded.build(mapExpression(forPart.getSource()))
                ),
                JRightPadded.build(mapCompoundBlock(forPart, ctx))
        );

        if (element.getElsePart() != null) {
            Space elsePrefix = ctx.nextStatementPrefix(element.getElsePart());
            return new Py.TrailingElseWrapper(
                    randomId(),
                    Space.EMPTY,
                    EMPTY,
                    loop,
                    JLeftPadded.build(mapCompoundBlock(element.getElsePart(), ctx)).withBefore(elsePrefix)
            );
        } else {
            return loop;
        }
    }

    private J.VariableDeclarations mapAsVariableDeclarations(PyExpression pyExpression) {
        if (pyExpression instanceof PyTargetExpression) {
            return mapTargetExpressionAsVariableDeclarations((PyTargetExpression) pyExpression);
        } else if (pyExpression instanceof PyTupleExpression) {
            return mapTupleAsVariableDeclarations((PyTupleExpression) pyExpression);
        } else {
            return new J.VariableDeclarations(
                    randomId(),
                    spaceBefore(pyExpression),
                    EMPTY,
                    emptyList(),
                    emptyList(),
                    null,
                    null,
                    emptyList(),
                    singletonList(
                            JRightPadded.build(mapAssignmentTarget(pyExpression).withPrefix(Space.EMPTY))
                    )
            );
        }
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
        PyExpression[] pyTargets = element.getElements();

        for (PyExpression pyExpression : pyTargets) {
            namedVariables.add(JRightPadded.build(
                    mapAssignmentTarget(pyExpression)
            ).withAfter(spaceBefore(pyExpression.getNextSibling())));
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

    private J.VariableDeclarations.NamedVariable mapAssignmentTarget(PyExpression pyExpression) {
        J.Identifier name;
        @Nullable JLeftPadded<Expression> initializer;

        Expression mapped = mapExpression(pyExpression).withPrefix(Space.EMPTY);
        if (mapped instanceof J.Identifier) {
            name = (J.Identifier) mapped;
            initializer = null;
        } else {
            name = new J.Identifier(randomId(), Space.EMPTY, EMPTY, "", null, null);
            initializer = JLeftPadded.build(mapped);
        }

        return new J.VariableDeclarations.NamedVariable(
                randomId(),
                spaceBefore(pyExpression),
                EMPTY,
                name,
                emptyList(),
                initializer,
                null
        );
    }

    private Statement mapFunction(PyFunction element, BlockContext ctx) {
        List<J.Annotation> annotations = mapDecoratorList(element.getDecoratorList(), ctx);

        JContainer<Statement> params;
        PsiElement rParen = maybeFindChildToken(element.getParameterList(), PyTokenTypes.RPAR);
        Space after = rParen == null ? Space.EMPTY : spaceBefore(rParen);
        if (element.getParameterList().getParameters().length == 0) {
            params = JContainer.build(spaceAfter(element.getNameIdentifier()),
                    singletonList(JRightPadded.build(new J.Empty(randomId(), after, EMPTY))), EMPTY);
        } else {
            PyParameter @NotNull [] pyParameters = element.getParameterList().getParameters();
            List<JRightPadded<Statement>> statements = new ArrayList<>(pyParameters.length);
            for (int i = 0; i < pyParameters.length; i++) {
                PyParameter parameter = pyParameters[i];
                statements.add(
                        JRightPadded.<Statement>build(
                                mapFunctionParameter(parameter).withPrefix(spaceBefore(parameter))
                        ).withAfter(i < pyParameters.length - 1 ? spaceAfter(parameter) : after)
                );
            }
            params = JContainer.build(spaceAfter(element.getNameIdentifier()), statements, EMPTY);
        }

        List<J.Modifier> modifiers = new ArrayList<>();

        PsiElement asyncToken = maybeFindChildToken(element, PyTokenTypes.ASYNC_KEYWORD);
        if (asyncToken != null) {
            modifiers.add(new J.Modifier(
                    randomId(),
                    spaceBefore(asyncToken),
                    EMPTY,
                    J.Modifier.Type.Async,
                    emptyList()
            ));
        }

        PsiElement defToken = findChildToken(element, PyTokenTypes.DEF_KEYWORD);
        modifiers.add(new J.Modifier(
                randomId(),
                spaceBefore(defToken),
                EMPTY,
                J.Modifier.Type.Default, // as in "def"
                emptyList()
        ));

        Space firstModifierPrefix = ctx.nextStatementPrefix();
        modifiers = ListUtils.mapFirst(modifiers, mod -> mod.withPrefix(firstModifierPrefix));

        return new J.MethodDeclaration(
                randomId(),
                Space.EMPTY,
                EMPTY,
                annotations,
                modifiers,
                null,
                mapTypeHintNullable(element.getAnnotation()),
                new J.MethodDeclaration.IdentifierWithAnnotations(
                        mapIdentifier(element).withPrefix(spaceBefore(element.getNameIdentifier())),
                        emptyList()
                ),
                params,
                null,
                mapCompoundBlock(element, ctx),
                null,
                null
        );
    }

    private Statement mapFunctionParameter(PyElement element) {
        J.Identifier name;
        Py.SpecialParameter.Kind specialParamKind;
        JLeftPadded<Expression> defaultValue;
        Py.TypeHint typeHint;

        if (element instanceof PyNamedParameter) {
            PyNamedParameter namedParameter = (PyNamedParameter) element;
            name = expectIdentifier(namedParameter.getNameIdentifier());
            typeHint = mapTypeHintNullable(namedParameter.getAnnotation());

            if (namedParameter.isKeywordContainer()) {
                specialParamKind = Py.SpecialParameter.Kind.KWARGS;
            } else if (namedParameter.isPositionalContainer()) {
                specialParamKind = Py.SpecialParameter.Kind.ARGS;
            } else {
                specialParamKind = null;
            }

            defaultValue = null;
            if (namedParameter.hasDefaultValue()) {
                defaultValue = JLeftPadded.build(
                        mapExpression(namedParameter.getDefaultValue())
                ).withBefore(spaceBefore(namedParameter.getDefaultValue()));
            }
        } else if (element instanceof PySingleStarParameter) {
            specialParamKind = Py.SpecialParameter.Kind.ARGS;

            name = new J.Identifier(randomId(), Space.EMPTY, EMPTY, "", null, null);
            defaultValue = null;
            typeHint = null;
        } else {
            throw new IllegalArgumentException(String.format(
                    "expected function parameter to be a NamedParameter or StarArgument; found: %s\n%s",
                    element.getClass().getSimpleName(),
                    element.getText()
            ));
        }

        TypeTree type;
        {
            if (specialParamKind != null) {
                type = new Py.SpecialParameter(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        specialParamKind,
                        typeHint,
                        null
                );
            } else {
                type = typeHint;
            }
        }

        return new J.VariableDeclarations(
                randomId(),
                Space.EMPTY,
                EMPTY,
                emptyList(),
                emptyList(),
                type,
                null,
                emptyList(),
                singletonList(JRightPadded.build(new J.VariableDeclarations.NamedVariable(
                        randomId(),
                        Space.EMPTY,
                        EMPTY,
                        name,
                        emptyList(),
                        defaultValue,
                        null
                )))
        );

    }

    public Statement mapAssertStatement(PyAssertStatement element) {
        return new Py.AssertStatement(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpressionsAsRightPadded(element.getArguments())
        );
    }

    private static final Map<IElementType, J.AssignmentOperation.Type> augAssignmentOps;

    static {
        Map<PyElementType, J.AssignmentOperation.Type> map = new HashMap<>();
        map.put(PyTokenTypes.PLUSEQ, J.AssignmentOperation.Type.Addition);
        map.put(PyTokenTypes.MINUSEQ, J.AssignmentOperation.Type.Subtraction);
        map.put(PyTokenTypes.ATEQ, J.AssignmentOperation.Type.MatrixMultiplication);
        map.put(PyTokenTypes.MULTEQ, J.AssignmentOperation.Type.Multiplication);
        map.put(PyTokenTypes.DIVEQ, J.AssignmentOperation.Type.Division);
        map.put(PyTokenTypes.PERCEQ, J.AssignmentOperation.Type.Modulo);
        map.put(PyTokenTypes.ANDEQ, J.AssignmentOperation.Type.BitAnd);
        map.put(PyTokenTypes.OREQ, J.AssignmentOperation.Type.BitOr);
        map.put(PyTokenTypes.XOREQ, J.AssignmentOperation.Type.BitXor);
        map.put(PyTokenTypes.LTLTEQ, J.AssignmentOperation.Type.LeftShift);
        map.put(PyTokenTypes.GTGTEQ, J.AssignmentOperation.Type.RightShift);
        map.put(PyTokenTypes.EXPEQ, J.AssignmentOperation.Type.Exponentiation);
        map.put(PyTokenTypes.FLOORDIVEQ, J.AssignmentOperation.Type.FloorDivision);
        augAssignmentOps = Collections.unmodifiableMap(map);
    }


    public Statement mapAugAssignmentStatement(PyAugAssignmentStatement element) {
        PyExpression pyLhs = element.getTarget();
        PyExpression pyRhs = element.getValue();

        Expression lhs = mapExpression(pyLhs);
        Expression rhs = mapExpression(pyRhs).withPrefix(spaceBefore(pyRhs));

        IElementType pyOp = element.getOperation().getNode().getElementType();
        J.AssignmentOperation.Type type = augAssignmentOps.get(pyOp);

        return new J.AssignmentOperation(
                randomId(),
                spaceBefore(element),
                EMPTY,
                lhs,
                JLeftPadded.build(type).withBefore(spaceAfter(pyLhs)),
                rhs,
                null
        );
    }


    public Statement mapAssignmentStatement(PyAssignmentStatement element) {
        PyExpression pyLhs = element.getLeftHandSideExpression();
        PyExpression pyRhs = element.getAssignedValue();
        PsiElement equalsToken = findChildToken(element, PyTokenTypes.EQ);

        Expression lhs = mapExpression(pyLhs);
        JLeftPadded<Expression> rhs =
                JLeftPadded.<Expression>build(mapExpression(pyRhs).withPrefix(spaceAfter(equalsToken)))
                        .withBefore(spaceBefore(equalsToken));

        return new J.Assignment(
                randomId(),
                spaceBefore(element),
                EMPTY,
                lhs,
                rhs,
                null
        );
    }

    public Expression mapAssignmentExpression(PyAssignmentExpression element) {
        PyExpression pyLhs = element.getTarget();
        PyExpression pyRhs = element.getAssignedValue();

        Expression lhs = mapExpression(pyLhs);
        Expression rhs = mapExpression(pyRhs).withPrefix(spaceBefore(pyRhs));

        return new J.Assignment(
                randomId(),
                spaceBefore(element),
                EMPTY,
                lhs,
                JLeftPadded.build(rhs).withBefore(spaceAfter(pyLhs)),
                null
        );
    }

    public Statement mapClassDeclarationStatement(PyClass element, BlockContext ctx) {
        List<J.Annotation> decorators = mapDecoratorList(element.getDecoratorList(), ctx);

        final Space kindPrefix = ctx.nextStatementPrefix(
                findChildToken(element, PyTokenTypes.CLASS_KEYWORD)
        );
        J.ClassDeclaration.Kind kind = new J.ClassDeclaration.Kind(
                randomId(),
                kindPrefix,
                EMPTY,
                decorators,
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

        return new J.ClassDeclaration(
                randomId(),
                // the prefix is currently either embedded in the decorators or in the `kind`
                Space.EMPTY,
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
                mapCompoundBlock(element, ctx),
                null
        );
    }

    public J.Annotation mapDecorator(PyDecorator pyDecorator) {
        NameTree name = mapQualifiedNameAsNameTree(requireNonNull(pyDecorator.getQualifiedName()));

        JContainer<Expression> arguments = mapArgumentList(pyDecorator.getArgumentList());

        return new J.Annotation(
                randomId(),
                Space.EMPTY,
                EMPTY,
                name,
                arguments
        );
    }

    public List<J.Annotation> mapDecoratorList(@Nullable PyDecoratorList pyDecoratorList, BlockContext ctx) {
        if (pyDecoratorList == null || pyDecoratorList.getDecorators().length == 0) {
            return emptyList();
        }
        PyDecorator[] pyDecorators = pyDecoratorList.getDecorators();
        List<J.Annotation> decorators = new ArrayList<>(pyDecorators.length);
        for (PyDecorator pyDecorator : pyDecorators) {
            J.Annotation mapped = mapDecorator(pyDecorator);

            Space prefix = ctx.nextStatementPrefix(pyDecorator);
            mapped = mapped.withPrefix(prefix);

            ctx.paddingCursor.resetToSpaceAfter(pyDecorator);
            Space suffix = ctx.paddingCursor.consumeUntilExpectedNewline();
            suffix = deindent(
                    suffix,
                    ctx.fullIndent,
                    PySpace.IndentStartMode.AFTER_STATEMENT,
                    PySpace.IndentEndMode.REST_OF_LINE
            );

            mapped = PythonExtraPadding.set(mapped, PythonExtraPadding.Location.AFTER_DECORATOR, suffix);

            decorators.add(mapped);
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

    public Statement mapIfStatement(PyIfStatement element, BlockContext ctx) {
        Space ifPrefix = ctx.nextStatementPrefix();

        PyExpression pyIfCondition = element.getIfPart().getCondition();
        if (pyIfCondition == null) {
            throw new RuntimeException("if condition is null");
        }

        Statement ifBody = mapCompoundBlock(element.getIfPart(), ctx);
        J.If.Else elsePart = mapElsePart(element, 0, ctx);

        return new J.If(
                randomId(),
                ifPrefix,
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
    private J.If.Else mapElsePart(PyIfStatement parent, int elifIndex, BlockContext ctx) {
        if (elifIndex < parent.getElifParts().length) {
            PyIfPart pyElifPart = parent.getElifParts()[elifIndex];

            PyExpression pyIfCondition = pyElifPart.getCondition();
            if (pyIfCondition == null) {
                throw new RuntimeException("if condition is null");
            }

            Space prefix = ctx.nextStatementPrefix(pyElifPart);
            J.Block thenPart = mapCompoundBlock(pyElifPart, ctx);
            J.If.Else elsePart = mapElsePart(parent, elifIndex + 1, ctx);

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
            Space prefix = ctx.nextStatementPrefix(parent.getElsePart());
            J.Block elsePart = mapCompoundBlock(parent.getElsePart(), ctx);
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
            BlockContext ctx
    ) {
        return mapBlock(container, colonToken, pyStatements, ctx, this::mapStatement);
    }

    public <T extends PsiElement> J.Block mapBlock(
            PsiElement container,
            @Nullable PsiElement colonToken,
            List<T> pyStatements,
            BlockContext outerCtx,
            BiFunction<T, BlockContext, List<? extends Statement>> mapFn
    ) {
        PsiPaddingCursor paddingCursor = outerCtx.paddingCursor;
        List<JRightPadded<Statement>> statements = new ArrayList<>(pyStatements.size());

        @Nullable Space blockPrefix;
        BlockContext innerCtx;

        if (colonToken != null) {
            blockPrefix = paddingCursor.consumeUntilNewlineOrRollback();
            if (blockPrefix == null) {
                blockPrefix = Space.EMPTY;
            }
            paddingCursor.resetToSpaceAfter(colonToken);

            Space firstPrefix = paddingCursor.withRollback(paddingCursor::consumeRemaining);
            final String containerIndent = outerCtx.fullIndent;
            final String fullIndent = firstPrefix.getIndent();
            if (!fullIndent.startsWith(containerIndent)) {
                throw new IllegalStateException(String.format(
                        "expected full block indent (%s) to start with container indent (%s)",
                        Space.build(fullIndent, emptyList()),
                        Space.build(containerIndent, emptyList())
                ));
            }
            String blockIndent = fullIndent.substring(containerIndent.length());
            blockPrefix = appendWhitespace(blockPrefix, "\n" + blockIndent);

            innerCtx = new BlockContext(fullIndent, false, paddingCursor);
        } else {
            blockPrefix = appendWhitespace(paddingCursor.consumeRemaining(), "\n");
            innerCtx = new BlockContext("", true, paddingCursor);
        }

        boolean precededBySemicolon = false;
        for (T pyStatement : pyStatements) {
            List<? extends Statement> mapped = mapFn.apply(pyStatement, innerCtx);

            @Nullable Space prefix;
            Space after;
            @Nullable JRightPadded<Statement> maybeEmptyStatement = null;
            @Nullable PsiElement semicolon;
            if (paddingCursor.isPast(pyStatement)) {
                // parsed a compound statement containing a block
                prefix = null;
                // the block must eventually contain a simple statement, so it's already newline-terminated
                after = Space.EMPTY;
                semicolon = null;
            } else {
                // parsed a simple statement.
                prefix = paddingCursor.consumeRemainingAndExpect(pyStatement);

                // a simple statement like `x=1; y=2` has the semicolon as a child of the statement
                semicolon = maybeFindChildToken(pyStatement, PyTokenTypes.SEMICOLON);

                // in single-line compound statements, like `def foo(x): return x;`, the parser stores the
                // semicolon as a sibling to the statement in the argument list
                if (semicolon == null) {
                    PsiElement maybeSemicolon = nextSiblingSkipWhitespace(pyStatement);
                    if (isLeafToken(maybeSemicolon, PyTokenTypes.SEMICOLON)) {
                        semicolon = maybeSemicolon;
                    }
                }

                if (semicolon != null) {
                    paddingCursor.resetToSpaceBefore(semicolon);
                    after = paddingCursor.consumeRemainingAndExpect(semicolon);
                    paddingCursor.resetToSpaceAfter(semicolon);

                    // if there is a newline following the semicolon, we need an empty statement.
                    // semicolons are statement delimiters, not statement terminators.
                    maybeEmptyStatement = paddingCursor.consumeUntilNewlineOrRollback(
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

                if (!precededBySemicolon) {
                    prefix = PySpace.deindent(
                            prefix,
                            innerCtx.fullIndent,
                            PySpace.IndentStartMode.LINE_START,
                            PySpace.IndentEndMode.STATEMENT_START
                    );
                }
            }

            /*
              There is usually only one statement returned.
              In the unusual case that there's more than one, every statement gets the same padding.
            */
            for (Statement statement : mapped) {
                if (prefix != null) {
                    statement = statement.withPrefix(prefix);
                }
                statements.add(JRightPadded.build(statement).withAfter(after));
            }

            if (maybeEmptyStatement != null) {
                statements.add(maybeEmptyStatement);
            }

            precededBySemicolon = semicolon != null && maybeEmptyStatement == null;
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
    public J.Block mapCompoundBlock(PyStatementListContainer pyElement, BlockContext ctx) {
        return mapBlock(
                pyElement,
                findChildToken(pyElement, PyTokenTypes.COLON),
                Arrays.asList(pyElement.getStatementList().getStatements()),
                ctx
        );
    }

    public Expression mapExpression(@Nullable PsiElement element) {
        if (element == null) {
            //noinspection DataFlowIssue
            return null;
        }

        try {
            if (element instanceof LeafPsiElement && isLeafToken(element, PyTokenTypes.IDENTIFIER)) {
                return expectIdentifier(element);
            }

            if (element instanceof PyPattern) {
                return mapPattern((PyPattern) element);
            }

            if (element instanceof PyAssignmentExpression) {
                return mapAssignmentExpression((PyAssignmentExpression) element);
            } else if (element instanceof PyBinaryExpression) {
                return mapBinaryExpression((PyBinaryExpression) element);
            } else if (element instanceof PyBoolLiteralExpression) {
                return mapBooleanLiteral((PyBoolLiteralExpression) element);
            } else if (element instanceof PyCallExpression) {
                return mapCallExpression((PyCallExpression) element);
            } else if (element instanceof PyComprehensionElement) {
                return mapComprehensionElement((PyComprehensionElement) element);
            } else if (element instanceof PyConditionalExpression) {
                return mapConditionalExpression((PyConditionalExpression) element);
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
            } else if (element instanceof PyStarArgument) {
                return mapStarArgument((PyStarArgument) element);
            } else if (element instanceof PyStarExpression) {
                return mapStarExpression((PyStarExpression) element);
            } else if (element instanceof PySubscriptionExpression) {
                return mapSubscription((PySubscriptionExpression) element);
            } else if (element instanceof PyStringLiteralExpression) {
                return mapStringLiteral((PyStringLiteralExpression) element);
            } else if (element instanceof PyTargetExpression) {
                return mapTargetExpression((PyTargetExpression) element);
            } else if (element instanceof PyTupleExpression) {
                return mapTupleLiteral((PyTupleExpression) element);
            } else if (element instanceof PyYieldExpression) {
                return mapYieldExpression((PyYieldExpression) element);
            } else {
                throw new IllegalArgumentException("unknown PSI element type " + element.getNode().getElementType());
            }
        } catch (Exception e) {
            throw new RuntimeException(
                    String.format(
                            "error processing expression of type %s in:\n--\n%s\n--",
                            element.getClass().getSimpleName(),
                            element.getText()
                    ),
                    e
            );
        }
    }

    private Expression mapStarArgument(PyStarArgument element) {
        return new Py.SpecialArgument(
                randomId(),
                spaceBefore(element),
                EMPTY,
                element.isKeyword()
                        ? Py.SpecialArgument.Kind.KWARGS
                        : Py.SpecialArgument.Kind.ARGS,
                mapExpression(element.getLastChild()),
                null
        );
    }

    private Expression mapStarExpression(PyStarExpression element) {
        return new Py.SpecialArgument(
                randomId(),
                spaceBefore(element),
                EMPTY,
                Py.SpecialArgument.Kind.ARGS,
                mapExpression(element.getLastChild()),
                null
        );
    }

    private Expression mapConditionalExpression(PyConditionalExpression element) {
        return new J.Ternary(
                randomId(),
                spaceBefore(element),
                EMPTY,
                mapExpression(element.getCondition()),
                new JLeftPadded<>(
                        spaceBefore(findChildToken(element, PyTokenTypes.IF_KEYWORD)),
                        mapExpression(element.getTruePart()),
                        EMPTY
                ),
                new JLeftPadded<>(
                        spaceBefore(findChildToken(element, PyTokenTypes.ELSE_KEYWORD)),
                        mapExpression(element.getFalsePart()),
                        EMPTY
                ),
                null
        );
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
            PsiElement openToken = maybeFindFirstChildToken(pattern, PyTokenTypes.LBRACKET, PyTokenTypes.LPAR);
            if (openToken == null) {
                kind = Py.MatchCase.Pattern.Kind.SEQUENCE;
            } else {
                kind = openToken.getNode().getElementType() == PyTokenTypes.LBRACKET
                        ? Py.MatchCase.Pattern.Kind.SEQUENCE_LIST
                        : Py.MatchCase.Pattern.Kind.SEQUENCE_TUPLE;
            }
            children = JContainer.build(
                    spaceAfter(openToken),
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
            throw new IllegalArgumentException(
                    String.format("unhandled case pattern of type %s", pattern.getClass().getSimpleName())
            );
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

    private @Nullable Py.TypeHint mapTypeHintNullable(@Nullable PyAnnotation element) {
        if (element == null) return null;
        return mapTypeHint(element);
    }

    private Py.TypeHint mapTypeHint(PyAnnotation element) {
        Py.TypeHint.Kind kind;
        {
            IElementType kindToken = element.getNode().getFirstChildNode().getElementType();
            if (kindToken == PyTokenTypes.RARROW) {
                kind = Py.TypeHint.Kind.RETURN_TYPE;
            } else if (kindToken == PyTokenTypes.COLON) {
                kind = Py.TypeHint.Kind.VARIABLE_TYPE;
            } else {
                throw new IllegalArgumentException(String.format(
                        "unrecognized type hint start token: %s",
                        kindToken
                ));
            }
        }

        return new Py.TypeHint(
                randomId(),
                spaceBefore(element),
                EMPTY,
                kind,
                mapExpression(element.getValue()),
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
        Markers markers = Markers.build(singletonList(new BuiltinDesugar(randomId())));
        if (
                !(element.getParent() instanceof PyParenthesizedExpression)
                        && maybeFindChildToken(element, PyTokenTypes.LPAR) == null
        ) {
            markers = markers.add(new OmitParentheses(randomId()));
        }

        J.Identifier builtins = makeBuiltinsIdentifier();
        JContainer<Expression> args = JContainer.build(singletonList(
                JRightPadded.build(mapSequenceExpressionAsArray(element))
        )).withBefore(spaceBefore(element));
        return new J.MethodInvocation(
                randomId(),
                spaceBefore(element),
                markers,
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

        PyExpression pyExpression = element.getExpression();
        List<JRightPadded<Expression>> expressions;
        if (pyExpression == null) {
            expressions = emptyList();
        } else if (pyExpression instanceof PyTupleExpression) {
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
        return new Py.NamedArgument(
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
        // keep in sync with `PythonOperatorLookup`
        Map<PyElementType, String> map = new HashMap<>();
        map.put(PyTokenTypes.EQEQ, "__eq__");
        map.put(PyTokenTypes.NE, "__ne__");
        map.put(PyTokenTypes.EXP, "__pow__");
        map.put(PyTokenTypes.FLOORDIV, "__floordiv__");
        map.put(PyTokenTypes.IN_KEYWORD, "__contains__");
        map.put(PyTokenTypes.AT, "__matmul__");
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
        map.put(PyTokenTypes.PERC, J.Binary.Type.Modulo);

        map.put(PyTokenTypes.OR_KEYWORD, J.Binary.Type.Or);
        map.put(PyTokenTypes.AND_KEYWORD, J.Binary.Type.And);

        map.put(PyTokenTypes.AND, J.Binary.Type.BitAnd);
        map.put(PyTokenTypes.OR, J.Binary.Type.BitOr);
        map.put(PyTokenTypes.XOR, J.Binary.Type.BitXor);
        map.put(PyTokenTypes.GTGT, J.Binary.Type.RightShift);
        map.put(PyTokenTypes.LTLT, J.Binary.Type.LeftShift);

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
            throw new IllegalArgumentException(
                    String.format("unhandled prefix expression with type %s", op)
            );
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

    public Expression mapTargetExpression(PyTargetExpression element) {
        Py.TypeHint typeHint = mapTypeHintNullable(element.getAnnotation());
        Expression typeTree = TypeTree.build(element.getText());
        typeTree = typeTree.withPrefix(spaceBefore(element));

        if (typeHint == null) {
            return typeTree;
        } else {
            return new Py.TypeHintedExpression(
                    randomId(),
                    spaceBefore(element),
                    EMPTY,
                    typeHint,
                    typeTree,
                    null
            );
        }
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
                element.isIntegerLiteral()
                        ? element.getLongValue()
                        : element.getBigDecimalValue(),
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
            throw new UnsupportedOperationException("only simple names are supported; found: " + qualifiedName);
        }
        //noinspection DataFlowIssue
        return qualifiedName.getLastComponent();
    }

    private NameTree mapQualifiedNameAsNameTree(QualifiedName pyQualifiedName) {
        J.Identifier name = new J.Identifier(
                randomId(),
                Space.EMPTY,
                EMPTY,
                requireNonNull(pyQualifiedName.getLastComponent()),
                null,
                null
        );
        if (pyQualifiedName.getComponentCount() == 1) {
            return name;
        } else {
            NameTree inner = mapQualifiedNameAsNameTree(pyQualifiedName.removeLastComponent());
            if (!(inner instanceof Expression)) {
                throw new IllegalStateException("expected qualified name to be both NameTree and Expression; found: " + inner.getClass().getSimpleName());
            }
            return new J.FieldAccess(
                    randomId(),
                    Space.EMPTY,
                    EMPTY,
                    (Expression) inner,
                    JLeftPadded.build(name),
                    null
            );
        }
    }

}
