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
import org.openrewrite.java.marker.OmitParentheses;
import org.openrewrite.java.tree.*;
import org.openrewrite.java.tree.J.Import;
import org.openrewrite.java.tree.Space.Location;
import org.openrewrite.marker.Marker;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.PythonVisitor;
import org.openrewrite.python.marker.BuiltinDesugar;
import org.openrewrite.python.marker.ImplicitNone;
import org.openrewrite.python.marker.MagicMethodDesugar;
import org.openrewrite.python.tree.PyContainer;
import org.openrewrite.python.tree.PyRightPadded;
import org.openrewrite.python.tree.PySpace;
import org.openrewrite.python.tree.Py;

import java.util.List;
import java.util.function.UnaryOperator;

import static java.util.Objects.requireNonNull;

public class PythonPrinter<P> extends PythonVisitor<PrintOutputCapture<P>> {
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
        visitContainer("{", dict.getPadding().getElements(), PyContainer.Location.DICT_LITERAL_ELEMENTS, ",", "}", p);
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
            p.append(keyword);
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
            p.append(":");
            visitStatements(block.getPadding().getStatements(), JRightPadded.Location.BLOCK_STATEMENT, p);
            visitSpace(block.getEnd(), Space.Location.BLOCK_END, p);
            afterSyntax(block, p);
            return block;
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
                if (!operator.equals("in")) {
                    throw new IllegalStateException(String.format(
                            "found method call `%s` as a de-sugared operator, but it is marked as negated (which it does not support)",
                            magicMethodName
                    ));
                }
                operator = "not " + operator;
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
            p.append(operator);
            visit((Expression) rhs.withPrefix(afterOperator), p);
            afterSyntax(method, p);
        }

        private void visitBuiltinDesugar(J.MethodInvocation method, PrintOutputCapture<P> p) {
            Expression select = method.getSelect();
            if (!(select instanceof J.Identifier)) {
                throw new IllegalStateException("expected builtin desugar to select from an Identifier");
            } else if (!((J.Identifier) select).getSimpleName().equals("__builtins__")) {
                throw new IllegalStateException("expected builtin desugar to select from __builtins__");
            }

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
}
