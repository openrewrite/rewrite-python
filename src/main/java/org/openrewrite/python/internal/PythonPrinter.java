/*
 * Copyright 2023 the original author or authors.
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

import org.openrewrite.Cursor;
import org.openrewrite.PrintOutputCapture;
import org.openrewrite.Tree;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.JavaPrinter;
import org.openrewrite.java.JavaVisitor;
import org.openrewrite.java.marker.OmitParentheses;
import org.openrewrite.java.tree.*;
import org.openrewrite.java.tree.J.Import;
import org.openrewrite.java.tree.Space.Location;
import org.openrewrite.marker.Marker;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.PythonVisitor;
import org.openrewrite.python.marker.*;
import org.openrewrite.python.tree.*;

import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.UnaryOperator;

import static java.util.Objects.requireNonNull;
import static org.openrewrite.python.marker.GroupedStatement.StatementGroup;

public class PythonPrinter<P> extends PythonVisitor<PrintOutputCapture<P>> {

    private static final String STATEMENT_GROUP_CURSOR_KEY = "STATEMENT_GROUP";
    private static final String STATEMENT_GROUP_INDEX_CURSOR_KEY = "STATEMENT_GROUP_INDEX";

    private final PythonJavaPrinter delegate = new PythonJavaPrinter();

    @Override
    public J visit(@Nullable Tree tree, PrintOutputCapture<P> p) {
        if (!(tree instanceof Py)) {
            // re-route printing to the java printer
            return delegate.visit(tree, p);
        } else {
            return super.visit(tree, p);
        }
    }

    @Override
    public J visitJavaSourceFile(JavaSourceFile sourceFile, PrintOutputCapture<P> p) {
        Py.CompilationUnit cu = (Py.CompilationUnit) sourceFile;
        beforeSyntax(cu, Location.COMPILATION_UNIT_PREFIX, p);
        for (JRightPadded<Import> anImport : cu.getPadding().getImports()) {
            visitRightPadded(anImport, PyRightPadded.Location.TOP_LEVEL_STATEMENT_SUFFIX, p);
        }
        for (JRightPadded<Statement> statement : cu.getPadding().getStatements()) {
            visitRightPadded(statement, PyRightPadded.Location.TOP_LEVEL_STATEMENT_SUFFIX, p);
        }
        visitSpace(cu.getEof(), Location.COMPILATION_UNIT_EOF, p);
        afterSyntax(cu, p);
        return cu;
    }

    @Override
    public J visitDictLiteral(Py.DictLiteral dict, PrintOutputCapture<P> p) {
        beforeSyntax(dict, PySpace.Location.DICT_LITERAL_PREFIX, p);
        if (dict.getElements().isEmpty()) {
            p.append("{");
            visitPythonExtraPadding(dict, PythonExtraPadding.Location.EMPTY_INITIALIZER, p);
            p.append("}");
        } else {
            visitContainer("{", dict.getPadding().getElements(), PyContainer.Location.DICT_LITERAL_ELEMENTS, ",", "}", p);
        }
        afterSyntax(dict, p);
        return dict;
    }

    @Override
    public J visitKeyValue(Py.KeyValue keyValue, PrintOutputCapture<P> p) {
        beforeSyntax(keyValue, PySpace.Location.KEY_VALUE_PREFIX, p);
        visitRightPadded(keyValue.getPadding().getKey(), PyRightPadded.Location.KEY_VALUE_KEY_SUFFIX, p);
        p.append(':');
        visit(keyValue.getValue(), p);
        afterSyntax(keyValue, p);
        return keyValue;
    }

    private class PythonJavaPrinter extends JavaPrinter<P> {
        @Override
        public J visit(@Nullable Tree tree, PrintOutputCapture<P> p) {
            if (tree instanceof Py) {
                // re-route printing back up to python
                return PythonPrinter.this.visit(tree, p);
            } else {
                return super.visit(tree, p);
            }
        }

        @Override
        public J visitBinary(J.Binary binary, PrintOutputCapture<P> p) {
            String keyword = "";
            switch (binary.getOperator()) {
                case Addition:
                    keyword = "+";
                    break;
                case Subtraction:
                    keyword = "-";
                    break;
                case Multiplication:
                    keyword = "*";
                    break;
                case Division:
                    keyword = "/";
                    break;
                case Modulo:
                    keyword = "%";
                    break;
                case LessThan:
                    keyword = "<";
                    break;
                case GreaterThan:
                    keyword = ">";
                    break;
                case LessThanOrEqual:
                    keyword = "<=";
                    break;
                case GreaterThanOrEqual:
                    keyword = ">=";
                    break;
                case Equal:
                    keyword = "is";
                    break;
                case NotEqual:
                    keyword = "is not";
                    break;
                case BitAnd:
                    keyword = "&";
                    break;
                case BitOr:
                    keyword = "|";
                    break;
                case BitXor:
                    keyword = "^";
                    break;
                case LeftShift:
                    keyword = "<<";
                    break;
                case RightShift:
                    keyword = ">>";
                    break;
                case UnsignedRightShift:
                    keyword = ">>>";
                    break;
                case Or:
                    keyword = "or";
                    break;
                case And:
                    keyword = "and";
                    break;
            }
            beforeSyntax(binary, Space.Location.BINARY_PREFIX, p);
            visit(binary.getLeft(), p);
            visitSpace(binary.getPadding().getOperator().getBefore(), Space.Location.BINARY_OPERATOR, p);

            int spaceIndex = keyword.indexOf(' ');
            if (spaceIndex >= 0) {
                p.append(keyword.substring(0, spaceIndex));
                visitPythonExtraPadding(binary, PythonExtraPadding.Location.WITHIN_OPERATOR_NAME, p);
                p.append(keyword.substring(spaceIndex + 1));
            } else {
                p.append(keyword);
            }

            visit(binary.getRight(), p);
            afterSyntax(binary, p);
            return binary;
        }

        @Override
        public J visitClassDeclaration(J.ClassDeclaration classDecl, PrintOutputCapture<P> p) {
            beforeSyntax(classDecl, Space.Location.CLASS_DECLARATION_PREFIX, p);
            visitSpace(Space.EMPTY, Space.Location.ANNOTATIONS, p);
            visit(classDecl.getLeadingAnnotations(), p);
            visit(classDecl.getAnnotations().getKind().getAnnotations(), p);
            visitSpace(classDecl.getAnnotations().getKind().getPrefix(), Space.Location.CLASS_KIND, p);
            p.append("class");
            visit(classDecl.getName(), p);
            if (classDecl.getPadding().getImplements() != null) {
                boolean omitParens = classDecl.getPadding().getImplements().getMarkers().findFirst(OmitParentheses.class).isPresent();
                visitContainer(omitParens ? "" : "(", classDecl.getPadding().getImplements(), JContainer.Location.IMPLEMENTS,
                        ",", omitParens ? "" : ")", p);
            }
            visit(classDecl.getBody(), p);
            afterSyntax(classDecl, p);
            return classDecl;
        }

        @Override
        public <T extends J> J visitControlParentheses(J.ControlParentheses<T> controlParens, PrintOutputCapture<P> p) {
            beforeSyntax(controlParens, Space.Location.CONTROL_PARENTHESES_PREFIX, p);
            visitRightPadded(controlParens.getPadding().getTree(), JRightPadded.Location.PARENTHESES, "", p);
            afterSyntax(controlParens, p);
            return controlParens;
        }

        @Override
        public J visitElse(J.If.Else elze, PrintOutputCapture<P> p) {
            beforeSyntax(elze, Space.Location.ELSE_PREFIX, p);
            if (getCursor().getParentTreeCursor().getValue() instanceof J.If &&
                    elze.getBody() instanceof J.If) {
                p.append("el");
            } else {
                p.append("else");
            }
            visitStatement(elze.getPadding().getBody(), JRightPadded.Location.IF_ELSE, p);
            afterSyntax(elze, p);
            return elze;
        }

        @Override
        public J visitBlock(J.Block block, PrintOutputCapture<P> p) {
            // blocks in Python are just collections of statements with no additional formatting
            beforeSyntax(block, Space.Location.BLOCK_PREFIX, p);
            if (getCursor().getParentTreeCursor().getValue() != Cursor.ROOT_VALUE) {
                p.append(":");
            }
            visitStatements(block.getPadding().getStatements(), JRightPadded.Location.BLOCK_STATEMENT, p);
            visitSpace(block.getEnd(), Space.Location.BLOCK_END, p);
            afterSyntax(block, p);
            return block;
        }


        @Override
        protected void visitStatements(List<JRightPadded<Statement>> statements, JRightPadded.Location location, PrintOutputCapture<P> p) {
            boolean inSingleLineStatementList = false;
            @Nullable StatementGroup<Statement> statementGroup = null;
            for (int i = 0; i < statements.size(); i++) {
                JRightPadded<Statement> paddedStat = statements.get(i);
                if (statementGroup == null || !statementGroup.containsIndex(i)) {
                    statementGroup = GroupedStatement.findCurrentStatementGroup(statements, i);
                    getCursor().putMessage(STATEMENT_GROUP_CURSOR_KEY, statementGroup == null ? null : statementGroup.getStatements());
                }
                getCursor().putMessage(STATEMENT_GROUP_INDEX_CURSOR_KEY, statementGroup == null ? null : i - statementGroup.getFirstIndex());

                if (statementGroup == null || !statementGroup.containsIndex(i + 1)) {
                    if (inSingleLineStatementList) {
                        p.append(";");
                    }
                    visitStatement(paddedStat, location, p);
                    inSingleLineStatementList = !paddedStat.getAfter().getLastWhitespace().endsWith("\n");
                } else {
                    visit(paddedStat.getElement(), p);
                }
            }
        }

        @Override
        public J visitForEachLoop(J.ForEachLoop forEachLoop, PrintOutputCapture<P> p) {
            beforeSyntax(forEachLoop, Space.Location.FOR_EACH_LOOP_PREFIX, p);
            p.append("for");
            visit(forEachLoop.getControl(), p);
            visit(forEachLoop.getBody(), p);
            afterSyntax(forEachLoop, p);
            return forEachLoop;
        }

        @Override
        public J visitForEachControl(J.ForEachLoop.Control control, PrintOutputCapture<P> p) {
            beforeSyntax(control, Space.Location.FOR_EACH_CONTROL_PREFIX, p);
            visitRightPadded(control.getPadding().getVariable(), JRightPadded.Location.FOREACH_VARIABLE, p);
            p.append("in");
            visitRightPadded(control.getPadding().getIterable(), JRightPadded.Location.FOREACH_ITERABLE, p);
            afterSyntax(control, p);
            return control;
        }

        @Override
        public J visitLiteral(J.Literal literal, PrintOutputCapture<P> p) {
            if (literal.getValue() == null) {
                if (literal.getMarkers().findFirst(ImplicitNone.class).isPresent()) {
                    super.visitLiteral(literal.withValueSource(""), p);
                } else {
                    super.visitLiteral(literal.withValueSource("None"), p);
                }
                return literal;
            } else {
                return super.visitLiteral(literal, p);
            }
        }

        @Override
        public J visitMethodDeclaration(J.MethodDeclaration method, PrintOutputCapture<P> p) {
            beforeSyntax(method, Space.Location.METHOD_DECLARATION_PREFIX, p);
            visitSpace(Space.EMPTY, Space.Location.ANNOTATIONS, p);
            visit(method.getLeadingAnnotations(), p);
            visit(method.getReturnTypeExpression(), p);
            p.append("def");
            visit(method.getName(), p);
            visitContainer("(", method.getPadding().getParameters(), JContainer.Location.METHOD_DECLARATION_PARAMETERS, ",", ")", p);
            visit(method.getBody(), p);
            afterSyntax(method, p);
            return method;
        }

        private void visitMagicMethodDesugar(J.MethodInvocation method, boolean negate, PrintOutputCapture<P> p) {
            String magicMethodName = method.getSimpleName();

            if ("__call__".equals(magicMethodName)) {
                beforeSyntax(method, Space.Location.METHOD_INVOCATION_PREFIX, p);
                visitRightPadded(method.getPadding().getSelect(), JRightPadded.Location.METHOD_SELECT, p);
                visitContainer("(", method.getPadding().getArguments(), JContainer.Location.METHOD_INVOCATION_ARGUMENTS, ",", ")", p);
                afterSyntax(method, p);

                return;
            }

            if (method.getArguments().size() != 1) {
                throw new IllegalStateException(String.format(
                        "expected de-sugared magic method call `%s` to have exactly one argument; found %d",
                        magicMethodName,
                        method.getArguments().size()
                ));
            }

            String operator = PythonOperatorLookup.operatorForMagicMethod(magicMethodName);
            if (operator == null) {
                throw new IllegalStateException(String.format(
                        "expected method call `%s` to be a de-sugared operator, but it does not match known operators",
                        magicMethodName
                ));
            }

            if (negate) {
                if (!"in".equals(operator)) {
                    throw new IllegalStateException(String.format(
                            "found method call `%s` as a de-sugared operator, but it is marked as negated (which it does not support)",
                            magicMethodName
                    ));
                }
            }

            boolean reverseOperandOrder = PythonOperatorLookup.doesMagicMethodReverseOperands(magicMethodName);

            Expression lhs = requireNonNull(method.getSelect());
            Expression rhs = method.getArguments().get(0);

            J.MethodInvocation.Padding padding = method.getPadding();
            Space beforeOperator = requireNonNull(padding.getSelect()).getAfter();
            Space afterOperator = rhs.getPrefix();

            if (reverseOperandOrder) {
                Expression tmp = lhs;
                lhs = rhs;
                rhs = tmp;
            }

            beforeSyntax(method, Space.Location.BINARY_PREFIX, p);
            visit((Expression) lhs.withPrefix(Space.EMPTY), p);
            visitSpace(beforeOperator, Space.Location.BINARY_OPERATOR, p);
            if (negate) {
                p.append("not");
                visitPythonExtraPadding(method, PythonExtraPadding.Location.WITHIN_OPERATOR_NAME, p);
            }
            p.append(operator);
            visit((Expression) rhs.withPrefix(afterOperator), p);
            afterSyntax(method, p);
        }

        private void visitBuiltinDesugar(J.MethodInvocation method, PrintOutputCapture<P> p) {
            Expression select = method.getSelect();
            if (!(select instanceof J.Identifier)) {
                throw new IllegalStateException("expected builtin desugar to select from an Identifier");
            } else if (!"__builtins__".equals(((J.Identifier) select).getSimpleName())) {
                throw new IllegalStateException("expected builtin desugar to select from __builtins__");
            }

            visitSpace(method.getPrefix(), Location.LANGUAGE_EXTENSION, p);

            String builtinName = requireNonNull(method.getName()).getSimpleName();
            switch (builtinName) {
                case "slice":
                    super.visitContainer(
                            "",
                            method.getPadding().getArguments(),
                            JContainer.Location.LANGUAGE_EXTENSION,
                            ":",
                            "",
                            p
                    );
                    return;
                case "set":
                case "tuple": {
                    if (method.getArguments().size() != 1) {
                        throw new IllegalStateException(String.format("builtin `%s` should have exactly one argument", builtinName));
                    }
                    Expression arg = method.getArguments().get(0);
                    if (!(arg instanceof J.NewArray)) {
                        throw new IllegalStateException(String.format("builtin `%s` should have exactly one argument, a J.NewArray", builtinName));
                    }

                    J.NewArray argList = (J.NewArray) arg;
                    int argCount = 0;
                    for (Expression argExpr : requireNonNull(argList.getInitializer())) {
                        if (!(argExpr instanceof J.Empty)) {
                            argCount++;
                        }
                    }

                    String before;
                    String after;
                    if ("set".equals(builtinName)) {
                        before = "{";
                        after = "}";
                    } else {
                        before = "(";
                        after = argCount == 1 ? ",)" : ")";
                    }

                    super.visitContainer(
                            before,
                            argList.getPadding().getInitializer(),
                            JContainer.Location.LANGUAGE_EXTENSION,
                            ",",
                            after,
                            p
                    );
                    return;
                }
                default:
                    throw new IllegalStateException(
                            String.format("builtin desugar doesn't support `%s`", builtinName)
                    );
            }
        }

        @Override
        public J visitMethodInvocation(J.MethodInvocation method, PrintOutputCapture<P> p) {
            if (method.getMarkers().findFirst(MagicMethodDesugar.class).isPresent()) {
                visitMagicMethodDesugar(method, false, p);
                return method;
            } else if (method.getMarkers().findFirst(BuiltinDesugar.class).isPresent()) {
                visitBuiltinDesugar(method, p);
                return method;
            } else {
                return super.visitMethodInvocation(method, p);
            }
        }


        @Override
        public J visitNewArray(J.NewArray newArray, PrintOutputCapture<P> p) {
            beforeSyntax(newArray, Space.Location.NEW_ARRAY_PREFIX, p);
            visitContainer("[", newArray.getPadding().getInitializer(), JContainer.Location.NEW_ARRAY_INITIALIZER, ",", "]", p);
            afterSyntax(newArray, p);
            return newArray;
        }

        @Override
        protected void visitStatement(@Nullable JRightPadded<Statement> paddedStat, JRightPadded.Location location, PrintOutputCapture<P> p) {
            if (paddedStat == null) {
                return;
            }
            visit(paddedStat.getElement(), p);
            visitSpace(paddedStat.getAfter(), location.getAfterLocation(), p);
        }

        @Override
        public J visitUnary(J.Unary unary, PrintOutputCapture<P> p) {
            if (unary.getMarkers().findFirst(MagicMethodDesugar.class).isPresent()) {
                if (unary.getOperator() != J.Unary.Type.Not) {
                    throw new IllegalStateException(String.format(
                            "found a unary operator (%s) marked as a magic method de-sugar, but only negation is supported",
                            unary.getOperator()
                    ));
                }
                Expression expression = unary.getExpression();
                while (expression instanceof J.Parentheses) {
                    expression = expression.unwrap();
                }
                if (!(expression instanceof J.MethodInvocation)) {
                    throw new IllegalStateException(String.format(
                            "found a unary operator (%s) marked as a magic method de-sugar, but its expression is not a magic method invocation",
                            unary.getOperator()
                    ));
                }
                visitMagicMethodDesugar((J.MethodInvocation) expression, true, p);
                return unary;
            }

            beforeSyntax(unary, Space.Location.UNARY_PREFIX, p);
            switch (unary.getOperator()) {
                case Not:
                    p.append("not");
                    break;
                case Positive:
                    p.append("+");
                    break;
                case Negative:
                    p.append("-");
                    break;
                case Complement:
                    p.append("~");
                    break;
            }
            visit(unary.getExpression(), p);
            afterSyntax(unary, p);
            return unary;
        }

        @Override
        public J visitImport(Import impoort, PrintOutputCapture<P> p) {
            List<Import> statementGroup = getCursor().getParentTreeCursor().getMessage(STATEMENT_GROUP_CURSOR_KEY);
            if (statementGroup != null) {
                Integer statementGroupIndex = getCursor().getParentTreeCursor().getMessage(STATEMENT_GROUP_INDEX_CURSOR_KEY);
                if (statementGroupIndex == null) {
                    throw new IllegalStateException();
                }
                if (statementGroupIndex != statementGroup.size() - 1) {
                    return impoort;
                }
            }

            if (statementGroup == null) {
                statementGroup = Collections.singletonList(impoort);
            }

            boolean hasNewline;
            {
                AtomicBoolean hasNewlineHolder = new AtomicBoolean(false);
                ContainsNewlineVisitor hasNewlineVisitor = new ContainsNewlineVisitor();
                for (Import inGroup : statementGroup) {
                    inGroup.acceptJava(hasNewlineVisitor, hasNewlineHolder);
                    if (hasNewlineHolder.get()) {
                        break;
                    }
                }
                hasNewline = hasNewlineHolder.get();
            }

            beforeSyntax(impoort, Space.Location.IMPORT_PREFIX, p);
            boolean isFrom = "".equals(impoort.getQualid().getSimpleName());
            if (isFrom) {
                p.append("import");
            } else {
                p.append("from");
                visit(impoort.getQualid().getTarget(), p);
                visitSpace(impoort.getQualid().getPadding().getName().getBefore(), Location.LANGUAGE_EXTENSION, p);
                p.append("import");
            }

            if (hasNewline) {
                visitPythonExtraPadding(impoort, PythonExtraPadding.Location.IMPORT_PARENS_PREFIX, p);
                p.append("(");
            }

            for (int i = 0; i < statementGroup.size(); i++) {
                Import inGroup = statementGroup.get(i);
                if (i != 0) {
                    p.append(",");
                }
                if (isFrom) {
                    visit(inGroup.getQualid().getTarget(), p);
                } else {
                    visit(inGroup.getQualid().getName(), p);
                }
                if (inGroup.getAlias() != null) {
                    visitSpace(inGroup.getPadding().getAlias().getBefore(), Space.Location.LANGUAGE_EXTENSION, p);
                    p.append("as");
                    visit(inGroup.getAlias(), p);
                }
            }

            if (hasNewline) {
                visitPythonExtraPadding(impoort, PythonExtraPadding.Location.IMPORT_PARENS_SUFFIX, p);
                p.append(")");
            }


            afterSyntax(impoort, p);
            return impoort;
        }
    }

    private void visitPythonExtraPadding(Tree tree, PythonExtraPadding.Location loc, PrintOutputCapture<P> p) {
        Space space = PythonExtraPadding.getOrDefault(tree, loc);
        if (space == null) {
            return;
        }
        visitSpace(
                space,
                Location.LANGUAGE_EXTENSION,
                p
        );
    }

    private static final UnaryOperator<String> PYTHON_MARKER_WRAPPER =
            out -> "/*~~" + out + (out.isEmpty() ? "" : "~~") + ">*/";

    private void beforeSyntax(Py k, PySpace.Location loc, PrintOutputCapture<P> p) {
        beforeSyntax(k.getPrefix(), k.getMarkers(), loc, p);
    }

    private void beforeSyntax(Space prefix, Markers markers, @Nullable PySpace.Location loc, PrintOutputCapture<P> p) {
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().beforePrefix(marker, new Cursor(getCursor(), marker), PYTHON_MARKER_WRAPPER));
        }
        if (loc != null) {
            visitSpace(prefix, loc, p);
        }
        visitMarkers(markers, p);
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().beforeSyntax(marker, new Cursor(getCursor(), marker), PYTHON_MARKER_WRAPPER));
        }
    }

    private void beforeSyntax(Py python, Location loc, PrintOutputCapture<P> p) {
        beforeSyntax(python.getPrefix(), python.getMarkers(), loc, p);
    }

    private void beforeSyntax(Space prefix, Markers markers, @Nullable Location loc, PrintOutputCapture<P> p) {
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().beforePrefix(marker, new Cursor(getCursor(), marker), PYTHON_MARKER_WRAPPER));
        }
        if (loc != null) {
            visitSpace(prefix, loc, p);
        }
        visitMarkers(markers, p);
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().beforeSyntax(marker, new Cursor(getCursor(), marker), PYTHON_MARKER_WRAPPER));
        }
    }

    private void afterSyntax(Py python, PrintOutputCapture<P> p) {
        afterSyntax(python.getMarkers(), p);
    }

    private void afterSyntax(Markers markers, PrintOutputCapture<P> p) {
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().afterSyntax(marker, new Cursor(getCursor(), marker), PYTHON_MARKER_WRAPPER));
        }
    }

    @Override
    public Space visitSpace(Space space, PySpace.Location loc, PrintOutputCapture<P> p) {
        return delegate.visitSpace(space, Space.Location.LANGUAGE_EXTENSION, p);
    }

    @Override
    public Space visitSpace(Space space, Space.Location loc, PrintOutputCapture<P> p) {
        return delegate.visitSpace(space, loc, p);
    }

    protected void visitContainer(String before, @Nullable JContainer<? extends J> container, PyContainer.Location location,
                                  String suffixBetween, @Nullable String after, PrintOutputCapture<P> p) {
        if (container == null) {
            return;
        }
        visitSpace(container.getBefore(), location.getBeforeLocation(), p);
        p.append(before);
        visitRightPadded(container.getPadding().getElements(), location.getElementLocation(), suffixBetween, p);
        p.append(after == null ? "" : after);
    }

    protected void visitRightPadded(List<? extends JRightPadded<? extends J>> nodes, PyRightPadded.Location location, String suffixBetween, PrintOutputCapture<P> p) {
        for (int i = 0; i < nodes.size(); i++) {
            JRightPadded<? extends J> node = nodes.get(i);
            visit(node.getElement(), p);
            visitSpace(node.getAfter(), location.getAfterLocation(), p);
            if (i < nodes.size() - 1) {
                p.append(suffixBetween);
            }
        }
    }

    @Override
    public J visitPassStatement(Py.PassStatement pass, PrintOutputCapture<P> p) {
        beforeSyntax(pass, PySpace.Location.PASS_PREFIX, p);
        p.append("pass");
        afterSyntax(pass, p);
        return pass;
    }

    @Override
    public J visitComprehensionExpression(Py.ComprehensionExpression comp, PrintOutputCapture<P> p) {
        beforeSyntax(comp, PySpace.Location.COMPREHENSION_PREFIX, p);
        String open;
        String close;
        switch (comp.getKind()) {
            case DICT:
            case SET:
                open = "{";
                close = "}";
                break;
            case LIST:
                open = "[";
                close = "]";
                break;
            case GENERATOR:
                open = "(";
                close = ")";
                break;
            default:
                throw new IllegalStateException();
        }

        p.append(open);
        visit(comp.getResult(), p);
        for (Py.ComprehensionExpression.Clause clause : comp.getClauses()) {
            visitComprehensionClause(clause, p);
        }
        visitSpace(comp.getSuffix(), PySpace.Location.COMPREHENSION_SUFFIX, p);
        p.append(close);

        afterSyntax(comp, p);
        return comp;
    }

    @Override
    public J visitComprehensionClause(Py.ComprehensionExpression.Clause clause, PrintOutputCapture<P> p) {
        visitSpace(clause.getPrefix(), PySpace.Location.COMPREHENSION_CLAUSE_PREFIX, p);
        p.append("for");
        visit(clause.getIteratorVariable(), p);
        visitSpace(clause.getPadding().getIteratedList().getBefore(), PySpace.Location.COMPREHENSION_IN, p);
        p.append("in");
        visit(clause.getIteratedList(), p);
        if (clause.getConditions() != null) {
            for (Py.ComprehensionExpression.Condition condition : clause.getConditions()) {
                visitComprehensionCondition(condition, p);
            }
        }
        return clause;
    }

    @Override
    public J visitComprehensionCondition(Py.ComprehensionExpression.Condition condition, PrintOutputCapture<P> p) {
        visitSpace(condition.getPrefix(), PySpace.Location.COMPREHENSION_CONDITION_PREFIX, p);
        p.append("if");
        visit(condition.getExpression(), p);
        return condition;
    }

    @Override
    public J visitAwaitExpression(Py.AwaitExpression await, PrintOutputCapture<P> p) {
        visitSpace(await.getPrefix(), PySpace.Location.AWAIT_PREFIX, p);
        p.append("await");
        visit(await.getExpression(), p);
        return await;
    }

    @Override
    public J visitAssertStatement(Py.AssertStatement assrt, PrintOutputCapture<P> p) {
        visitSpace(assrt.getPrefix(), PySpace.Location.ASSERT_PREFIX, p);
        p.append("assert");
        visitRightPadded(
                assrt.getPadding().getExpressions(),
                PyRightPadded.Location.ASSERT_ELEMENT,
                ",",
                p
        );
        return assrt;
    }

    @Override
    public J visitYieldExpression(Py.YieldExpression yield, PrintOutputCapture<P> p) {
        visitSpace(yield.getPrefix(), PySpace.Location.YIELD_PREFIX, p);
        p.append("yield");

        if (yield.isFrom()) {
            visitLeftPadded(yield.getPadding().getFrom(), PyLeftPadded.Location.YIELD_FROM, p);
            p.append("from");
        }

        visitRightPadded(
                yield.getPadding().getExpressions(),
                PyRightPadded.Location.YIELD_ELEMENT,
                ",",
                p
        );
        return yield;
    }

    @Override
    public J visitDelStatement(Py.DelStatement del, PrintOutputCapture<P> p) {
        visitSpace(del.getPrefix(), PySpace.Location.DEL_PREFIX, p);
        p.append("del");
        visitRightPadded(
                del.getPadding().getTargets(),
                PyRightPadded.Location.DEL_ELEMENT,
                ",",
                p
        );
        return del;
    }

    private static class ContainsNewlineVisitor extends JavaVisitor<AtomicBoolean> {
        @Override
        public Space visitSpace(Space space, Location loc, AtomicBoolean hasNewline) {
            space = super.visitSpace(space, loc, hasNewline);
            if (space.getWhitespace().contains("\n")) {
                hasNewline.set(true);
            } else if (!space.getComments().isEmpty()) {
                hasNewline.set(true);
            }
            return space;
        }

        @Override
        public J visitImport(Import impoort, AtomicBoolean hasNewline) {
            impoort = (Import) super.visitImport(impoort, hasNewline);
            visitLeftPadded(impoort.getPadding().getAlias(), JLeftPadded.Location.LANGUAGE_EXTENSION, hasNewline);
            return impoort;
        }
    }
}
