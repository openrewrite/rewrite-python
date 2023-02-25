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
import org.openrewrite.python.tree.PContainer;
import org.openrewrite.python.tree.PRightPadded;
import org.openrewrite.python.tree.PSpace;
import org.openrewrite.python.tree.Py;
import org.openrewrite.python.tree.Py.Binary;
import org.openrewrite.python.tree.Py.CompilationUnit;

import java.util.List;
import java.util.function.UnaryOperator;

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
        CompilationUnit cu = (CompilationUnit) sourceFile;

        beforeSyntax(cu, Location.COMPILATION_UNIT_PREFIX, p);

//        visit(((CompilationUnit) sourceFile).getAnnotations(), p);

        for (JRightPadded<Import> imprt : cu.getPadding().getImports()) {
            visitRightPadded(imprt, PRightPadded.Location.TOP_LEVEL_STATEMENT_SUFFIX, p);
        }

        for (JRightPadded<Statement> statement : cu.getPadding().getStatements()) {
            visitRightPadded(statement, PRightPadded.Location.TOP_LEVEL_STATEMENT_SUFFIX, p);
        }

        visitSpace(cu.getEof(), Location.COMPILATION_UNIT_EOF, p);
        afterSyntax(cu, p);
        return cu;
    }

    @Override
    public J visitBinary(Binary binary, PrintOutputCapture<P> p) {
        return binary;
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
        public J visitClassDeclaration(J.ClassDeclaration classDecl, PrintOutputCapture<P> p) {
            beforeSyntax(classDecl, Space.Location.CLASS_DECLARATION_PREFIX, p);
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
        public J visitUnary(J.Unary unary, PrintOutputCapture<P> p) {
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
            }
            visit(unary.getExpression(), p);
            afterSyntax(unary, p);
            return unary;
        }
    }

    protected void visitStatement(@Nullable JRightPadded<Statement> paddedStat, JRightPadded.Location location, PrintOutputCapture<P> p) {
        if (paddedStat != null) {
            visit(paddedStat.getElement(), p);
            visitSpace(paddedStat.getAfter(), location.getAfterLocation(), p);
            visitMarkers(paddedStat.getMarkers(), p);
        }
    }

    private static final UnaryOperator<String> PYTHON_MARKER_WRAPPER =
            out -> "/*~~" + out + (out.isEmpty() ? "" : "~~") + ">*/";

    private void beforeSyntax(Py k, PSpace.Location loc, PrintOutputCapture<P> p) {
        beforeSyntax(k.getPrefix(), k.getMarkers(), loc, p);
    }

    private void beforeSyntax(Space prefix, Markers markers, @Nullable PSpace.Location loc, PrintOutputCapture<P> p) {
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
    public Space visitSpace(Space space, PSpace.Location loc, PrintOutputCapture<P> p) {
        return delegate.visitSpace(space, Space.Location.LANGUAGE_EXTENSION, p);
    }

    @Override
    public Space visitSpace(Space space, Space.Location loc, PrintOutputCapture<P> p) {
        return delegate.visitSpace(space, loc, p);
    }

    protected void visitContainer(String before, @Nullable JContainer<? extends J> container, PContainer.Location location,
                                  String suffixBetween, @Nullable String after, PrintOutputCapture<P> p) {
        if (container == null) {
            return;
        }
        visitSpace(container.getBefore(), location.getBeforeLocation(), p);
        p.append(before);
        visitRightPadded(container.getPadding().getElements(), location.getElementLocation(), suffixBetween, p);
        p.append(after == null ? "" : after);
    }

    protected void visitRightPadded(List<? extends JRightPadded<? extends J>> nodes, PRightPadded.Location location, String suffixBetween, PrintOutputCapture<P> p) {
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
        beforeSyntax(pass, PSpace.Location.PASS_PREFIX, p);
        p.append("pass");
        afterSyntax(pass, p);
        return pass;
    }
}
