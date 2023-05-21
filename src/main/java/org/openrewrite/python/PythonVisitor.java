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

import org.openrewrite.SourceFile;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.JavaVisitor;
import org.openrewrite.java.tree.*;
import org.openrewrite.java.tree.J.CompilationUnit;
import org.openrewrite.python.tree.*;

/**
 * Visit K types.
 */
public class PythonVisitor<P> extends JavaVisitor<P> {

    @Override
    public boolean isAcceptable(SourceFile sourceFile, P p) {
        return sourceFile instanceof Py.CompilationUnit;
    }

    @Override
    public String getLanguage() {
        return "python";
    }

    @Override
    public J visitJavaSourceFile(JavaSourceFile cu, P p) {
        return cu instanceof Py.CompilationUnit ? visitCompilationUnit((Py.CompilationUnit) cu, p) : cu;
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

    @Override
    public J visitCompilationUnit(CompilationUnit cu, P p) {
        throw new UnsupportedOperationException("Python has a different structure for its compilation unit. See P.CompilationUnit.");
    }

    public J visitPassStatement(Py.PassStatement ogPass, P p) {
        Py.PassStatement pass = ogPass;
        pass = pass.withPrefix(visitSpace(pass.getPrefix(), PySpace.Location.PASS_PREFIX, p));
        pass = pass.withMarkers(visitMarkers(pass.getMarkers(), p));
        return visitStatement(pass, p);
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

    public J visitAwaitExpression(Py.AwaitExpression ogAwait, P p) {
        Py.AwaitExpression await = ogAwait;
        await = await.withPrefix(visitSpace(await.getPrefix(), PySpace.Location.AWAIT_PREFIX, p));
        await = await.withMarkers(visitMarkers(await.getMarkers(), p));
        Expression temp = (Expression) visitExpression(await, p);
        if (!(temp instanceof Py.AwaitExpression)) {
            return temp;
        } else {
            await = (Py.AwaitExpression) temp;
        }
        await = await.withExpression(visitAndCast(await.getExpression(), p));
        await = await.withType(visitType(await.getType(), p));
        return await;
    }

    public J visitAssertStatement(Py.AssertStatement ogAssert, P p) {
        Py.AssertStatement assert_ = ogAssert;
        assert_ = assert_.withPrefix(visitSpace(assert_.getPrefix(), PySpace.Location.ASSERT_PREFIX, p));
        assert_ = assert_.withMarkers(visitMarkers(assert_.getMarkers(), p));
        Statement temp = (Statement) visitStatement(assert_, p);
        if (!(temp instanceof Py.AssertStatement)) {
            return temp;
        } else {
            assert_ = (Py.AssertStatement) temp;
        }
        assert_ = assert_.getPadding().withExpressions(ListUtils.map(
                assert_.getPadding().getExpressions(),
                t -> visitRightPadded(t, PyRightPadded.Location.ASSERT_ELEMENT, p)
        ));
        return assert_;
    }

    public J visitYieldExpression(Py.YieldExpression ogYield, P p) {
        Py.YieldExpression yield = ogYield;
        yield = yield.withPrefix(visitSpace(yield.getPrefix(), PySpace.Location.YIELD_PREFIX, p));
        yield = yield.withMarkers(visitMarkers(yield.getMarkers(), p));
        Expression temp = (Expression) visitExpression(yield, p);
        if (!(temp instanceof Py.YieldExpression)) {
            return temp;
        } else {
            yield = (Py.YieldExpression) temp;
        }
        yield = yield.getPadding().withFrom(
                visitLeftPadded(yield.getPadding().getFrom(), PyLeftPadded.Location.YIELD_FROM, p)
        );
        yield = yield.getPadding().withExpressions(ListUtils.map(
                yield.getPadding().getExpressions(),
                t -> visitRightPadded(t, PyRightPadded.Location.YIELD_ELEMENT, p)
        ));
        return yield;
    }

    public J visitDelStatement(Py.DelStatement ogDel, P p) {
        Py.DelStatement del = ogDel;
        del = del.withPrefix(visitSpace(del.getPrefix(), PySpace.Location.DEL_PREFIX, p));
        del = del.withMarkers(visitMarkers(del.getMarkers(), p));
        Statement temp = (Statement) visitStatement(del, p);
        if (!(temp instanceof Py.DelStatement)) {
            return temp;
        } else {
            del = (Py.DelStatement) temp;
        }
        del = del.getPadding().withTargets(ListUtils.map(
                del.getPadding().getTargets(),
                t -> visitRightPadded(t, PyRightPadded.Location.DEL_ELEMENT, p)
        ));
        return del;
    }

    public J visitExceptionType(Py.ExceptionType ogType, P p) {
        Py.ExceptionType type = ogType;
        type = type.withPrefix(visitSpace(type.getPrefix(), PySpace.Location.EXCEPTION_TYPE_PREFIX, p));
        type = type.withMarkers(visitMarkers(type.getMarkers(), p));
        type = type.withExpression(visitAndCast(type.getExpression(), p));
        return type;
    }

    public J visitTypeHint(Py.TypeHint ogType, P p) {
        Py.TypeHint type = ogType;
        type = type.withPrefix(visitSpace(type.getPrefix(), PySpace.Location.EXCEPTION_TYPE_PREFIX, p));
        type = type.withMarkers(visitMarkers(type.getMarkers(), p));
        type = type.withExpression(visitAndCast(type.getExpression(), p));
        return type;
    }

    public J visitVariableScopeStatement(Py.VariableScopeStatement ogStmt, P p) {
        Py.VariableScopeStatement stmt = ogStmt;
        stmt = stmt.withPrefix(visitSpace(stmt.getPrefix(), PySpace.Location.VARIABLE_SCOPE_PREFIX, p));
        stmt = stmt.withMarkers(visitMarkers(stmt.getMarkers(), p));
        Statement temp = (Statement) visitStatement(stmt, p);
        if (!(temp instanceof Py.VariableScopeStatement)) {
            return temp;
        } else {
            stmt = (Py.VariableScopeStatement) temp;
        }
        stmt = stmt.getPadding().withNames(ListUtils.map(
                stmt.getPadding().getNames(),
                t -> visitRightPadded(t, PyRightPadded.Location.VARIABLE_SCOPE_ELEMENT, p)
        ));
        return stmt;
    }

    public J visitErrorFromExpression(Py.ErrorFromExpression ogExpr, P p) {
        Py.ErrorFromExpression expr = ogExpr;
        expr = expr.withPrefix(visitSpace(expr.getPrefix(), PySpace.Location.ERROR_FROM_PREFIX, p));
        expr = expr.withMarkers(visitMarkers(expr.getMarkers(), p));
        Expression temp = (Expression) visitExpression(expr, p);
        if (!(temp instanceof Py.ErrorFromExpression)) {
            return temp;
        } else {
            expr = (Py.ErrorFromExpression) temp;
        }
        expr = expr.withError(visitAndCast(expr.getError(), p));
        expr = expr.getPadding().withFrom(
                visitLeftPadded(expr.getPadding().getFrom(), PyLeftPadded.Location.ERROR_FROM, p)
        );
        return expr;
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

    public J visitSpecialParameter(Py.SpecialParameter ogParam, P p) {
        Py.SpecialParameter param = ogParam;
        param = param.withPrefix(visitSpace(param.getPrefix(), PySpace.Location.SPECIAL_PARAM_PREFIX, p));
        param = param.withMarkers(visitMarkers(param.getMarkers(), p));
        param = param.withTypeHint(visitAndCast(param.getTypeHint(), p));
        return param;
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

    public J visitSpecialArgument(Py.SpecialArgument ogArg, P p) {
        Py.SpecialArgument arg = ogArg;
        arg = arg.withPrefix(visitSpace(arg.getPrefix(), PySpace.Location.SPECIAL_ARG_PREFIX, p));
        arg = arg.withMarkers(visitMarkers(arg.getMarkers(), p));
        Expression temp = (Expression) visitExpression(arg, p);
        if (!(temp instanceof Py.SpecialArgument)) {
            return temp;
        } else {
            arg = (Py.SpecialArgument) temp;
        }
        arg = arg.withExpression(visitAndCast(arg.getExpression(), p));
        arg = arg.withType(visitType(arg.getType(), p));
        return arg;
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
}
