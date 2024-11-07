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
package org.openrewrite.python;

import org.jspecify.annotations.Nullable;
import org.openrewrite.SourceFile;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.java.JavaVisitor;
import org.openrewrite.java.tree.*;
import org.openrewrite.python.tree.*;

public class PythonVisitor<P> extends JavaVisitor<P> {

    @Override
    public boolean isAcceptable(SourceFile sourceFile, P p) {
        return sourceFile instanceof Py.CompilationUnit;
    }

    @Override
    public String getLanguage() {
        return "python";
    }

    public J visitAsync(Py.Async async, P p) {
        Py.Async a = async;
        a = a.withPrefix(visitSpace(a.getPrefix(), PySpace.Location.ASYNC_PREFIX, p));
        a = a.withMarkers(visitMarkers(a.getMarkers(), p));
        Statement temp = (Statement) visitStatement(a, p);
        if (!(temp instanceof Py.Async)) {
            return temp;
        } else {
            a = (Py.Async) temp;
        }
        a = a.withStatement(visitAndCast(a.getStatement(), p));
        return a;
    }

    public J visitAwait(Py.Await ogAwait, P p) {
        Py.Await await = ogAwait;
        await = await.withPrefix(visitSpace(await.getPrefix(), PySpace.Location.AWAIT_PREFIX, p));
        await = await.withMarkers(visitMarkers(await.getMarkers(), p));
        Expression temp = (Expression) visitExpression(await, p);
        if (!(temp instanceof Py.Await)) {
            return temp;
        } else {
            await = (Py.Await) temp;
        }
        await = await.withExpression(visitAndCast(await.getExpression(), p));
        await = await.withType(visitType(await.getType(), p));
        return await;
    }

    public J visitBinary(Py.Binary binary, P p) {
        Py.Binary b = binary;
        b = b.withPrefix(visitSpace(b.getPrefix(), PySpace.Location.BINARY_PREFIX, p));
        b = b.withMarkers(visitMarkers(b.getMarkers(), p));
        Expression temp = (Expression) visitExpression(b, p);
        if (!(temp instanceof Py.Binary)) {
            return temp;
        } else {
            b = (Py.Binary) temp;
        }
        b = b.withLeft(visitAndCast(b.getLeft(), p));
        b = b.getPadding().withOperator(visitLeftPadded(b.getPadding().getOperator(), PyLeftPadded.Location.BINARY_OPERATOR, p));
        b = b.withRight(visitAndCast(b.getRight(), p));
        b = b.withType(visitType(b.getType(), p));
        return b;
    }

    public J visitChainedAssignment(Py.ChainedAssignment chainedAssignment, P p) {
        Py.ChainedAssignment ca = chainedAssignment;
        ca = ca.withPrefix(visitSpace(ca.getPrefix(), PySpace.Location.CHAINED_ASSIGNMENT_PREFIX, p));
        ca = ca.withMarkers(visitMarkers(ca.getMarkers(), p));
        Statement temp = (Statement) visitStatement(ca, p);
        if (!(temp instanceof Py.ChainedAssignment)) {
            return temp;
        } else {
            ca = (Py.ChainedAssignment) temp;
        }
        ca = ca.getPadding().withVariables(ListUtils.map(ca.getPadding().getVariables(), t -> visitRightPadded(t, PyRightPadded.Location.CHAINED_ASSIGNMENT_VARIABLE, p)));
        ca = ca.withAssignment(visitAndCast(ca.getAssignment(), p));
        return ca;
    }

    public J visitCollectionLiteral(Py.CollectionLiteral coll, P p) {
        Py.CollectionLiteral c = coll;
        c = c.withPrefix(visitSpace(c.getPrefix(), PySpace.Location.COLLECTION_LITERAL_PREFIX, p));
        c = c.withMarkers(visitMarkers(c.getMarkers(), p));
        Expression temp = (Expression) visitExpression(c, p);
        if (!(temp instanceof Py.CollectionLiteral)) {
            return temp;
        } else {
            c = (Py.CollectionLiteral) temp;
        }
        c = c.getPadding().withElements(visitContainer(c.getPadding().getElements(), PyContainer.Location.DICT_LITERAL_ELEMENTS, p));
        return c;
    }

    public J visitCompilationUnit(Py.CompilationUnit cu, P p) {
        Py.CompilationUnit c = cu;
        c = c.withPrefix(visitSpace(c.getPrefix(), Space.Location.COMPILATION_UNIT_PREFIX, p));
        c = c.withMarkers(visitMarkers(c.getMarkers(), p));
        c = c.getPadding().withImports(ListUtils.map(c.getPadding().getImports(), t -> visitRightPadded(t, JRightPadded.Location.IMPORT, p)));
        c = c.withStatements(ListUtils.map(c.getStatements(), e -> visitAndCast(e, p)));
        c = c.withEof(visitSpace(c.getEof(), Space.Location.COMPILATION_UNIT_EOF, p));
        return c;
    }

    public J visitComprehensionExpression(Py.ComprehensionExpression ogComp, P p) {
        Py.ComprehensionExpression comp = ogComp;
        comp = comp.withPrefix(visitSpace(comp.getPrefix(), PySpace.Location.COMPREHENSION_PREFIX, p));
        comp = comp.withMarkers(visitMarkers(comp.getMarkers(), p));
        Expression temp = (Expression) visitExpression(comp, p);
        if (!(temp instanceof Py.ComprehensionExpression)) {
            return temp;
        } else {
            comp = (Py.ComprehensionExpression) temp;
        }
        comp = comp.withResult(visitAndCast(comp.getResult(), p));
        comp = comp.withClauses(ListUtils.map(
                comp.getClauses(),
                clause -> visitAndCast(clause, p)
        ));
        comp = comp.withSuffix(visitSpace(comp.getSuffix(), PySpace.Location.COMPREHENSION_SUFFIX, p));
        comp = comp.withType(visitType(comp.getType(), p));
        return comp;
    }

    public J visitComprehensionClause(Py.ComprehensionExpression.Clause ogClause, P p) {
        Py.ComprehensionExpression.Clause clause = ogClause;
        clause = clause.withPrefix(visitSpace(clause.getPrefix(), PySpace.Location.COMPREHENSION_CLAUSE_PREFIX, p));
        clause = clause.withMarkers(visitMarkers(clause.getMarkers(), p));
        clause = clause.withIteratorVariable(visitAndCast(clause.getIteratorVariable(), p));
        clause = clause.withConditions(ListUtils.map(
                clause.getConditions(),
                condition -> visitAndCast(condition, p)
        ));
        return clause;
    }

    public J visitComprehensionCondition(Py.ComprehensionExpression.Condition ogCondition, P p) {
        Py.ComprehensionExpression.Condition condition = ogCondition;
        condition = condition.withPrefix(visitSpace(condition.getPrefix(), PySpace.Location.COMPREHENSION_CONDITION_PREFIX, p));
        condition = condition.withMarkers(visitMarkers(condition.getMarkers(), p));
        condition = condition.withExpression(visitAndCast(condition.getExpression(), p));
        return condition;
    }

    public J visitDel(Py.Del ogDel, P p) {
        Py.Del del = ogDel;
        del = del.withPrefix(visitSpace(del.getPrefix(), PySpace.Location.DEL_PREFIX, p));
        del = del.withMarkers(visitMarkers(del.getMarkers(), p));
        Statement temp = (Statement) visitStatement(del, p);
        if (!(temp instanceof Py.Del)) {
            return temp;
        } else {
            del = (Py.Del) temp;
        }
        del = del.getPadding().withTargets(ListUtils.map(
                del.getPadding().getTargets(),
                t -> visitRightPadded(t, PyRightPadded.Location.DEL_ELEMENT, p)
        ));
        return del;
    }

    public J visitDictLiteral(Py.DictLiteral dict, P p) {
        Py.DictLiteral d = dict;
        d = d.withPrefix(visitSpace(d.getPrefix(), PySpace.Location.DICT_LITERAL_PREFIX, p));
        d = d.withMarkers(visitMarkers(d.getMarkers(), p));
        Expression temp = (Expression) visitExpression(d, p);
        if (!(temp instanceof Py.DictLiteral)) {
            return temp;
        } else {
            d = (Py.DictLiteral) temp;
        }
        d = d.getPadding().withElements(visitContainer(d.getPadding().getElements(), PyContainer.Location.DICT_LITERAL_ELEMENTS, p));
        return d;
    }

    public J visitExpressionStatement(Py.ExpressionStatement expressionStatement, P p) {
        Py.ExpressionStatement stmt = expressionStatement;
        stmt = stmt.withExpression(visitAndCast(stmt.getExpression(), p));
        return visitStatement(stmt, p);
    }

    public J visitExceptionType(Py.ExceptionType ogType, P p) {
        Py.ExceptionType type = ogType;
        type = type.withPrefix(visitSpace(type.getPrefix(), PySpace.Location.EXCEPTION_TYPE_PREFIX, p));
        type = type.withMarkers(visitMarkers(type.getMarkers(), p));
        type = type.withExpression(visitAndCast(type.getExpression(), p));
        return type;
    }

    public J visitErrorFrom(Py.ErrorFrom ogExpr, P p) {
        Py.ErrorFrom expr = ogExpr;
        expr = expr.withPrefix(visitSpace(expr.getPrefix(), PySpace.Location.ERROR_FROM_PREFIX, p));
        expr = expr.withMarkers(visitMarkers(expr.getMarkers(), p));
        Expression temp = (Expression) visitExpression(expr, p);
        if (!(temp instanceof Py.ErrorFrom)) {
            return temp;
        } else {
            expr = (Py.ErrorFrom) temp;
        }
        expr = expr.withError(visitAndCast(expr.getError(), p));
        expr = expr.getPadding().withFrom(
                visitLeftPadded(expr.getPadding().getFrom(), PyLeftPadded.Location.ERROR_FROM, p)
        );
        return expr;
    }


    public J visitExpressionTypeTree(Py.ExpressionTypeTree expressionTypeTree, P p) {
        Py.ExpressionTypeTree t = expressionTypeTree;
        t = t.withPrefix(visitSpace(t.getPrefix(), PySpace.Location.EXPRESSION_TYPE_TREE_PREFIX, p));
        t = t.withMarkers(visitMarkers(t.getMarkers(), p));
        t = t.withReference(visit(t.getReference(), p));
        return t;
    }

    public J visitFormattedString(Py.FormattedString fString, P p) {
        Py.FormattedString fs = fString;
        fs = fs.withPrefix(visitSpace(fs.getPrefix(), PySpace.Location.FORMATTED_STRING_PREFIX, p));
        fs = fs.withMarkers(visitMarkers(fs.getMarkers(), p));
        Expression temp = (Expression) visitExpression(fs, p);
        if (!(temp instanceof Py.FormattedString)) {
            return temp;
        } else {
            fs = (Py.FormattedString) temp;
        }
        fs = fs.withParts(ListUtils.map(fs.getParts(), part -> visitAndCast(part, p)));
        return fs;
    }

    public J visitFormattedStringValue(Py.FormattedString.Value value, P p) {
        Py.FormattedString.Value fv = value;
        fv = fv.withPrefix(visitSpace(fv.getPrefix(), PySpace.Location.FORMATTED_STRING_VALUE_PREFIX, p));
        fv = fv.withMarkers(visitMarkers(fv.getMarkers(), p));
        Expression temp = (Expression) visitExpression(fv, p);
        if (!(temp instanceof Py.FormattedString.Value)) {
            return temp;
        } else {
            fv = (Py.FormattedString.Value) temp;
        }
        fv = fv.getPadding().withExpression(visitRightPadded(fv.getPadding().getExpression(), PyRightPadded.Location.FORMATTED_STRING_VALUE_EXPRESSION, p));
        fv = fv.getPadding().withDebug(visitRightPadded(fv.getPadding().getDebug(), PyRightPadded.Location.FORMATTED_STRING_VALUE_DEBUG, p));
        fv = fv.withFormat(visitAndCast(fv.getFormat(), p));
        return fv;
    }

    public J visitKeyValue(Py.KeyValue keyValue, P p) {
        Py.KeyValue e = keyValue;
        e = e.withPrefix(visitSpace(e.getPrefix(), PySpace.Location.DICT_ENTRY, p));
        Expression temp = (Expression) visitExpression(e, p);
        if (!(temp instanceof Py.KeyValue)) {
            return temp;
        } else {
            e = (Py.KeyValue) temp;
        }
        e = e.getPadding().withKey(visitRightPadded(e.getPadding().getKey(), PyRightPadded.Location.DICT_ENTRY_KEY, p));
        e = e.withValue(visitAndCast(e.getValue(), p));
        e = e.withType(visitType(e.getType(), p));
        return e;
    }

    public J visitLiteralType(Py.LiteralType literalType, P p) {
        Py.LiteralType type = literalType;
        type = type.withPrefix(visitSpace(type.getPrefix(), PySpace.Location.LITERAL_TYPE_PREFIX, p));
        type = type.withMarkers(visitMarkers(type.getMarkers(), p));
        type = type.withLiteral(visitAndCast(type.getLiteral(), p));
        return type;
    }

    public J visitMatchCasePattern(Py.MatchCase.Pattern ogPattern, P p) {
        Py.MatchCase.Pattern pattern = ogPattern;
        pattern = pattern.withPrefix(visitSpace(pattern.getPrefix(), PySpace.Location.MATCH_PATTERN_PREFIX, p));
        pattern = pattern.withMarkers(visitMarkers(pattern.getMarkers(), p));
        Expression temp = (Expression) visitExpression(pattern, p);
        if (!(temp instanceof Py.MatchCase.Pattern)) {
            return temp;
        } else {
            pattern = (Py.MatchCase.Pattern) temp;
        }
        pattern.withChildren(ListUtils.map(
                pattern.getChildren(),
                child -> (Expression) visitAndCast(child, p)
        ));
        return pattern;
    }

    public J visitMatchCase(Py.MatchCase ogMatch, P p) {
        Py.MatchCase case_ = ogMatch;
        case_ = case_.withPrefix(visitSpace(case_.getPrefix(), PySpace.Location.MATCH_CASE_PREFIX, p));
        case_ = case_.withMarkers(visitMarkers(case_.getMarkers(), p));
        Expression temp = (Expression) visitExpression(case_, p);
        if (!(temp instanceof Py.MatchCase)) {
            return temp;
        } else {
            case_ = (Py.MatchCase) temp;
        }
        case_ = case_.getPadding().withGuard(
                visitLeftPadded(case_.getPadding().getGuard(), PyLeftPadded.Location.MATCH_CASE_GUARD, p)
        );
        case_ = case_.withPattern(visitAndCast(case_.getPattern(), p));
        return case_;
    }

    public J visitMultiImport(Py.MultiImport multiImport_, P p) {
        Py.MultiImport mi = multiImport_;
        mi = mi.withPrefix(visitSpace(mi.getPrefix(), PySpace.Location.MULTI_IMPORT_PREFIX, p));
        mi = mi.withMarkers(visitMarkers(mi.getMarkers(), p));
        mi = mi.getPadding().withFrom(visitRightPadded(mi.getPadding().getFrom(), PyRightPadded.Location.MULTI_IMPORT_FROM, p));
        mi = mi.getPadding().withNames(visitContainer(mi.getPadding().getNames(), PyContainer.Location.MULTI_IMPORT_NAMES, p));
        return mi;
    }

    public J visitNamedArgument(Py.NamedArgument ogArg, P p) {
        Py.NamedArgument arg = ogArg;
        arg = arg.withPrefix(visitSpace(arg.getPrefix(), PySpace.Location.NAMED_ARGUMENT_PREFIX, p));
        arg = arg.withMarkers(visitMarkers(arg.getMarkers(), p));
        Expression temp = (Expression) visitExpression(arg, p);
        if (!(temp instanceof Py.NamedArgument)) {
            return temp;
        } else {
            arg = (Py.NamedArgument) temp;
        }
        arg = arg.withName(visitAndCast(arg.getName(), p));
        arg = arg.withType(visitType(arg.getType(), p));
        return arg;
    }

    public J visitPass(Py.Pass pass, P p) {
        pass = pass.withPrefix(visitSpace(pass.getPrefix(), PySpace.Location.PASS_PREFIX, p));
        pass = pass.withMarkers(visitMarkers(pass.getMarkers(), p));
        return visitStatement(pass, p);
    }

    public J visitSpecialParameter(Py.SpecialParameter ogParam, P p) {
        Py.SpecialParameter param = ogParam;
        param = param.withPrefix(visitSpace(param.getPrefix(), PySpace.Location.SPECIAL_PARAM_PREFIX, p));
        param = param.withMarkers(visitMarkers(param.getMarkers(), p));
        param = param.withTypeHint(visitAndCast(param.getTypeHint(), p));
        return param;
    }

    public J visitStar(Py.Star star, P p) {
        Py.Star arg = star;
        arg = arg.withPrefix(visitSpace(arg.getPrefix(), PySpace.Location.STAR_PREFIX, p));
        arg = arg.withMarkers(visitMarkers(arg.getMarkers(), p));
        Expression temp = (Expression) visitExpression(arg, p);
        if (!(temp instanceof Py.Star)) {
            return temp;
        } else {
            arg = (Py.Star) temp;
        }
        arg = arg.withExpression(visitAndCast(arg.getExpression(), p));
        arg = arg.withType(visitType(arg.getType(), p));
        return arg;
    }

    public J visitSlice(Py.Slice slice, P p) {
        Py.Slice sl = slice;
        sl = sl.withPrefix(visitSpace(sl.getPrefix(), PySpace.Location.SLICE_EXPRESSION_PREFIX, p));
        sl = sl.withMarkers(visitMarkers(sl.getMarkers(), p));
        Expression temp = (Expression) visitExpression(sl, p);
        if (!(temp instanceof Py.Slice)) {
            return temp;
        } else {
            sl = (Py.Slice) temp;
        }
        sl = sl.getPadding().withStart(visitRightPadded(sl.getPadding().getStart(), PyRightPadded.Location.SLICE_EXPRESSION_START, p));
        sl = sl.getPadding().withStop(visitRightPadded(sl.getPadding().getStop(), PyRightPadded.Location.SLICE_EXPRESSION_STOP, p));
        sl = sl.getPadding().withStep(visitRightPadded(sl.getPadding().getStep(), PyRightPadded.Location.SLICE_EXPRESSION_STEP, p));
        return sl;
    }

    public J visitStatementExpression(Py.StatementExpression statementExpression, P p) {
        Py.StatementExpression expr = statementExpression;
        expr = expr.withStatement(visitAndCast(expr.getStatement(), p));
        return visitExpression(expr, p);
    }

    public J visitTypeHint(Py.TypeHint ogType, P p) {
        Py.TypeHint type = ogType;
        type = type.withPrefix(visitSpace(type.getPrefix(), PySpace.Location.EXCEPTION_TYPE_PREFIX, p));
        type = type.withMarkers(visitMarkers(type.getMarkers(), p));
        type = type.withTypeTree(visitAndCast(type.getTypeTree(), p));
        return type;
    }

    public J visitTypeHintedExpression(Py.TypeHintedExpression ogExpr, P p) {
        Py.TypeHintedExpression expr = ogExpr;
        expr = expr.withPrefix(visitSpace(expr.getPrefix(), PySpace.Location.TYPE_HINTED_EXPRESSION_PREFIX, p));
        expr = expr.withMarkers(visitMarkers(expr.getMarkers(), p));
        Expression temp = (Expression) visitExpression(expr, p);
        if (!(temp instanceof Py.TypeHintedExpression)) {
            return temp;
        } else {
            expr = (Py.TypeHintedExpression) temp;
        }
        expr = expr.withTypeHint(visitAndCast(expr.getTypeHint(), p));
        expr = expr.withExpression(visitAndCast(expr.getExpression(), p));
        return expr;
    }

    public J visitTrailingElseWrapper(Py.TrailingElseWrapper ogWrapper, P p) {
        Py.TrailingElseWrapper wrapper = ogWrapper;
        wrapper = wrapper.withPrefix(visitSpace(wrapper.getPrefix(), PySpace.Location.TRAILING_ELSE_WRAPPER_PREFIX, p));
        wrapper = wrapper.withMarkers(visitMarkers(wrapper.getMarkers(), p));
        Statement temp = (Statement) visitStatement(wrapper, p);
        if (!(temp instanceof Py.TrailingElseWrapper)) {
            return temp;
        } else {
            wrapper = (Py.TrailingElseWrapper) temp;
        }
        wrapper = wrapper.getPadding().withElseBlock(
                visitLeftPadded(wrapper.getPadding().getElseBlock(), JLeftPadded.Location.LANGUAGE_EXTENSION, p)
        );
        return wrapper;
    }

    public J visitUnionType(Py.UnionType unionType, P p) {
        Py.UnionType u = unionType;
        u = u.withPrefix(visitSpace(u.getPrefix(), PySpace.Location.UNION_TYPE_PREFIX, p));
        u = u.withMarkers(visitMarkers(u.getMarkers(), p));
        Expression temp = (Expression) visitExpression(u, p);
        if (!(temp instanceof Py.UnionType)) {
            return temp;
        } else {
            u = (Py.UnionType) temp;
        }
        u = u.getPadding().withTypes(ListUtils.map(u.getPadding().getTypes(), e -> visitRightPadded(e, PyRightPadded.Location.UNION_TYPE_TYPE, p)));
        return u;
    }

    public J visitVariableScope(Py.VariableScope ogStmt, P p) {
        Py.VariableScope stmt = ogStmt;
        stmt = stmt.withPrefix(visitSpace(stmt.getPrefix(), PySpace.Location.VARIABLE_SCOPE_PREFIX, p));
        stmt = stmt.withMarkers(visitMarkers(stmt.getMarkers(), p));
        Statement temp = (Statement) visitStatement(stmt, p);
        if (!(temp instanceof Py.VariableScope)) {
            return temp;
        } else {
            stmt = (Py.VariableScope) temp;
        }
        stmt = stmt.getPadding().withNames(ListUtils.map(
                stmt.getPadding().getNames(),
                t -> visitRightPadded(t, PyRightPadded.Location.VARIABLE_SCOPE_ELEMENT, p)
        ));
        return stmt;
    }

    public J visitYieldFrom(Py.YieldFrom ogYield, P p) {
        Py.YieldFrom yield = ogYield;
        yield = yield.withPrefix(visitSpace(yield.getPrefix(), PySpace.Location.YIELD_FROM_PREFIX, p));
        yield = yield.withMarkers(visitMarkers(yield.getMarkers(), p));
        Expression temp = (Expression) visitExpression(yield, p);
        if (!(temp instanceof Py.YieldFrom)) {
            return temp;
        } else {
            yield = (Py.YieldFrom) temp;
        }
        return yield;
    }

    @Override
    public J visitCompilationUnit(J.CompilationUnit cu, P p) {
        throw new UnsupportedOperationException("Python has a different structure for its compilation unit. See P.CompilationUnit.");
    }

    public <T> JRightPadded<T> visitRightPadded(@Nullable JRightPadded<T> right, PyRightPadded.Location loc, P p) {
        return super.visitRightPadded(right, JRightPadded.Location.LANGUAGE_EXTENSION, p);
    }

    public <T> JLeftPadded<T> visitLeftPadded(@Nullable JLeftPadded<T> left, PyLeftPadded.Location loc, P p) {
        return super.visitLeftPadded(left, JLeftPadded.Location.LANGUAGE_EXTENSION, p);
    }

    public Space visitSpace(Space space, PySpace.Location loc, P p) {
        return visitSpace(space, Space.Location.LANGUAGE_EXTENSION, p);
    }

    public <J2 extends J> JContainer<J2> visitContainer(JContainer<J2> container, PyContainer.Location loc, P p) {
        return super.visitContainer(container, JContainer.Location.LANGUAGE_EXTENSION, p);
    }
}
