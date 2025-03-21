/*
 * Copyright 2024 the original author or authors.
 * <p>
 * Licensed under the Moderne Source Available License (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * https://docs.moderne.io/licensing/moderne-source-available-license
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.openrewrite.python.internal;

import org.jspecify.annotations.Nullable;
import org.openrewrite.Cursor;
import org.openrewrite.PrintOutputCapture;
import org.openrewrite.Tree;
import org.openrewrite.java.JavaPrinter;
import org.openrewrite.java.marker.OmitParentheses;
import org.openrewrite.java.marker.Semicolon;
import org.openrewrite.java.marker.TrailingComma;
import org.openrewrite.java.tree.*;
import org.openrewrite.java.tree.J.Import;
import org.openrewrite.java.tree.Space.Location;
import org.openrewrite.marker.Marker;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.PythonVisitor;
import org.openrewrite.python.marker.KeywordArguments;
import org.openrewrite.python.marker.KeywordOnlyArguments;
import org.openrewrite.python.marker.Quoted;
import org.openrewrite.python.marker.SuppressNewline;
import org.openrewrite.python.tree.*;

import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import java.util.function.UnaryOperator;

import static java.util.Objects.requireNonNull;

public class PythonPrinter<P> extends PythonVisitor<PrintOutputCapture<P>> {
    private final PythonJavaPrinter delegate = new PythonJavaPrinter();

    @Override
    public J visit(@Nullable Tree tree, PrintOutputCapture<P> p) {
        if (!(tree instanceof Py)) {
            // re-route printing to the Java printer
            return delegate.visitNonNull(requireNonNull(tree), p);
        } else {
            //noinspection DataFlowIssue
            return super.visit(tree, p);
        }
    }

    @Override
    public void setCursor(@Nullable Cursor cursor) {
        super.setCursor(cursor);
        delegate.internalSetCursor(cursor);
    }

    private void internalSetCursor(@Nullable Cursor cursor) {
        super.setCursor(cursor);
    }

    @Override
    public J visitCompilationUnit(Py.CompilationUnit cu, PrintOutputCapture<P> p) {
        beforeSyntax(cu, Location.COMPILATION_UNIT_PREFIX, p);
        for (JRightPadded<Import> anImport : cu.getPadding().getImports()) {
            visitRightPadded(anImport, PyRightPadded.Location.TOP_LEVEL_STATEMENT_SUFFIX, p);
        }
        for (JRightPadded<Statement> statement : cu.getPadding().getStatements()) {
            visitRightPadded(statement, PyRightPadded.Location.TOP_LEVEL_STATEMENT_SUFFIX, p);
        }

        visitSpace(cu.getEof(), Location.COMPILATION_UNIT_EOF, p);
        if (cu.getMarkers().findFirst(SuppressNewline.class).isPresent()) {
            if (lastCharIs(p, '\n')) {
                p.out.setLength(p.out.length() - 1);
            }
        }
        afterSyntax(cu, p);
        return cu;
    }

    @Override
    public J visitBinary(Py.Binary binary, PrintOutputCapture<P> p) {
        beforeSyntax(binary, PySpace.Location.BINARY_PREFIX, p);
        visit(binary.getLeft(), p);
        visitSpace(binary.getPadding().getOperator().getBefore(), PySpace.Location.BINARY_OPERATOR, p);

        switch (binary.getOperator()) {
            case NotIn:
                p.append("not");
                if (binary.getNegation() != null) {
                    visitSpace(binary.getNegation(), PySpace.Location.BINARY_NEGATION, p);
                } else {
                    p.append(' ');
                }
                p.append("in");
                break;
            case In:
                p.append("in");
                break;
            case Is:
                p.append("is");
                break;
            case IsNot:
                p.append("is");
                if (binary.getNegation() != null) {
                    visitSpace(binary.getNegation(), PySpace.Location.BINARY_NEGATION, p);
                } else {
                    p.append(' ');
                }
                p.append("not");
                break;
            case FloorDivision:
                p.append("//");
                break;
            case MatrixMultiplication:
                p.append("@");
                break;
            case Power:
                p.append("**");
                break;
            case StringConcatenation:
                // empty
                break;
        }

        visit(binary.getRight(), p);
        afterSyntax(binary, p);
        return binary;
    }

    @Override
    public J visitChainedAssignment(Py.ChainedAssignment chainedAssignment, PrintOutputCapture<P> p) {
        beforeSyntax(chainedAssignment, PySpace.Location.CHAINED_ASSIGNMENT_PREFIX, p);
        visitRightPadded(chainedAssignment.getPadding().getVariables(), PyRightPadded.Location.CHAINED_ASSIGNMENT_VARIABLES, "=", p);
        p.append('=');
        visit(chainedAssignment.getAssignment(), p);
        afterSyntax(chainedAssignment, p);
        return chainedAssignment;
    }

    @Override
    public J visitCollectionLiteral(Py.CollectionLiteral coll, PrintOutputCapture<P> p) {
        beforeSyntax(coll, PySpace.Location.COLLECTION_LITERAL_PREFIX, p);
        JContainer<Expression> elements = coll.getPadding().getElements();
        switch (coll.getKind()) {
            case LIST:
                visitContainer("[", elements, PyContainer.Location.COLLECTION_LITERAL_ELEMENTS, ",", "]", p);
                break;
            case SET:
                visitContainer("{", elements, PyContainer.Location.COLLECTION_LITERAL_ELEMENTS, ",", "}", p);
                break;
            case TUPLE:
                if (elements.getMarkers().findFirst(OmitParentheses.class).isPresent()) {
                    visitContainer("", elements, PyContainer.Location.COLLECTION_LITERAL_ELEMENTS, ",", "", p);
                } else {
                    visitContainer("(", elements, PyContainer.Location.COLLECTION_LITERAL_ELEMENTS, ",", ")", p);
                }
                break;
        }
        afterSyntax(coll, p);
        return coll;
    }

    @Override
    public J visitDictLiteral(Py.DictLiteral dict, PrintOutputCapture<P> p) {
        beforeSyntax(dict, PySpace.Location.DICT_LITERAL_PREFIX, p);
        visitContainer("{", dict.getPadding().getElements(), PyContainer.Location.DICT_LITERAL_ELEMENTS, ",", "}", p);
        afterSyntax(dict, p);
        return dict;
    }

    @Override
    public J visitForLoop(Py.ForLoop forLoop, PrintOutputCapture<P> p) {
        beforeSyntax(forLoop, PySpace.Location.FOR_LOOP_PREFIX, p);
        p.append("for");
        visit(forLoop.getTarget(), p);
        visitLeftPadded("in", forLoop.getPadding().getIterable(), PyLeftPadded.Location.FOR_LOOP_ITERABLE, p);
        visitRightPadded(forLoop.getPadding().getBody(), PyRightPadded.Location.FOR_LOOP_BODY, p);
        return forLoop;
    }

    @Override
    public J visitFormattedString(Py.FormattedString fString, PrintOutputCapture<P> p) {
        beforeSyntax(fString, PySpace.Location.FORMATTED_STRING_PREFIX, p);
        p.append(fString.getDelimiter());
        visit(fString.getParts(), p);
        if (!fString.getDelimiter().isEmpty()) {
            int idx = Math.max(fString.getDelimiter().indexOf('\''), fString.getDelimiter().indexOf('"'));
            p.append(fString.getDelimiter().substring(idx));
        }
        return fString;
    }

    @Override
    public J visitFormattedStringValue(Py.FormattedString.Value value, PrintOutputCapture<P> p) {
        beforeSyntax(value, PySpace.Location.FORMATTED_STRING_VALUE_PREFIX, p);
        p.append('{');
        visitRightPadded(value.getPadding().getExpression(), PyRightPadded.Location.FORMATTED_STRING_VALUE_EXPRESSION, p);
        if (value.getPadding().getDebug() != null) {
            p.append('=');
            visitSpace(value.getPadding().getDebug().getAfter(), PySpace.Location.FORMATTED_STRING_VALUE_DEBUG_SUFFIX, p);
        }
        if (value.getConversion() != null) {
            p.append('!');
            switch (value.getConversion()) {
                case STR:
                    p.append('s');
                    break;
                case REPR:
                    p.append('r');
                    break;
                case ASCII:
                    p.append('a');
                    break;
            }
        }
        if (value.getFormat() != null) {
            p.append(':');
            visit(value.getFormat(), p);
        }
        p.append('}');
        return value;
    }

    @Override
    public J visitMultiImport(Py.MultiImport multiImport_, PrintOutputCapture<P> p) {
        beforeSyntax(multiImport_, PySpace.Location.MULTI_IMPORT_PREFIX, p);
        if (multiImport_.getFrom() != null) {
            p.append("from");
            visitRightPadded(multiImport_.getPadding().getFrom(), PyRightPadded.Location.MULTI_IMPORT_FROM, p);
        }
        p.append("import");
        if (multiImport_.isParenthesized()) {
            visitContainer("(", multiImport_.getPadding().getNames(), PyContainer.Location.MULTI_IMPORT_NAMES, ",", ")", p);
        } else {
            visitContainer("", multiImport_.getPadding().getNames(), PyContainer.Location.MULTI_IMPORT_NAMES, ",", "", p);
        }
        afterSyntax(multiImport_, p);
        return multiImport_;
    }

    @Override
    public J visitKeyValue(Py.KeyValue keyValue, PrintOutputCapture<P> p) {
        beforeSyntax(keyValue, PySpace.Location.KEY_VALUE_PREFIX, p);
        visitRightPadded(keyValue.getPadding().getKey(), PyRightPadded.Location.KEY_VALUE_KEY, p);
        p.append(':');
        visit(keyValue.getValue(), p);
        afterSyntax(keyValue, p);
        return keyValue;
    }

    @Override
    public J visitPass(Py.Pass pass, PrintOutputCapture<P> p) {
        beforeSyntax(pass, PySpace.Location.PASS_PREFIX, p);
        p.append("pass");
        afterSyntax(pass, p);
        return pass;
    }

    @Override
    public J visitComprehensionExpression(Py.ComprehensionExpression comp, PrintOutputCapture<P> p) {
        beforeSyntax(comp, PySpace.Location.COMPREHENSION_EXPRESSION_PREFIX, p);
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
                if (comp.getMarkers().findFirst(OmitParentheses.class).isPresent()) {
                    open = "";
                    close = "";
                } else {
                    open = "(";
                    close = ")";
                }
                break;
            default:
                throw new IllegalStateException();
        }

        p.append(open);
        visit(comp.getResult(), p);
        for (Py.ComprehensionExpression.Clause clause : comp.getClauses()) {
            visit(clause, p);
        }
        visitSpace(comp.getSuffix(), PySpace.Location.COMPREHENSION_EXPRESSION_SUFFIX, p);
        p.append(close);

        afterSyntax(comp, p);
        return comp;
    }

    @Override
    public J visitComprehensionClause(Py.ComprehensionExpression.Clause clause, PrintOutputCapture<P> p) {
        beforeSyntax(clause, PySpace.Location.COMPREHENSION_EXPRESSION_CLAUSE_PREFIX, p);
        if (clause.isAsync()) {
            p.append("async");
            visitSpace(clause.getPadding().getAsync().getAfter(), PySpace.Location.COMPREHENSION_EXPRESSION_CLAUSE_ASYNC_SUFFIX, p);
        }
        p.append("for");
        visit(clause.getIteratorVariable(), p);
        visitSpace(clause.getPadding().getIteratedList().getBefore(), PySpace.Location.COMPREHENSION_EXPRESSION_CLAUSE_ITERATED_LIST, p);
        p.append("in");
        visit(clause.getIteratedList(), p);
        if (clause.getConditions() != null) {
            for (Py.ComprehensionExpression.Condition condition : clause.getConditions()) {
                visit(condition, p);
            }
        }
        return clause;
    }

    @Override
    public J visitComprehensionCondition(Py.ComprehensionExpression.Condition condition, PrintOutputCapture<P> p) {
        beforeSyntax(condition, PySpace.Location.COMPREHENSION_EXPRESSION_CONDITION_PREFIX, p);
        p.append("if");
        visit(condition.getExpression(), p);
        return condition;
    }

    @Override
    public J visitAsync(Py.Async async, PrintOutputCapture<P> p) {
        beforeSyntax(async, PySpace.Location.ASYNC_PREFIX, p);
        p.append("async");
        visit(async.getStatement(), p);
        return async;
    }

    @Override
    public J visitAwait(Py.Await await, PrintOutputCapture<P> p) {
        beforeSyntax(await, PySpace.Location.AWAIT_PREFIX, p);
        p.append("await");
        visit(await.getExpression(), p);
        return await;
    }

    @Override
    public J visitYieldFrom(Py.YieldFrom yield, PrintOutputCapture<P> p) {
        beforeSyntax(yield, PySpace.Location.YIELD_FROM_PREFIX, p);
        p.append("from");
        visit(yield.getExpression(), p);
        return yield;
    }

    @Override
    public J visitVariableScope(Py.VariableScope scope, PrintOutputCapture<P> p) {
        beforeSyntax(scope, PySpace.Location.VARIABLE_SCOPE_PREFIX, p);
        switch (scope.getKind()) {
            case GLOBAL:
                p.append("global");
                break;
            case NONLOCAL:
                p.append("nonlocal");
                break;
        }

        visitRightPadded(
                scope.getPadding().getNames(),
                PyRightPadded.Location.VARIABLE_SCOPE_NAMES,
                ",",
                p
        );
        return scope;
    }

    @Override
    public J visitDel(Py.Del del, PrintOutputCapture<P> p) {
        beforeSyntax(del, PySpace.Location.DEL_PREFIX, p);
        p.append("del");
        visitRightPadded(
                del.getPadding().getTargets(),
                PyRightPadded.Location.DEL_TARGETS,
                ",",
                p
        );
        return del;
    }

    @Override
    public J visitExceptionType(Py.ExceptionType type, PrintOutputCapture<P> p) {
        beforeSyntax(type, PySpace.Location.EXCEPTION_TYPE_PREFIX, p);
        if (type.isExceptionGroup()) {
            p.append("*");
        }
        visit(type.getExpression(), p);
        return type;
    }

    @Override
    public J visitErrorFrom(Py.ErrorFrom expr, PrintOutputCapture<P> p) {
        beforeSyntax(expr, PySpace.Location.ERROR_FROM_PREFIX, p);
        visit(expr.getError(), p);
        visitSpace(expr.getPadding().getFrom().getBefore(), PySpace.Location.ERROR_FROM_SOURCE, p);
        p.append("from");
        visit(expr.getFrom(), p);
        return expr;
    }

    @Override
    public J visitLiteralType(Py.LiteralType literalType, PrintOutputCapture<P> p) {
        beforeSyntax(literalType, PySpace.Location.LITERAL_TYPE_PREFIX, p);
        visit(literalType.getLiteral(), p);
        afterSyntax(literalType, p);
        return literalType;
    }

    @Override
    public J visitMatchCase(Py.MatchCase match, PrintOutputCapture<P> p) {
        beforeSyntax(match, PySpace.Location.MATCH_CASE_PREFIX, p);
        visit(match.getPattern(), p);
        if (match.getPadding().getGuard() != null) {
            visitSpace(match.getPadding().getGuard().getBefore(), PySpace.Location.MATCH_CASE_GUARD, p);
            p.append("if");
            visit(match.getGuard(), p);
        }
        return match;
    }

    @Override
    public J visitMatchCasePattern(Py.MatchCase.Pattern pattern, PrintOutputCapture<P> p) {
        beforeSyntax(pattern, PySpace.Location.MATCH_CASE_PATTERN_PREFIX, p);
        JContainer<Expression> children = pattern.getPadding().getChildren();
        switch (pattern.getKind()) {
            case AS:
                visitContainer(
                        "",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        "as",
                        "",
                        p
                );
                break;
            case CAPTURE:
            case LITERAL:
                visitContainer(
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        p
                );
                break;
            case CLASS:
                visitSpace(children.getBefore(), PySpace.Location.MATCH_CASE_PATTERN_CHILD_PREFIX, p);
                visitRightPadded(children.getPadding().getElements().get(0), PyRightPadded.Location.MATCH_CASE_PATTERN_CHILD, p);
                visitContainer(
                        "(",
                        JContainer.build(children.getPadding().getElements().subList(1, children.getElements().size())),
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        ",",
                        ")",
                        p
                );
                break;
            case DOUBLE_STAR:
                visitContainer(
                        "**",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        "",
                        "",
                        p
                );
                break;
            case KEY_VALUE:
                visitContainer(
                        "",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        ":",
                        "",
                        p
                );
                break;
            case KEYWORD:
                visitContainer(
                        "",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        "=",
                        "",
                        p
                );
                break;
            case MAPPING:
                visitContainer(
                        "{",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        ",",
                        "}",
                        p
                );
                break;
            case OR:
                visitContainer(
                        "",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        "|",
                        "",
                        p
                );
                break;
            case SEQUENCE:
                visitContainer(
                        "",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        ",",
                        "",
                        p
                );
                break;
            case SEQUENCE_LIST:
                visitContainer(
                        "[",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        ",",
                        "]",
                        p
                );
                break;
            case GROUP:
            case SEQUENCE_TUPLE:
                visitContainer(
                        "(",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        ",",
                        ")",
                        p
                );
                break;
            case STAR:
                visitContainer(
                        "*",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        "",
                        "",
                        p
                );
                break;
            case VALUE:
                visitContainer(
                        "",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        "",
                        "",
                        p
                );
                break;
            case WILDCARD:
                visitContainer(
                        "_",
                        children,
                        PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN,
                        "",
                        "",
                        p
                );
                break;
        }
        return pattern;
    }

    @Override
    public J visitSpecialParameter(Py.SpecialParameter param, PrintOutputCapture<P> p) {
        beforeSyntax(param, PySpace.Location.SPECIAL_PARAMETER_PREFIX, p);
        switch (param.getKind()) {
            case ARGS:
                p.append("*");
                break;
            case KWARGS:
                p.append("**");
                break;
        }
        afterSyntax(param, p);
        return param;
    }

    @Override
    public J visitNamedArgument(Py.NamedArgument arg, PrintOutputCapture<P> p) {
        beforeSyntax(arg, PySpace.Location.NAMED_ARGUMENT, p);
        visit(arg.getName(), p);
        visitLeftPadded("=", arg.getPadding().getValue(), PyLeftPadded.Location.NAMED_ARGUMENT_VALUE, p);
        return arg;
    }

    @Override
    public J visitSlice(Py.Slice slice, PrintOutputCapture<P> p) {
        beforeSyntax(slice, PySpace.Location.SLICE_PREFIX, p);
        visitRightPadded(slice.getPadding().getStart(), PyRightPadded.Location.SLICE_START, p);
        p.append(':');
        if (slice.getPadding().getStop() != null) {
            visitRightPadded(slice.getPadding().getStop(), PyRightPadded.Location.SLICE_STOP, p);
            if (slice.getPadding().getStep() != null) {
                p.append(':');
                visitRightPadded(slice.getPadding().getStep(), PyRightPadded.Location.SLICE_STEP, p);
            }
        }
        return slice;
    }

    @Override
    public J visitStar(Py.Star star, PrintOutputCapture<P> p) {
        beforeSyntax(star, PySpace.Location.STAR_PREFIX, p);
        switch (star.getKind()) {
            case LIST:
                p.append("*");
                break;
            case DICT:
                p.append("**");
                break;
        }
        visit(star.getExpression(), p);
        afterSyntax(star, p);
        return star;
    }

    @Override
    public J visitTrailingElseWrapper(Py.TrailingElseWrapper wrapper, PrintOutputCapture<P> p) {
        beforeSyntax(wrapper, PySpace.Location.TRAILING_ELSE_WRAPPER_PREFIX, p);
        visit(wrapper.getStatement(), p);
        if (!(wrapper.getStatement() instanceof J.Try)) {
            visitSpace(
                    wrapper.getPadding().getElseBlock().getBefore(),
                    Location.ELSE_PREFIX,
                    p
            );
            p.append("else");
            visit(wrapper.getElseBlock(), p);
        }
        afterSyntax(wrapper, p);
        return wrapper;
    }

    @Override
    public J visitTypeHint(Py.TypeHint type, PrintOutputCapture<P> p) {
        beforeSyntax(type, PySpace.Location.TYPE_HINT_PREFIX, p);
        J parent = getCursor().getParentTreeCursor().getValue();
        if (parent instanceof J.MethodDeclaration) {
            p.append("->");
        } else {
            p.append(':');
        }
        visit(type.getTypeTree(), p);
        afterSyntax(type, p);
        return type;
    }

    @Override
    public J visitTypeHintedExpression(Py.TypeHintedExpression expr, PrintOutputCapture<P> p) {
        beforeSyntax(expr, PySpace.Location.TYPE_HINTED_EXPRESSION_PREFIX, p);
        visit(expr.getExpression(), p);
        visit(expr.getTypeHint(), p);
        afterSyntax(expr, p);
        return expr;
    }

    @Override
    public J visitTypeAlias(Py.TypeAlias typeAlias, PrintOutputCapture<P> p) {
        beforeSyntax(typeAlias, PySpace.Location.UNION_TYPE_PREFIX, p);
        p.append("type");
        visit(typeAlias.getName(), p);
        visitLeftPadded("=", typeAlias.getPadding().getValue(), PyLeftPadded.Location.TYPE_ALIAS_VALUE, p);
        afterSyntax(typeAlias, p);
        return typeAlias;
    }

    @Override
    public J visitUnionType(Py.UnionType unionType, PrintOutputCapture<P> p) {
        beforeSyntax(unionType, PySpace.Location.UNION_TYPE_PREFIX, p);
        visitRightPadded(unionType.getPadding().getTypes(), PyRightPadded.Location.UNION_TYPE_TYPES, "|", p);
        afterSyntax(unionType, p);
        return unionType;
    }

    @SuppressWarnings("SameParameterValue")
    private static boolean lastCharIs(PrintOutputCapture<?> p, char c) {
        return p.out.length() != 0 && p.out.charAt(p.out.length() - 1) == c;
    }

    private class PythonJavaPrinter extends JavaPrinter<P> {
        @Override
        public J visit(@Nullable Tree tree, PrintOutputCapture<P> p) {
            if (tree instanceof Py) {
                // re-route printing back up to Python printer
                return PythonPrinter.this.visitNonNull(tree, p);
            } else {
                //noinspection DataFlowIssue
                return super.visit(tree, p);
            }
        }

        @Override
        public void setCursor(@Nullable Cursor cursor) {
            super.setCursor(cursor);
            PythonPrinter.this.internalSetCursor(cursor);
        }

        public void internalSetCursor(@Nullable Cursor cursor) {
            super.setCursor(cursor);
        }

        @Override
        public J visitAnnotation(J.Annotation annotation, PrintOutputCapture<P> p) {
            beforeSyntax(annotation, Location.ANNOTATION_PREFIX, p);
            p.append("@");
            visit(annotation.getAnnotationType(), p);
            visitContainer("(", annotation.getPadding().getArguments(), JContainer.Location.ANNOTATION_ARGUMENTS, ",", ")", p);
            afterSyntax(annotation, p);
            return annotation;
        }

        @Override
        public J visitArrayDimension(J.ArrayDimension arrayDimension, PrintOutputCapture<P> p) {
            beforeSyntax(arrayDimension, Location.DIMENSION_PREFIX, p);
            p.append("[");
            visitRightPadded(arrayDimension.getPadding().getIndex(), JRightPadded.Location.ARRAY_INDEX, "]", p);
            afterSyntax(arrayDimension, p);
            return arrayDimension;
        }

        @Override
        public J visitAssert(J.Assert azzert, PrintOutputCapture<P> p) {
            beforeSyntax(azzert, Location.ASSERT_PREFIX, p);
            p.append("assert");
            visit(azzert.getCondition(), p);
            if (azzert.getDetail() != null) {
                visitLeftPadded(",", azzert.getDetail(), JLeftPadded.Location.ASSERT_DETAIL, p);
            }
            afterSyntax(azzert, p);
            return azzert;
        }

        @Override
        public J visitAssignment(J.Assignment assignment, PrintOutputCapture<P> p) {
            final String symbol;
            J parentTree = getCursor().getParentTreeCursor().getValue();
            if (parentTree instanceof J.Block ||
                parentTree instanceof Py.CompilationUnit ||
                (parentTree instanceof J.If) && ((J.If) parentTree).getThenPart() == assignment ||
                (parentTree instanceof J.If.Else) && ((J.If.Else) parentTree).getBody() == assignment ||
                (parentTree instanceof Loop) && ((Loop) parentTree).getBody() == assignment) {
                symbol = "=";
            } else {
                symbol = ":=";
            }

            beforeSyntax(assignment, Location.ASSIGNMENT_PREFIX, p);
            visit(assignment.getVariable(), p);
            visitLeftPadded(symbol, assignment.getPadding().getAssignment(), JLeftPadded.Location.ASSIGNMENT, p);
            afterSyntax(assignment, p);
            return assignment;
        }

        @Override
        public J visitAssignmentOperation(J.AssignmentOperation assignOp, PrintOutputCapture<P> p) {
            String keyword = "";
            switch (assignOp.getOperator()) {
                case Addition:
                    keyword = "+=";
                    break;
                case Subtraction:
                    keyword = "-=";
                    break;
                case Multiplication:
                    keyword = "*=";
                    break;
                case Division:
                    keyword = "/=";
                    break;
                case Modulo:
                    keyword = "%=";
                    break;
                case BitAnd:
                    keyword = "&=";
                    break;
                case BitOr:
                    keyword = "|=";
                    break;
                case BitXor:
                    keyword = "^=";
                    break;
                case LeftShift:
                    keyword = "<<=";
                    break;
                case RightShift:
                    keyword = ">>=";
                    break;
                case UnsignedRightShift:
                    keyword = ">>>=";
                    break;
                case Exponentiation:
                    keyword = "**=";
                    break;
                case FloorDivision:
                    keyword = "//=";
                    break;
                case MatrixMultiplication:
                    keyword = "@=";
                    break;
            }
            beforeSyntax(assignOp, Location.ASSIGNMENT_OPERATION_PREFIX, p);
            visit(assignOp.getVariable(), p);
            visitSpace(assignOp.getPadding().getOperator().getBefore(), Location.ASSIGNMENT_OPERATION_OPERATOR, p);
            p.append(keyword);
            visit(assignOp.getAssignment(), p);
            afterSyntax(assignOp, p);
            return assignOp;
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
                    keyword = "==";
                    break;
                case NotEqual:
                    keyword = "!=";
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
            beforeSyntax(binary, Location.BINARY_PREFIX, p);
            visit(binary.getLeft(), p);
            visitSpace(binary.getPadding().getOperator().getBefore(), Location.BINARY_OPERATOR, p);

            p.append(keyword);

            visit(binary.getRight(), p);
            afterSyntax(binary, p);
            return binary;
        }

        @Override
        public J visitBlock(J.Block block, PrintOutputCapture<P> p) {
            beforeSyntax(block, Location.BLOCK_PREFIX, p);
            p.append(':');

            visitStatements(block.getPadding().getStatements(), JRightPadded.Location.BLOCK_STATEMENT, p);
            visitSpace(block.getEnd(), Location.BLOCK_END, p);
            afterSyntax(block, p);
            return block;
        }

        @Override
        public J visitCase(J.Case ca, PrintOutputCapture<P> p) {
            beforeSyntax(ca, Location.CASE_PREFIX, p);
            J elem = ca.getCaseLabels().get(0);
            if (!(elem instanceof J.Identifier) || !((J.Identifier) elem).getSimpleName().equals("default")) {
                p.append("case");
            }
            visitContainer("", ca.getPadding().getCaseLabels(), JContainer.Location.CASE_EXPRESSION, ",", "", p);
            visitSpace(ca.getPadding().getStatements().getBefore(), Location.CASE, p);
            visitStatements(ca.getPadding().getStatements().getPadding().getElements(), JRightPadded.Location.CASE, p);
            if (ca.getBody() instanceof Statement) {
                visitRightPadded(ca.getPadding().getBody(), JRightPadded.Location.LANGUAGE_EXTENSION, p);
            } else {
                visitRightPadded(ca.getPadding().getBody(), JRightPadded.Location.CASE_BODY, ";", p);
            }
            afterSyntax(ca, p);
            return ca;
        }

        @Override
        public J visitCatch(J.Try.Catch ca, PrintOutputCapture<P> p) {
            beforeSyntax(ca, Location.CATCH_PREFIX, p);
            p.append("except");

            J.VariableDeclarations multiVariable = ca.getParameter().getTree();
            beforeSyntax(multiVariable, Location.VARIABLE_DECLARATIONS_PREFIX, p);
            visit(multiVariable.getTypeExpression(), p);
            for (JRightPadded<J.VariableDeclarations.NamedVariable> paddedVariable : multiVariable.getPadding().getVariables()) {
                J.VariableDeclarations.NamedVariable variable = paddedVariable.getElement();
                if (variable.getName().getSimpleName().isEmpty()) {
                    continue;
                }
                visitSpace(paddedVariable.getAfter(), Location.LANGUAGE_EXTENSION, p);
                beforeSyntax(variable, Location.VARIABLE_PREFIX, p);
                p.append("as");
                visit(variable.getName(), p);
                afterSyntax(variable, p);
            }
            afterSyntax(multiVariable, p);

            visit(ca.getBody(), p);
            afterSyntax(ca, p);
            return ca;
        }

        @Override
        public J visitClassDeclaration(J.ClassDeclaration classDecl, PrintOutputCapture<P> p) {
            beforeSyntax(classDecl, Location.CLASS_DECLARATION_PREFIX, p);
            visitSpace(Space.EMPTY, Location.ANNOTATIONS, p);
            visit(classDecl.getLeadingAnnotations(), p);
            visit(classDecl.getPadding().getKind().getAnnotations(), p);
            visitSpace(
                    classDecl.getPadding().getKind().getPrefix(),
                    Location.CLASS_KIND,
                    p
            );
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
            beforeSyntax(controlParens, Location.CONTROL_PARENTHESES_PREFIX, p);
            visitRightPadded(controlParens.getPadding().getTree(), JRightPadded.Location.PARENTHESES, "", p);
            afterSyntax(controlParens, p);
            return controlParens;
        }

        @Override
        public J visitElse(J.If.Else else_, PrintOutputCapture<P> p) {
            beforeSyntax(else_, Location.ELSE_PREFIX, p);
            if (getCursor().getParentTreeCursor().getValue() instanceof J.If && else_.getBody() instanceof J.If) {
                p.append("el");
                visit(else_.getBody(), p);
            } else if (else_.getBody() instanceof J.Block) {
                p.append("else");
                visit(else_.getBody(), p);
            } else {
                p.append("else");
                p.append(':');
                visit(else_.getBody(), p);
            }
            afterSyntax(else_, p);
            return else_;
        }

        @Override
        public J visitForEachControl(J.ForEachLoop.Control control, PrintOutputCapture<P> p) {
            beforeSyntax(control, Location.FOR_EACH_CONTROL_PREFIX, p);
            visitRightPadded(control.getPadding().getVariable(), JRightPadded.Location.FOREACH_VARIABLE, p);
            p.append("in");
            visitRightPadded(control.getPadding().getIterable(), JRightPadded.Location.FOREACH_ITERABLE, p);
            afterSyntax(control, p);
            return control;
        }

        @Override
        public J visitForEachLoop(J.ForEachLoop forEachLoop, PrintOutputCapture<P> p) {
            beforeSyntax(forEachLoop, Location.FOR_EACH_LOOP_PREFIX, p);
            p.append("for");
            visit(forEachLoop.getControl(), p);
            visit(forEachLoop.getBody(), p);
            afterSyntax(forEachLoop, p);
            return forEachLoop;
        }

        @Override
        public J visitIdentifier(J.Identifier ident, PrintOutputCapture<P> p) {
            this.beforeSyntax(ident, Location.IDENTIFIER_PREFIX, p);
            Optional<Quoted> quoted = ident.getMarkers().findFirst(Quoted.class);
            quoted.ifPresent(value -> p.append(value.getStyle().getQuote()));
            p.append(ident.getSimpleName());
            quoted.ifPresent(value -> p.append(value.getStyle().getQuote()));
            this.afterSyntax(ident, p);
            return ident;
        }

        @Override
        public J visitIf(J.If iff, PrintOutputCapture<P> p) {
            beforeSyntax(iff, Location.IF_PREFIX, p);
            p.append("if");
            visit(iff.getIfCondition(), p);

            JRightPadded<Statement> thenPart = iff.getPadding().getThenPart();
            if (!(thenPart.getElement() instanceof J.Block)) {
                p.append(":");
            }
            visitStatement(thenPart, JRightPadded.Location.IF_THEN, p);
            visit(iff.getElsePart(), p);
            afterSyntax(iff, p);
            return iff;
        }

        @Override
        public J visitImport(Import im, PrintOutputCapture<P> p) {
            beforeSyntax(im, Location.IMPORT_PREFIX, p);
            if (im.getQualid().getTarget() instanceof J.Empty) {
                visit(im.getQualid().getName(), p);
            } else {
                visit(im.getQualid(), p);
            }
            visitLeftPadded("as", im.getPadding().getAlias(), JLeftPadded.Location.IMPORT_ALIAS_PREFIX, p);
            afterSyntax(im, p);
            return im;
        }

        @Override
        public J visitLambda(J.Lambda lambda, PrintOutputCapture<P> p) {
            beforeSyntax(lambda, Location.LAMBDA_PREFIX, p);
            p.append("lambda");
            visitSpace(lambda.getParameters().getPrefix(), Location.LAMBDA_PARAMETERS_PREFIX, p);
            visitMarkers(lambda.getParameters().getMarkers(), p);
            visitRightPadded(lambda.getParameters().getPadding().getParameters(), JRightPadded.Location.LAMBDA_PARAM, ",", p);
            visitSpace(lambda.getArrow(), Location.LAMBDA_ARROW_PREFIX, p);
            p.append(":");
            visit(lambda.getBody(), p);
            afterSyntax(lambda, p);
            return lambda;
        }

        @Override
        public J visitLiteral(J.Literal literal, PrintOutputCapture<P> p) {
            if (literal.getValue() == null && literal.getValueSource() == null) {
                // currently, also `...` is mapped to a `None` value
                literal = literal.withValueSource("None");
            }

            beforeSyntax(literal, Location.LITERAL_PREFIX, p);
            List<J.Literal.UnicodeEscape> unicodeEscapes = literal.getUnicodeEscapes();
            if (unicodeEscapes == null) {
                p.append(literal.getValueSource());
            } else if (literal.getValueSource() != null) {
                Iterator<J.Literal.UnicodeEscape> surrogateIter = unicodeEscapes.iterator();
                J.Literal.UnicodeEscape surrogate = surrogateIter.hasNext() ?
                        surrogateIter.next() : null;
                int i = 0;
                if (surrogate != null && surrogate.getValueSourceIndex() == 0) {
                    p.append("\\u").append(surrogate.getCodePoint());
                    if (surrogateIter.hasNext()) {
                        surrogate = surrogateIter.next();
                    }
                }

                char[] valueSourceArr = literal.getValueSource().toCharArray();
                for (char c : valueSourceArr) {
                    p.append(c);
                    if (surrogate != null && surrogate.getValueSourceIndex() == ++i) {
                        while (surrogate != null && surrogate.getValueSourceIndex() == i) {
                            p.append("\\u").append(surrogate.getCodePoint());
                            surrogate = surrogateIter.hasNext() ? surrogateIter.next() : null;
                        }
                    }
                }
            }
            afterSyntax(literal, p);
            return literal;
        }

        @Override
        public <M extends Marker> M visitMarker(Marker marker, PrintOutputCapture<P> p) {
            if (marker instanceof Semicolon) {
                p.append(';');
            } else if (marker instanceof TrailingComma) {
                p.append(',');
                visitSpace(((TrailingComma) marker).getSuffix(), Location.ANY, p);
            }
            //noinspection unchecked
            return (M) marker;
        }

        @Override
        public J visitMethodDeclaration(J.MethodDeclaration method, PrintOutputCapture<P> p) {
            beforeSyntax(method, Location.METHOD_DECLARATION_PREFIX, p);
            visitSpace(Space.EMPTY, Location.ANNOTATIONS, p);
            visit(method.getLeadingAnnotations(), p);
            for (J.Modifier m : method.getModifiers()) {
                visitModifier(m, p);
            }
            visit(method.getName(), p);
            visitContainer("(", method.getPadding().getParameters(), JContainer.Location.METHOD_DECLARATION_PARAMETERS, ",", ")", p);
            visit(method.getReturnTypeExpression(), p);
            visit(method.getBody(), p);
            afterSyntax(method, p);
            return method;
        }

        @Override
        public J visitMethodInvocation(J.MethodInvocation method, PrintOutputCapture<P> p) {
            beforeSyntax(method, Location.METHOD_INVOCATION_PREFIX, p);
            visitRightPadded(method.getPadding().getSelect(), JRightPadded.Location.METHOD_SELECT, method.getSimpleName().isEmpty() ? "" : ".", p);
            visitContainer("<", method.getPadding().getTypeParameters(), JContainer.Location.TYPE_PARAMETERS, ",", ">", p);
            visit(method.getName(), p);
            String before = "(";
            String after = ")";
            if (method.getMarkers().findFirst(OmitParentheses.class).isPresent()) {
                before = "";
                after = "";
            }
            visitContainer(before, method.getPadding().getArguments(), JContainer.Location.METHOD_INVOCATION_ARGUMENTS, ",", after, p);
            afterSyntax(method, p);
            return method;
        }

        @Override
        public J visitModifier(J.Modifier mod, PrintOutputCapture<P> p) {
            String keyword = null;
            switch (mod.getType()) {
                case Default:
                    keyword = "def";
                    break;
                case Async:
                    keyword = "async";
                    break;
            }
            if (keyword != null) {
                visit(mod.getAnnotations(), p);
                beforeSyntax(mod, Location.MODIFIER_PREFIX, p);
                p.append(keyword);
                afterSyntax(mod, p);
            }
            return mod;
        }

        @Override
        public J visitNewArray(J.NewArray newArray, PrintOutputCapture<P> p) {
            beforeSyntax(newArray, Location.NEW_ARRAY_PREFIX, p);
            visitContainer("[", newArray.getPadding().getInitializer(), JContainer.Location.NEW_ARRAY_INITIALIZER, ",", "]", p);
            afterSyntax(newArray, p);
            return newArray;
        }

        @Override
        public J visitParameterizedType(J.ParameterizedType type, PrintOutputCapture<P> p) {
            beforeSyntax(type, Location.PARAMETERIZED_TYPE_PREFIX, p);
            visit(type.getClazz(), p);
            visitContainer("[", type.getPadding().getTypeParameters(), JContainer.Location.TYPE_PARAMETERS, ",", "]", p);
            afterSyntax(type, p);
            return type;
        }

        @Override
        public J visitSwitch(J.Switch sw, PrintOutputCapture<P> p) {
            beforeSyntax(sw, Location.SWITCH_PREFIX, p);
            p.append("match");
            visit(sw.getSelector(), p);
            visit(sw.getCases(), p);
            afterSyntax(sw, p);
            return sw;
        }

        @Override
        public J visitTernary(J.Ternary ternary, PrintOutputCapture<P> p) {
            beforeSyntax(ternary, Location.TERNARY_PREFIX, p);
            visit(ternary.getTruePart(), p);
            visitSpace(ternary.getPadding().getTruePart().getBefore(), Location.TERNARY_TRUE, p);
            p.append("if");
            visit(ternary.getCondition(), p);
            visitLeftPadded("else", ternary.getPadding().getFalsePart(), JLeftPadded.Location.TERNARY_FALSE, p);
            afterSyntax(ternary, p);
            return ternary;
        }

        @Override
        public J visitThrow(J.Throw thrown, PrintOutputCapture<P> p) {
            beforeSyntax(thrown, Location.THROW_PREFIX, p);
            p.append("raise");
            visit(thrown.getException(), p);
            afterSyntax(thrown, p);
            return thrown;
        }

        @Override
        public J visitTry(J.Try tryable, PrintOutputCapture<P> p) {
            boolean isWithStatement = tryable.getResources() != null && !tryable.getResources().isEmpty();

            beforeSyntax(tryable, Location.TRY_PREFIX, p);
            if (isWithStatement) {
                p.append("with");
            } else {
                p.append("try");
            }
            JContainer<J.Try.Resource> resources = tryable.getPadding().getResources();
            if (isWithStatement && resources != null) {
                visitSpace(resources.getBefore(), Location.TRY_RESOURCES, p);
                boolean omitParentheses = resources.getMarkers().findFirst(OmitParentheses.class).isPresent();
                if (!omitParentheses) {
                    p.append("(");
                }
                boolean first = true;
                for (JRightPadded<J.Try.Resource> resource : resources.getPadding().getElements()) {
                    if (!first) {
                        p.append(",");
                    } else {
                        first = false;
                    }

                    visitSpace(resource.getElement().getPrefix(), Location.TRY_RESOURCE, p);
                    visitMarkers(resource.getElement().getMarkers(), p);

                    TypedTree decl = resource.getElement().getVariableDeclarations();
                    if (decl instanceof J.Assignment) {
                        J.Assignment assignment = (J.Assignment) decl;
                        visit(assignment.getAssignment(), p);
                        if (!(assignment.getVariable() instanceof J.Empty)) {
                            visitSpace(assignment.getPadding().getAssignment().getBefore(), Location.LANGUAGE_EXTENSION, p);
                            p.append("as");
                            visit(assignment.getVariable(), p);
                        }
                    } else {
                        visit(decl, p);
                    }

                    visitSpace(resource.getAfter(), Location.TRY_RESOURCE_SUFFIX, p);
                    visitMarkers(resource.getMarkers(), p);
                }
                visitMarkers(resources.getMarkers(), p);
                if (!omitParentheses) {
                    p.append(")");
                }
            }

            J.Block tryBody = tryable.getBody();
            Py.TrailingElseWrapper elseWrapper = getCursor().getParentTreeCursor().getValue() instanceof Py.TrailingElseWrapper ?
                    ((Py.TrailingElseWrapper) getCursor().getParentTreeCursor().getValue()) : null;

            visit(tryBody, p);
            visit(tryable.getCatches(), p);
            if (elseWrapper != null) {
                visitSpace(
                        elseWrapper.getPadding().getElseBlock().getBefore(),
                        Location.ELSE_PREFIX,
                        p
                );
                p.append("else");
                visit(elseWrapper.getElseBlock(), p);
            }

            visitLeftPadded("finally", tryable.getPadding().getFinally(), JLeftPadded.Location.TRY_FINALLY, p);
            afterSyntax(tryable, p);
            return tryable;
        }

        @Override
        public J visitUnary(J.Unary unary, PrintOutputCapture<P> p) {
            beforeSyntax(unary, Location.UNARY_PREFIX, p);
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
        public J visitVariable(J.VariableDeclarations.NamedVariable variable, PrintOutputCapture<P> p) {
            beforeSyntax(variable, Location.VARIABLE_PREFIX, p);
            J.VariableDeclarations vd = getCursor().getParentTreeCursor().getValue();
            JRightPadded<J.VariableDeclarations.NamedVariable> padding = getCursor().getParent().getValue();
            TypeTree type = vd.getTypeExpression();
            if (type instanceof Py.SpecialParameter) {
                Py.SpecialParameter special = (Py.SpecialParameter) type;
                visit(special, p);
                type = special.getTypeHint();
            }
            if (variable.getName().getSimpleName().isEmpty()) {
                visit(variable.getInitializer(), p);
            } else {
                if (vd.getVarargs() != null) {
                    visitSpace(vd.getVarargs(), Location.VARARGS, p);
                    p.append('*');
                }
                if (vd.getMarkers().findFirst(KeywordArguments.class).isPresent()) {
                    p.append("**");
                }
                visit(variable.getName(), p);
                if (type != null) {
                    visitSpace(padding.getAfter(), JRightPadded.Location.NAMED_VARIABLE.getAfterLocation(), p);
                    p.append(':');
                    visit(type, p);
                }
                visitLeftPadded("=", variable.getPadding().getInitializer(), JLeftPadded.Location.VARIABLE_INITIALIZER, p);
            }
            afterSyntax(variable, p);
            return variable;
        }

        @Override
        public J visitVariableDeclarations(J.VariableDeclarations multiVariable, PrintOutputCapture<P> p) {
            beforeSyntax(multiVariable, Location.VARIABLE_DECLARATIONS_PREFIX, p);
            visitSpace(Space.EMPTY, Location.ANNOTATIONS, p);
            visit(multiVariable.getLeadingAnnotations(), p);
            for (J.Modifier m : multiVariable.getModifiers()) {
                visitModifier(m, p);
            }

            if (multiVariable.getMarkers().findFirst(KeywordOnlyArguments.class).isPresent()) {
                p.append("*");
            }

            List<? extends JRightPadded<? extends J>> nodes = multiVariable.getPadding().getVariables();
            for (int i = 0; i < nodes.size(); i++) {
                JRightPadded<? extends J> node = nodes.get(i);
                setCursor(new Cursor(getCursor(), node));
                visit(node.getElement(), p);
                visitMarkers(node.getMarkers(), p);
                if (i < nodes.size() - 1) {
                    p.append(",");
                }
                setCursor(getCursor().getParent());
            }

            afterSyntax(multiVariable, p);
            return multiVariable;
        }

        @Override
        protected void printStatementTerminator(Statement s, PrintOutputCapture<P> p) {
            // optional semicolons are handled in `visitMarker()`
        }
    }

    @Override
    public <M extends Marker> M visitMarker(Marker marker, PrintOutputCapture<P> p) {
        return delegate.visitMarker(marker, p);
    }

    private static final UnaryOperator<String> JAVA_MARKER_WRAPPER =
            out -> "/*~~" + out + (out.isEmpty() ? "" : "~~") + ">*/";

    private void beforeSyntax(Py py,
                              @SuppressWarnings("SameParameterValue") Location loc,
                              PrintOutputCapture<P> p) {
        beforeSyntax(py.getPrefix(), py.getMarkers(), loc, p);
    }

    private void beforeSyntax(Py py, PySpace.Location loc, PrintOutputCapture<P> p) {
        beforeSyntax(py.getPrefix(), py.getMarkers(), loc, p);
    }

    private void beforeSyntax(Space prefix, Markers markers, PySpace.@Nullable Location loc, PrintOutputCapture<P> p) {
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().beforePrefix(marker, new Cursor(getCursor(), marker), JAVA_MARKER_WRAPPER));
        }
        if (loc != null) {
            visitSpace(prefix, loc, p);
        }
        visitMarkers(markers, p);
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().beforeSyntax(marker, new Cursor(getCursor(), marker), JAVA_MARKER_WRAPPER));
        }
    }

    private void beforeSyntax(Space prefix, Markers markers, @Nullable Location loc, PrintOutputCapture<P> p) {
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().beforePrefix(marker, new Cursor(getCursor(), marker), JAVA_MARKER_WRAPPER));
        }
        if (loc != null) {
            visitSpace(prefix, loc, p);
        }
        visitMarkers(markers, p);
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().beforeSyntax(marker, new Cursor(getCursor(), marker), JAVA_MARKER_WRAPPER));
        }
    }

    private void afterSyntax(Py py, PrintOutputCapture<P> p) {
        afterSyntax(py.getMarkers(), p);
    }

    private void afterSyntax(Markers markers, PrintOutputCapture<P> p) {
        for (Marker marker : markers.getMarkers()) {
            p.append(p.getMarkerPrinter().afterSyntax(marker, new Cursor(getCursor(), marker), JAVA_MARKER_WRAPPER));
        }
    }

    @Override
    public Space visitSpace(Space space, PySpace.Location loc, PrintOutputCapture<P> p) {
        return delegate.visitSpace(space, Location.LANGUAGE_EXTENSION, p);
    }

    @Override
    public Space visitSpace(Space space, Location loc, PrintOutputCapture<P> p) {
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

    private <T extends Tree> void visitLeftPadded(@SuppressWarnings("SameParameterValue") String s,
                                                  JLeftPadded<T> left,
                                                  @SuppressWarnings({"SameParameterValue", "unused"}) PyLeftPadded.Location loc,
                                                  PrintOutputCapture<P> p) {
        delegate.visitSpace(left.getBefore(), Location.LANGUAGE_EXTENSION, p);
        p.append(s);
        setCursor(new Cursor(this.getCursor(), left));
        T t = left.getElement();
        if (t instanceof J) {
            this.visitAndCast(left.getElement(), p);
        }

        setCursor(this.getCursor().getParent());
        visitMarkers(left.getMarkers(), p);
    }

    protected void visitRightPadded(List<? extends JRightPadded<? extends J>> nodes, PyRightPadded.Location location, String suffixBetween, PrintOutputCapture<P> p) {
        for (int i = 0; i < nodes.size(); i++) {
            JRightPadded<? extends J> node = nodes.get(i);
            visit(node.getElement(), p);
            visitSpace(node.getAfter(), location.getAfterLocation(), p);
            visitMarkers(node.getMarkers(), p);
            if (i < nodes.size() - 1) {
                p.append(suffixBetween);
            }
        }
    }
}
