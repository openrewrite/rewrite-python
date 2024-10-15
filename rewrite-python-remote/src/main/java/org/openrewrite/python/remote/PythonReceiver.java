/*
 * Copyright 2024 the original author or authors.
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
package org.openrewrite.python.remote;

import java.nio.charset.Charset;
import java.nio.file.Path;
import java.util.UUID;

import lombok.Value;
import org.jspecify.annotations.Nullable;
import org.openrewrite.Checksum;
import org.openrewrite.Cursor;
import org.openrewrite.FileAttributes;
import org.openrewrite.Tree;
import org.openrewrite.java.tree.Comment;
import org.openrewrite.java.tree.J;
import org.openrewrite.java.tree.JContainer;
import org.openrewrite.java.tree.JLeftPadded;
import org.openrewrite.java.tree.JRightPadded;
import org.openrewrite.java.tree.JavaType;
import org.openrewrite.java.tree.Space;
import org.openrewrite.python.PythonVisitor;
import org.openrewrite.python.tree.Py;
import org.openrewrite.remote.Receiver;
import org.openrewrite.remote.ReceiverContext;
import org.openrewrite.remote.ReceiverFactory;

@Value
public class PythonReceiver implements Receiver<Py> {

    @Override
    public Py receive(@Nullable Py before, ReceiverContext ctx) {
        ReceiverContext forked = fork(ctx);
        //noinspection DataFlowIssue
        return (Py) forked.getVisitor().visit(before, forked);
    }

    @Override
    public ReceiverContext fork(ReceiverContext ctx) {
        return ctx.fork(new Visitor(), new Factory());
    }

    private static class Visitor extends PythonVisitor<ReceiverContext> {

        public @Nullable J visit(@Nullable Tree tree, ReceiverContext ctx) {
            //noinspection DataFlowIssue
            Cursor cursor = new Cursor(getCursor(), tree);
            setCursor(cursor);

            tree = ctx.receiveNode((J) tree, ctx::receiveTree);

            setCursor(cursor.getParent());
            return (J) tree;
        }

        @Override
        public Py.Binary visitBinary(Py.Binary binary, ReceiverContext ctx) {
            binary = binary.withId(ctx.receiveNonNullValue(binary.getId(), UUID.class));
            binary = binary.withPrefix(ctx.receiveNonNullNode(binary.getPrefix(), PythonReceiver::receiveSpace));
            binary = binary.withMarkers(ctx.receiveNonNullNode(binary.getMarkers(), ctx::receiveMarkers));
            binary = binary.withLeft(ctx.receiveNonNullNode(binary.getLeft(), ctx::receiveTree));
            binary = binary.getPadding().withOperator(ctx.receiveNonNullNode(binary.getPadding().getOperator(), leftPaddedValueReceiver(org.openrewrite.python.tree.Py.Binary.Type.class)));
            binary = binary.withNegation(ctx.receiveNode(binary.getNegation(), PythonReceiver::receiveSpace));
            binary = binary.withRight(ctx.receiveNonNullNode(binary.getRight(), ctx::receiveTree));
            binary = binary.withType(ctx.receiveValue(binary.getType(), JavaType.class));
            return binary;
        }

        @Override
        public Py.ExceptionType visitExceptionType(Py.ExceptionType exceptionType, ReceiverContext ctx) {
            exceptionType = exceptionType.withId(ctx.receiveNonNullValue(exceptionType.getId(), UUID.class));
            exceptionType = exceptionType.withPrefix(ctx.receiveNonNullNode(exceptionType.getPrefix(), PythonReceiver::receiveSpace));
            exceptionType = exceptionType.withMarkers(ctx.receiveNonNullNode(exceptionType.getMarkers(), ctx::receiveMarkers));
            exceptionType = exceptionType.withType(ctx.receiveValue(exceptionType.getType(), JavaType.class));
            exceptionType = exceptionType.withExceptionGroup(ctx.receiveNonNullValue(exceptionType.isExceptionGroup(), boolean.class));
            exceptionType = exceptionType.withExpression(ctx.receiveNonNullNode(exceptionType.getExpression(), ctx::receiveTree));
            return exceptionType;
        }

        @Override
        public Py.TypeHint visitTypeHint(Py.TypeHint typeHint, ReceiverContext ctx) {
            typeHint = typeHint.withId(ctx.receiveNonNullValue(typeHint.getId(), UUID.class));
            typeHint = typeHint.withPrefix(ctx.receiveNonNullNode(typeHint.getPrefix(), PythonReceiver::receiveSpace));
            typeHint = typeHint.withMarkers(ctx.receiveNonNullNode(typeHint.getMarkers(), ctx::receiveMarkers));
            typeHint = typeHint.withTypeTree(ctx.receiveNonNullNode(typeHint.getTypeTree(), ctx::receiveTree));
            typeHint = typeHint.withType(ctx.receiveValue(typeHint.getType(), JavaType.class));
            return typeHint;
        }

        @Override
        public Py.CompilationUnit visitCompilationUnit(Py.CompilationUnit compilationUnit, ReceiverContext ctx) {
            compilationUnit = compilationUnit.withId(ctx.receiveNonNullValue(compilationUnit.getId(), UUID.class));
            compilationUnit = compilationUnit.withPrefix(ctx.receiveNonNullNode(compilationUnit.getPrefix(), PythonReceiver::receiveSpace));
            compilationUnit = compilationUnit.withMarkers(ctx.receiveNonNullNode(compilationUnit.getMarkers(), ctx::receiveMarkers));
            compilationUnit = compilationUnit.withSourcePath(ctx.receiveNonNullValue(compilationUnit.getSourcePath(), Path.class));
            compilationUnit = compilationUnit.withFileAttributes(ctx.receiveValue(compilationUnit.getFileAttributes(), FileAttributes.class));
            String charsetName = ctx.receiveValue(compilationUnit.getCharset().name(), String.class);
            if (charsetName != null) {
                compilationUnit = (Py.CompilationUnit) compilationUnit.withCharset(Charset.forName(charsetName));
            }
            compilationUnit = compilationUnit.withCharsetBomMarked(ctx.receiveNonNullValue(compilationUnit.isCharsetBomMarked(), boolean.class));
            compilationUnit = compilationUnit.withChecksum(ctx.receiveValue(compilationUnit.getChecksum(), Checksum.class));
            compilationUnit = compilationUnit.getPadding().withImports(ctx.receiveNonNullNodes(compilationUnit.getPadding().getImports(), PythonReceiver::receiveRightPaddedTree));
            compilationUnit = compilationUnit.getPadding().withStatements(ctx.receiveNonNullNodes(compilationUnit.getPadding().getStatements(), PythonReceiver::receiveRightPaddedTree));
            compilationUnit = compilationUnit.withEof(ctx.receiveNonNullNode(compilationUnit.getEof(), PythonReceiver::receiveSpace));
            return compilationUnit;
        }

        @Override
        public Py.ExpressionStatement visitExpressionStatement(Py.ExpressionStatement expressionStatement, ReceiverContext ctx) {
            expressionStatement = expressionStatement.withId(ctx.receiveNonNullValue(expressionStatement.getId(), UUID.class));
            expressionStatement = expressionStatement.withExpression(ctx.receiveNonNullNode(expressionStatement.getExpression(), ctx::receiveTree));
            return expressionStatement;
        }

        @Override
        public Py.StatementExpression visitStatementExpression(Py.StatementExpression statementExpression, ReceiverContext ctx) {
            statementExpression = statementExpression.withId(ctx.receiveNonNullValue(statementExpression.getId(), UUID.class));
            statementExpression = statementExpression.withStatement(ctx.receiveNonNullNode(statementExpression.getStatement(), ctx::receiveTree));
            return statementExpression;
        }

        @Override
        public Py.MultiImport visitMultiImport(Py.MultiImport multiImport, ReceiverContext ctx) {
            multiImport = multiImport.withId(ctx.receiveNonNullValue(multiImport.getId(), UUID.class));
            multiImport = multiImport.withPrefix(ctx.receiveNonNullNode(multiImport.getPrefix(), PythonReceiver::receiveSpace));
            multiImport = multiImport.withMarkers(ctx.receiveNonNullNode(multiImport.getMarkers(), ctx::receiveMarkers));
            multiImport = multiImport.getPadding().withFrom(ctx.receiveNode(multiImport.getPadding().getFrom(), PythonReceiver::receiveRightPaddedTree));
            multiImport = multiImport.withParenthesized(ctx.receiveNonNullValue(multiImport.isParenthesized(), boolean.class));
            multiImport = multiImport.getPadding().withNames(ctx.receiveNonNullNode(multiImport.getPadding().getNames(), PythonReceiver::receiveContainer));
            return multiImport;
        }

        @Override
        public Py.KeyValue visitKeyValue(Py.KeyValue keyValue, ReceiverContext ctx) {
            keyValue = keyValue.withId(ctx.receiveNonNullValue(keyValue.getId(), UUID.class));
            keyValue = keyValue.withPrefix(ctx.receiveNonNullNode(keyValue.getPrefix(), PythonReceiver::receiveSpace));
            keyValue = keyValue.withMarkers(ctx.receiveNonNullNode(keyValue.getMarkers(), ctx::receiveMarkers));
            keyValue = keyValue.getPadding().withKey(ctx.receiveNonNullNode(keyValue.getPadding().getKey(), PythonReceiver::receiveRightPaddedTree));
            keyValue = keyValue.withValue(ctx.receiveNonNullNode(keyValue.getValue(), ctx::receiveTree));
            keyValue = keyValue.withType(ctx.receiveValue(keyValue.getType(), JavaType.class));
            return keyValue;
        }

        @Override
        public Py.DictLiteral visitDictLiteral(Py.DictLiteral dictLiteral, ReceiverContext ctx) {
            dictLiteral = dictLiteral.withId(ctx.receiveNonNullValue(dictLiteral.getId(), UUID.class));
            dictLiteral = dictLiteral.withPrefix(ctx.receiveNonNullNode(dictLiteral.getPrefix(), PythonReceiver::receiveSpace));
            dictLiteral = dictLiteral.withMarkers(ctx.receiveNonNullNode(dictLiteral.getMarkers(), ctx::receiveMarkers));
            dictLiteral = dictLiteral.getPadding().withElements(ctx.receiveNonNullNode(dictLiteral.getPadding().getElements(), PythonReceiver::receiveContainer));
            dictLiteral = dictLiteral.withType(ctx.receiveValue(dictLiteral.getType(), JavaType.class));
            return dictLiteral;
        }

        @Override
        public Py.CollectionLiteral visitCollectionLiteral(Py.CollectionLiteral collectionLiteral, ReceiverContext ctx) {
            collectionLiteral = collectionLiteral.withId(ctx.receiveNonNullValue(collectionLiteral.getId(), UUID.class));
            collectionLiteral = collectionLiteral.withPrefix(ctx.receiveNonNullNode(collectionLiteral.getPrefix(), PythonReceiver::receiveSpace));
            collectionLiteral = collectionLiteral.withMarkers(ctx.receiveNonNullNode(collectionLiteral.getMarkers(), ctx::receiveMarkers));
            collectionLiteral = collectionLiteral.withKind(ctx.receiveNonNullValue(collectionLiteral.getKind(), Py.CollectionLiteral.Kind.class));
            collectionLiteral = collectionLiteral.getPadding().withElements(ctx.receiveNonNullNode(collectionLiteral.getPadding().getElements(), PythonReceiver::receiveContainer));
            collectionLiteral = collectionLiteral.withType(ctx.receiveValue(collectionLiteral.getType(), JavaType.class));
            return collectionLiteral;
        }

        @Override
        public Py.FormattedString visitFormattedString(Py.FormattedString formattedString, ReceiverContext ctx) {
            formattedString = formattedString.withId(ctx.receiveNonNullValue(formattedString.getId(), UUID.class));
            formattedString = formattedString.withPrefix(ctx.receiveNonNullNode(formattedString.getPrefix(), PythonReceiver::receiveSpace));
            formattedString = formattedString.withMarkers(ctx.receiveNonNullNode(formattedString.getMarkers(), ctx::receiveMarkers));
            formattedString = formattedString.withDelimiter(ctx.receiveNonNullValue(formattedString.getDelimiter(), String.class));
            formattedString = formattedString.withParts(ctx.receiveNonNullNodes(formattedString.getParts(), ctx::receiveTree));
            return formattedString;
        }

        @Override
        public Py.FormattedString.Value visitFormattedStringValue(Py.FormattedString.Value value, ReceiverContext ctx) {
            value = value.withId(ctx.receiveNonNullValue(value.getId(), UUID.class));
            value = value.withPrefix(ctx.receiveNonNullNode(value.getPrefix(), PythonReceiver::receiveSpace));
            value = value.withMarkers(ctx.receiveNonNullNode(value.getMarkers(), ctx::receiveMarkers));
            value = value.getPadding().withExpression(ctx.receiveNonNullNode(value.getPadding().getExpression(), PythonReceiver::receiveRightPaddedTree));
            value = value.getPadding().withDebug(ctx.receiveNode(value.getPadding().getDebug(), rightPaddedValueReceiver(
		            Boolean.class)));
            value = value.withConversion(ctx.receiveValue(value.getConversion(), Py.FormattedString.Value.Conversion.class));
            value = value.withFormat(ctx.receiveNode(value.getFormat(), ctx::receiveTree));
            return value;
        }

        @Override
        public Py.Pass visitPass(Py.Pass pass, ReceiverContext ctx) {
            pass = pass.withId(ctx.receiveNonNullValue(pass.getId(), UUID.class));
            pass = pass.withPrefix(ctx.receiveNonNullNode(pass.getPrefix(), PythonReceiver::receiveSpace));
            pass = pass.withMarkers(ctx.receiveNonNullNode(pass.getMarkers(), ctx::receiveMarkers));
            return pass;
        }

        @Override
        public Py.TrailingElseWrapper visitTrailingElseWrapper(Py.TrailingElseWrapper trailingElseWrapper, ReceiverContext ctx) {
            trailingElseWrapper = trailingElseWrapper.withId(ctx.receiveNonNullValue(trailingElseWrapper.getId(), UUID.class));
            trailingElseWrapper = trailingElseWrapper.withPrefix(ctx.receiveNonNullNode(trailingElseWrapper.getPrefix(), PythonReceiver::receiveSpace));
            trailingElseWrapper = trailingElseWrapper.withMarkers(ctx.receiveNonNullNode(trailingElseWrapper.getMarkers(), ctx::receiveMarkers));
            trailingElseWrapper = trailingElseWrapper.withStatement(ctx.receiveNonNullNode(trailingElseWrapper.getStatement(), ctx::receiveTree));
            trailingElseWrapper = trailingElseWrapper.getPadding().withElseBlock(ctx.receiveNonNullNode(trailingElseWrapper.getPadding().getElseBlock(), PythonReceiver::receiveLeftPaddedTree));
            return trailingElseWrapper;
        }

        @Override
        public Py.ComprehensionExpression visitComprehensionExpression(Py.ComprehensionExpression comprehensionExpression, ReceiverContext ctx) {
            comprehensionExpression = comprehensionExpression.withId(ctx.receiveNonNullValue(comprehensionExpression.getId(), UUID.class));
            comprehensionExpression = comprehensionExpression.withPrefix(ctx.receiveNonNullNode(comprehensionExpression.getPrefix(), PythonReceiver::receiveSpace));
            comprehensionExpression = comprehensionExpression.withMarkers(ctx.receiveNonNullNode(comprehensionExpression.getMarkers(), ctx::receiveMarkers));
            comprehensionExpression = comprehensionExpression.withKind(ctx.receiveNonNullValue(comprehensionExpression.getKind(), Py.ComprehensionExpression.Kind.class));
            comprehensionExpression = comprehensionExpression.withResult(ctx.receiveNonNullNode(comprehensionExpression.getResult(), ctx::receiveTree));
            comprehensionExpression = comprehensionExpression.withClauses(ctx.receiveNonNullNodes(comprehensionExpression.getClauses(), ctx::receiveTree));
            comprehensionExpression = comprehensionExpression.withSuffix(ctx.receiveNonNullNode(comprehensionExpression.getSuffix(), PythonReceiver::receiveSpace));
            comprehensionExpression = comprehensionExpression.withType(ctx.receiveValue(comprehensionExpression.getType(), JavaType.class));
            return comprehensionExpression;
        }

        @Override
        public Py.ComprehensionExpression.Condition visitComprehensionCondition(Py.ComprehensionExpression.Condition condition, ReceiverContext ctx) {
            condition = condition.withId(ctx.receiveNonNullValue(condition.getId(), UUID.class));
            condition = condition.withPrefix(ctx.receiveNonNullNode(condition.getPrefix(), PythonReceiver::receiveSpace));
            condition = condition.withMarkers(ctx.receiveNonNullNode(condition.getMarkers(), ctx::receiveMarkers));
            condition = condition.withExpression(ctx.receiveNonNullNode(condition.getExpression(), ctx::receiveTree));
            return condition;
        }

        @Override
        public Py.ComprehensionExpression.Clause visitComprehensionClause(Py.ComprehensionExpression.Clause clause, ReceiverContext ctx) {
            clause = clause.withId(ctx.receiveNonNullValue(clause.getId(), UUID.class));
            clause = clause.withPrefix(ctx.receiveNonNullNode(clause.getPrefix(), PythonReceiver::receiveSpace));
            clause = clause.withMarkers(ctx.receiveNonNullNode(clause.getMarkers(), ctx::receiveMarkers));
            clause = clause.withIteratorVariable(ctx.receiveNonNullNode(clause.getIteratorVariable(), ctx::receiveTree));
            clause = clause.getPadding().withIteratedList(ctx.receiveNonNullNode(clause.getPadding().getIteratedList(), PythonReceiver::receiveLeftPaddedTree));
            clause = clause.withConditions(ctx.receiveNodes(clause.getConditions(), ctx::receiveTree));
            return clause;
        }

        @Override
        public Py.Await visitAwait(Py.Await await, ReceiverContext ctx) {
            await = await.withId(ctx.receiveNonNullValue(await.getId(), UUID.class));
            await = await.withPrefix(ctx.receiveNonNullNode(await.getPrefix(), PythonReceiver::receiveSpace));
            await = await.withMarkers(ctx.receiveNonNullNode(await.getMarkers(), ctx::receiveMarkers));
            await = await.withExpression(ctx.receiveNonNullNode(await.getExpression(), ctx::receiveTree));
            await = await.withType(ctx.receiveValue(await.getType(), JavaType.class));
            return await;
        }

        @Override
        public Py.YieldFrom visitYieldFrom(Py.YieldFrom yieldFrom, ReceiverContext ctx) {
            yieldFrom = yieldFrom.withId(ctx.receiveNonNullValue(yieldFrom.getId(), UUID.class));
            yieldFrom = yieldFrom.withPrefix(ctx.receiveNonNullNode(yieldFrom.getPrefix(), PythonReceiver::receiveSpace));
            yieldFrom = yieldFrom.withMarkers(ctx.receiveNonNullNode(yieldFrom.getMarkers(), ctx::receiveMarkers));
            yieldFrom = yieldFrom.withExpression(ctx.receiveNonNullNode(yieldFrom.getExpression(), ctx::receiveTree));
            yieldFrom = yieldFrom.withType(ctx.receiveValue(yieldFrom.getType(), JavaType.class));
            return yieldFrom;
        }

        @Override
        public Py.VariableScope visitVariableScope(Py.VariableScope variableScope, ReceiverContext ctx) {
            variableScope = variableScope.withId(ctx.receiveNonNullValue(variableScope.getId(), UUID.class));
            variableScope = variableScope.withPrefix(ctx.receiveNonNullNode(variableScope.getPrefix(), PythonReceiver::receiveSpace));
            variableScope = variableScope.withMarkers(ctx.receiveNonNullNode(variableScope.getMarkers(), ctx::receiveMarkers));
            variableScope = variableScope.withKind(ctx.receiveNonNullValue(variableScope.getKind(), Py.VariableScope.Kind.class));
            variableScope = variableScope.getPadding().withNames(ctx.receiveNonNullNodes(variableScope.getPadding().getNames(), PythonReceiver::receiveRightPaddedTree));
            return variableScope;
        }

        @Override
        public Py.Del visitDel(Py.Del del, ReceiverContext ctx) {
            del = del.withId(ctx.receiveNonNullValue(del.getId(), UUID.class));
            del = del.withPrefix(ctx.receiveNonNullNode(del.getPrefix(), PythonReceiver::receiveSpace));
            del = del.withMarkers(ctx.receiveNonNullNode(del.getMarkers(), ctx::receiveMarkers));
            del = del.getPadding().withTargets(ctx.receiveNonNullNodes(del.getPadding().getTargets(), PythonReceiver::receiveRightPaddedTree));
            return del;
        }

        @Override
        public Py.SpecialParameter visitSpecialParameter(Py.SpecialParameter specialParameter, ReceiverContext ctx) {
            specialParameter = specialParameter.withId(ctx.receiveNonNullValue(specialParameter.getId(), UUID.class));
            specialParameter = specialParameter.withPrefix(ctx.receiveNonNullNode(specialParameter.getPrefix(), PythonReceiver::receiveSpace));
            specialParameter = specialParameter.withMarkers(ctx.receiveNonNullNode(specialParameter.getMarkers(), ctx::receiveMarkers));
            specialParameter = specialParameter.withKind(ctx.receiveNonNullValue(specialParameter.getKind(), Py.SpecialParameter.Kind.class));
            specialParameter = specialParameter.withTypeHint(ctx.receiveNode(specialParameter.getTypeHint(), ctx::receiveTree));
            specialParameter = specialParameter.withType(ctx.receiveValue(specialParameter.getType(), JavaType.class));
            return specialParameter;
        }

        @Override
        public Py.Star visitStar(Py.Star star, ReceiverContext ctx) {
            star = star.withId(ctx.receiveNonNullValue(star.getId(), UUID.class));
            star = star.withPrefix(ctx.receiveNonNullNode(star.getPrefix(), PythonReceiver::receiveSpace));
            star = star.withMarkers(ctx.receiveNonNullNode(star.getMarkers(), ctx::receiveMarkers));
            star = star.withKind(ctx.receiveNonNullValue(star.getKind(), Py.Star.Kind.class));
            star = star.withExpression(ctx.receiveNonNullNode(star.getExpression(), ctx::receiveTree));
            star = star.withType(ctx.receiveValue(star.getType(), JavaType.class));
            return star;
        }

        @Override
        public Py.NamedArgument visitNamedArgument(Py.NamedArgument namedArgument, ReceiverContext ctx) {
            namedArgument = namedArgument.withId(ctx.receiveNonNullValue(namedArgument.getId(), UUID.class));
            namedArgument = namedArgument.withPrefix(ctx.receiveNonNullNode(namedArgument.getPrefix(), PythonReceiver::receiveSpace));
            namedArgument = namedArgument.withMarkers(ctx.receiveNonNullNode(namedArgument.getMarkers(), ctx::receiveMarkers));
            namedArgument = namedArgument.withName(ctx.receiveNonNullNode(namedArgument.getName(), ctx::receiveTree));
            namedArgument = namedArgument.getPadding().withValue(ctx.receiveNonNullNode(namedArgument.getPadding().getValue(), PythonReceiver::receiveLeftPaddedTree));
            namedArgument = namedArgument.withType(ctx.receiveValue(namedArgument.getType(), JavaType.class));
            return namedArgument;
        }

        @Override
        public Py.TypeHintedExpression visitTypeHintedExpression(Py.TypeHintedExpression typeHintedExpression, ReceiverContext ctx) {
            typeHintedExpression = typeHintedExpression.withId(ctx.receiveNonNullValue(typeHintedExpression.getId(), UUID.class));
            typeHintedExpression = typeHintedExpression.withPrefix(ctx.receiveNonNullNode(typeHintedExpression.getPrefix(), PythonReceiver::receiveSpace));
            typeHintedExpression = typeHintedExpression.withMarkers(ctx.receiveNonNullNode(typeHintedExpression.getMarkers(), ctx::receiveMarkers));
            typeHintedExpression = typeHintedExpression.withTypeHint(ctx.receiveNonNullNode(typeHintedExpression.getTypeHint(), ctx::receiveTree));
            typeHintedExpression = typeHintedExpression.withExpression(ctx.receiveNonNullNode(typeHintedExpression.getExpression(), ctx::receiveTree));
            typeHintedExpression = typeHintedExpression.withType(ctx.receiveValue(typeHintedExpression.getType(), JavaType.class));
            return typeHintedExpression;
        }

        @Override
        public Py.ErrorFrom visitErrorFrom(Py.ErrorFrom errorFrom, ReceiverContext ctx) {
            errorFrom = errorFrom.withId(ctx.receiveNonNullValue(errorFrom.getId(), UUID.class));
            errorFrom = errorFrom.withPrefix(ctx.receiveNonNullNode(errorFrom.getPrefix(), PythonReceiver::receiveSpace));
            errorFrom = errorFrom.withMarkers(ctx.receiveNonNullNode(errorFrom.getMarkers(), ctx::receiveMarkers));
            errorFrom = errorFrom.withError(ctx.receiveNonNullNode(errorFrom.getError(), ctx::receiveTree));
            errorFrom = errorFrom.getPadding().withFrom(ctx.receiveNonNullNode(errorFrom.getPadding().getFrom(), PythonReceiver::receiveLeftPaddedTree));
            errorFrom = errorFrom.withType(ctx.receiveValue(errorFrom.getType(), JavaType.class));
            return errorFrom;
        }

        @Override
        public Py.MatchCase visitMatchCase(Py.MatchCase matchCase, ReceiverContext ctx) {
            matchCase = matchCase.withId(ctx.receiveNonNullValue(matchCase.getId(), UUID.class));
            matchCase = matchCase.withPrefix(ctx.receiveNonNullNode(matchCase.getPrefix(), PythonReceiver::receiveSpace));
            matchCase = matchCase.withMarkers(ctx.receiveNonNullNode(matchCase.getMarkers(), ctx::receiveMarkers));
            matchCase = matchCase.withPattern(ctx.receiveNonNullNode(matchCase.getPattern(), ctx::receiveTree));
            matchCase = matchCase.getPadding().withGuard(ctx.receiveNode(matchCase.getPadding().getGuard(), PythonReceiver::receiveLeftPaddedTree));
            matchCase = matchCase.withType(ctx.receiveValue(matchCase.getType(), JavaType.class));
            return matchCase;
        }

        @Override
        public Py.MatchCase.Pattern visitMatchCasePattern(Py.MatchCase.Pattern pattern, ReceiverContext ctx) {
            pattern = pattern.withId(ctx.receiveNonNullValue(pattern.getId(), UUID.class));
            pattern = pattern.withPrefix(ctx.receiveNonNullNode(pattern.getPrefix(), PythonReceiver::receiveSpace));
            pattern = pattern.withMarkers(ctx.receiveNonNullNode(pattern.getMarkers(), ctx::receiveMarkers));
            pattern = pattern.withKind(ctx.receiveNonNullValue(pattern.getKind(), Py.MatchCase.Pattern.Kind.class));
            pattern = pattern.getPadding().withChildren(ctx.receiveNonNullNode(pattern.getPadding().getChildren(), PythonReceiver::receiveContainer));
            pattern = pattern.withType(ctx.receiveValue(pattern.getType(), JavaType.class));
            return pattern;
        }

        @Override
        public Py.Slice visitSlice(Py.Slice slice, ReceiverContext ctx) {
            slice = slice.withId(ctx.receiveNonNullValue(slice.getId(), UUID.class));
            slice = slice.withPrefix(ctx.receiveNonNullNode(slice.getPrefix(), PythonReceiver::receiveSpace));
            slice = slice.withMarkers(ctx.receiveNonNullNode(slice.getMarkers(), ctx::receiveMarkers));
            slice = slice.getPadding().withStart(ctx.receiveNode(slice.getPadding().getStart(), PythonReceiver::receiveRightPaddedTree));
            slice = slice.getPadding().withStop(ctx.receiveNode(slice.getPadding().getStop(), PythonReceiver::receiveRightPaddedTree));
            slice = slice.getPadding().withStep(ctx.receiveNode(slice.getPadding().getStep(), PythonReceiver::receiveRightPaddedTree));
            return slice;
        }

        @Override
        public J.AnnotatedType visitAnnotatedType(J.AnnotatedType annotatedType, ReceiverContext ctx) {
            annotatedType = annotatedType.withId(ctx.receiveNonNullValue(annotatedType.getId(), UUID.class));
            annotatedType = annotatedType.withPrefix(ctx.receiveNonNullNode(annotatedType.getPrefix(), PythonReceiver::receiveSpace));
            annotatedType = annotatedType.withMarkers(ctx.receiveNonNullNode(annotatedType.getMarkers(), ctx::receiveMarkers));
            annotatedType = annotatedType.withAnnotations(ctx.receiveNonNullNodes(annotatedType.getAnnotations(), ctx::receiveTree));
            annotatedType = annotatedType.withTypeExpression(ctx.receiveNonNullNode(annotatedType.getTypeExpression(), ctx::receiveTree));
            return annotatedType;
        }

        @Override
        public J.Annotation visitAnnotation(J.Annotation annotation, ReceiverContext ctx) {
            annotation = annotation.withId(ctx.receiveNonNullValue(annotation.getId(), UUID.class));
            annotation = annotation.withPrefix(ctx.receiveNonNullNode(annotation.getPrefix(), PythonReceiver::receiveSpace));
            annotation = annotation.withMarkers(ctx.receiveNonNullNode(annotation.getMarkers(), ctx::receiveMarkers));
            annotation = annotation.withAnnotationType(ctx.receiveNonNullNode(annotation.getAnnotationType(), ctx::receiveTree));
            annotation = annotation.getPadding().withArguments(ctx.receiveNode(annotation.getPadding().getArguments(), PythonReceiver::receiveContainer));
            return annotation;
        }

        @Override
        public J.ArrayAccess visitArrayAccess(J.ArrayAccess arrayAccess, ReceiverContext ctx) {
            arrayAccess = arrayAccess.withId(ctx.receiveNonNullValue(arrayAccess.getId(), UUID.class));
            arrayAccess = arrayAccess.withPrefix(ctx.receiveNonNullNode(arrayAccess.getPrefix(), PythonReceiver::receiveSpace));
            arrayAccess = arrayAccess.withMarkers(ctx.receiveNonNullNode(arrayAccess.getMarkers(), ctx::receiveMarkers));
            arrayAccess = arrayAccess.withIndexed(ctx.receiveNonNullNode(arrayAccess.getIndexed(), ctx::receiveTree));
            arrayAccess = arrayAccess.withDimension(ctx.receiveNonNullNode(arrayAccess.getDimension(), ctx::receiveTree));
            arrayAccess = arrayAccess.withType(ctx.receiveValue(arrayAccess.getType(), JavaType.class));
            return arrayAccess;
        }

        @Override
        public J.ArrayType visitArrayType(J.ArrayType arrayType, ReceiverContext ctx) {
            arrayType = arrayType.withId(ctx.receiveNonNullValue(arrayType.getId(), UUID.class));
            arrayType = arrayType.withPrefix(ctx.receiveNonNullNode(arrayType.getPrefix(), PythonReceiver::receiveSpace));
            arrayType = arrayType.withMarkers(ctx.receiveNonNullNode(arrayType.getMarkers(), ctx::receiveMarkers));
            arrayType = arrayType.withElementType(ctx.receiveNonNullNode(arrayType.getElementType(), ctx::receiveTree));
            arrayType = arrayType.withAnnotations(ctx.receiveNodes(arrayType.getAnnotations(), ctx::receiveTree));
            arrayType = arrayType.withDimension(ctx.receiveNode(arrayType.getDimension(), leftPaddedNodeReceiver(
		            Space.class)));
            arrayType = arrayType.withType(ctx.receiveValue(arrayType.getType(), JavaType.class));
            return arrayType;
        }

        @Override
        public J.Assert visitAssert(J.Assert assert_, ReceiverContext ctx) {
            assert_ = assert_.withId(ctx.receiveNonNullValue(assert_.getId(), UUID.class));
            assert_ = assert_.withPrefix(ctx.receiveNonNullNode(assert_.getPrefix(), PythonReceiver::receiveSpace));
            assert_ = assert_.withMarkers(ctx.receiveNonNullNode(assert_.getMarkers(), ctx::receiveMarkers));
            assert_ = assert_.withCondition(ctx.receiveNonNullNode(assert_.getCondition(), ctx::receiveTree));
            assert_ = assert_.withDetail(ctx.receiveNode(assert_.getDetail(), PythonReceiver::receiveLeftPaddedTree));
            return assert_;
        }

        @Override
        public J.Assignment visitAssignment(J.Assignment assignment, ReceiverContext ctx) {
            assignment = assignment.withId(ctx.receiveNonNullValue(assignment.getId(), UUID.class));
            assignment = assignment.withPrefix(ctx.receiveNonNullNode(assignment.getPrefix(), PythonReceiver::receiveSpace));
            assignment = assignment.withMarkers(ctx.receiveNonNullNode(assignment.getMarkers(), ctx::receiveMarkers));
            assignment = assignment.withVariable(ctx.receiveNonNullNode(assignment.getVariable(), ctx::receiveTree));
            assignment = assignment.getPadding().withAssignment(ctx.receiveNonNullNode(assignment.getPadding().getAssignment(), PythonReceiver::receiveLeftPaddedTree));
            assignment = assignment.withType(ctx.receiveValue(assignment.getType(), JavaType.class));
            return assignment;
        }

        @Override
        public J.AssignmentOperation visitAssignmentOperation(J.AssignmentOperation assignmentOperation, ReceiverContext ctx) {
            assignmentOperation = assignmentOperation.withId(ctx.receiveNonNullValue(assignmentOperation.getId(), UUID.class));
            assignmentOperation = assignmentOperation.withPrefix(ctx.receiveNonNullNode(assignmentOperation.getPrefix(), PythonReceiver::receiveSpace));
            assignmentOperation = assignmentOperation.withMarkers(ctx.receiveNonNullNode(assignmentOperation.getMarkers(), ctx::receiveMarkers));
            assignmentOperation = assignmentOperation.withVariable(ctx.receiveNonNullNode(assignmentOperation.getVariable(), ctx::receiveTree));
            assignmentOperation = assignmentOperation.getPadding().withOperator(ctx.receiveNonNullNode(assignmentOperation.getPadding().getOperator(), leftPaddedValueReceiver(
		            J.AssignmentOperation.Type.class)));
            assignmentOperation = assignmentOperation.withAssignment(ctx.receiveNonNullNode(assignmentOperation.getAssignment(), ctx::receiveTree));
            assignmentOperation = assignmentOperation.withType(ctx.receiveValue(assignmentOperation.getType(), JavaType.class));
            return assignmentOperation;
        }

        @Override
        public J.Binary visitBinary(J.Binary binary, ReceiverContext ctx) {
            binary = binary.withId(ctx.receiveNonNullValue(binary.getId(), UUID.class));
            binary = binary.withPrefix(ctx.receiveNonNullNode(binary.getPrefix(), PythonReceiver::receiveSpace));
            binary = binary.withMarkers(ctx.receiveNonNullNode(binary.getMarkers(), ctx::receiveMarkers));
            binary = binary.withLeft(ctx.receiveNonNullNode(binary.getLeft(), ctx::receiveTree));
            binary = binary.getPadding().withOperator(ctx.receiveNonNullNode(binary.getPadding().getOperator(), leftPaddedValueReceiver(
		            J.Binary.Type.class)));
            binary = binary.withRight(ctx.receiveNonNullNode(binary.getRight(), ctx::receiveTree));
            binary = binary.withType(ctx.receiveValue(binary.getType(), JavaType.class));
            return binary;
        }

        @Override
        public J.Block visitBlock(J.Block block, ReceiverContext ctx) {
            block = block.withId(ctx.receiveNonNullValue(block.getId(), UUID.class));
            block = block.withPrefix(ctx.receiveNonNullNode(block.getPrefix(), PythonReceiver::receiveSpace));
            block = block.withMarkers(ctx.receiveNonNullNode(block.getMarkers(), ctx::receiveMarkers));
            block = block.getPadding().withStatic(ctx.receiveNonNullNode(block.getPadding().getStatic(), rightPaddedValueReceiver(
		            Boolean.class)));
            block = block.getPadding().withStatements(ctx.receiveNonNullNodes(block.getPadding().getStatements(), PythonReceiver::receiveRightPaddedTree));
            block = block.withEnd(ctx.receiveNonNullNode(block.getEnd(), PythonReceiver::receiveSpace));
            return block;
        }

        @Override
        public J.Break visitBreak(J.Break break_, ReceiverContext ctx) {
            break_ = break_.withId(ctx.receiveNonNullValue(break_.getId(), UUID.class));
            break_ = break_.withPrefix(ctx.receiveNonNullNode(break_.getPrefix(), PythonReceiver::receiveSpace));
            break_ = break_.withMarkers(ctx.receiveNonNullNode(break_.getMarkers(), ctx::receiveMarkers));
            break_ = break_.withLabel(ctx.receiveNode(break_.getLabel(), ctx::receiveTree));
            return break_;
        }

        @Override
        public J.Case visitCase(J.Case case_, ReceiverContext ctx) {
            case_ = case_.withId(ctx.receiveNonNullValue(case_.getId(), UUID.class));
            case_ = case_.withPrefix(ctx.receiveNonNullNode(case_.getPrefix(), PythonReceiver::receiveSpace));
            case_ = case_.withMarkers(ctx.receiveNonNullNode(case_.getMarkers(), ctx::receiveMarkers));
            case_ = case_.withType(ctx.receiveNonNullValue(case_.getType(), J.Case.Type.class));
            case_ = case_.getPadding().withExpressions(ctx.receiveNonNullNode(case_.getPadding().getExpressions(), PythonReceiver::receiveContainer));
            case_ = case_.getPadding().withStatements(ctx.receiveNonNullNode(case_.getPadding().getStatements(), PythonReceiver::receiveContainer));
            case_ = case_.getPadding().withBody(ctx.receiveNode(case_.getPadding().getBody(), PythonReceiver::receiveRightPaddedTree));
            return case_;
        }

        @Override
        public J.ClassDeclaration visitClassDeclaration(J.ClassDeclaration classDeclaration, ReceiverContext ctx) {
            classDeclaration = classDeclaration.withId(ctx.receiveNonNullValue(classDeclaration.getId(), UUID.class));
            classDeclaration = classDeclaration.withPrefix(ctx.receiveNonNullNode(classDeclaration.getPrefix(), PythonReceiver::receiveSpace));
            classDeclaration = classDeclaration.withMarkers(ctx.receiveNonNullNode(classDeclaration.getMarkers(), ctx::receiveMarkers));
            classDeclaration = classDeclaration.withLeadingAnnotations(ctx.receiveNonNullNodes(classDeclaration.getLeadingAnnotations(), ctx::receiveTree));
            classDeclaration = classDeclaration.withModifiers(ctx.receiveNonNullNodes(classDeclaration.getModifiers(), PythonReceiver::receiveModifier));
            classDeclaration = classDeclaration.getPadding().withKind(ctx.receiveNonNullNode(classDeclaration.getPadding().getKind(), PythonReceiver::receiveClassDeclarationKind));
            classDeclaration = classDeclaration.withName(ctx.receiveNonNullNode(classDeclaration.getName(), ctx::receiveTree));
            classDeclaration = classDeclaration.getPadding().withTypeParameters(ctx.receiveNode(classDeclaration.getPadding().getTypeParameters(), PythonReceiver::receiveContainer));
            classDeclaration = classDeclaration.getPadding().withPrimaryConstructor(ctx.receiveNode(classDeclaration.getPadding().getPrimaryConstructor(), PythonReceiver::receiveContainer));
            classDeclaration = classDeclaration.getPadding().withExtends(ctx.receiveNode(classDeclaration.getPadding().getExtends(), PythonReceiver::receiveLeftPaddedTree));
            classDeclaration = classDeclaration.getPadding().withImplements(ctx.receiveNode(classDeclaration.getPadding().getImplements(), PythonReceiver::receiveContainer));
            classDeclaration = classDeclaration.getPadding().withPermits(ctx.receiveNode(classDeclaration.getPadding().getPermits(), PythonReceiver::receiveContainer));
            classDeclaration = classDeclaration.withBody(ctx.receiveNonNullNode(classDeclaration.getBody(), ctx::receiveTree));
            classDeclaration = classDeclaration.withType(ctx.receiveValue(classDeclaration.getType(), JavaType.FullyQualified.class));
            return classDeclaration;
        }

        @Override
        public J.Continue visitContinue(J.Continue continue_, ReceiverContext ctx) {
            continue_ = continue_.withId(ctx.receiveNonNullValue(continue_.getId(), UUID.class));
            continue_ = continue_.withPrefix(ctx.receiveNonNullNode(continue_.getPrefix(), PythonReceiver::receiveSpace));
            continue_ = continue_.withMarkers(ctx.receiveNonNullNode(continue_.getMarkers(), ctx::receiveMarkers));
            continue_ = continue_.withLabel(ctx.receiveNode(continue_.getLabel(), ctx::receiveTree));
            return continue_;
        }

        @Override
        public J.DoWhileLoop visitDoWhileLoop(J.DoWhileLoop doWhileLoop, ReceiverContext ctx) {
            doWhileLoop = doWhileLoop.withId(ctx.receiveNonNullValue(doWhileLoop.getId(), UUID.class));
            doWhileLoop = doWhileLoop.withPrefix(ctx.receiveNonNullNode(doWhileLoop.getPrefix(), PythonReceiver::receiveSpace));
            doWhileLoop = doWhileLoop.withMarkers(ctx.receiveNonNullNode(doWhileLoop.getMarkers(), ctx::receiveMarkers));
            doWhileLoop = doWhileLoop.getPadding().withBody(ctx.receiveNonNullNode(doWhileLoop.getPadding().getBody(), PythonReceiver::receiveRightPaddedTree));
            doWhileLoop = doWhileLoop.getPadding().withWhileCondition(ctx.receiveNonNullNode(doWhileLoop.getPadding().getWhileCondition(), PythonReceiver::receiveLeftPaddedTree));
            return doWhileLoop;
        }

        @Override
        public J.Empty visitEmpty(J.Empty empty, ReceiverContext ctx) {
            empty = empty.withId(ctx.receiveNonNullValue(empty.getId(), UUID.class));
            empty = empty.withPrefix(ctx.receiveNonNullNode(empty.getPrefix(), PythonReceiver::receiveSpace));
            empty = empty.withMarkers(ctx.receiveNonNullNode(empty.getMarkers(), ctx::receiveMarkers));
            return empty;
        }

        @Override
        public J.EnumValue visitEnumValue(J.EnumValue enumValue, ReceiverContext ctx) {
            enumValue = enumValue.withId(ctx.receiveNonNullValue(enumValue.getId(), UUID.class));
            enumValue = enumValue.withPrefix(ctx.receiveNonNullNode(enumValue.getPrefix(), PythonReceiver::receiveSpace));
            enumValue = enumValue.withMarkers(ctx.receiveNonNullNode(enumValue.getMarkers(), ctx::receiveMarkers));
            enumValue = enumValue.withAnnotations(ctx.receiveNonNullNodes(enumValue.getAnnotations(), ctx::receiveTree));
            enumValue = enumValue.withName(ctx.receiveNonNullNode(enumValue.getName(), ctx::receiveTree));
            enumValue = enumValue.withInitializer(ctx.receiveNode(enumValue.getInitializer(), ctx::receiveTree));
            return enumValue;
        }

        @Override
        public J.EnumValueSet visitEnumValueSet(J.EnumValueSet enumValueSet, ReceiverContext ctx) {
            enumValueSet = enumValueSet.withId(ctx.receiveNonNullValue(enumValueSet.getId(), UUID.class));
            enumValueSet = enumValueSet.withPrefix(ctx.receiveNonNullNode(enumValueSet.getPrefix(), PythonReceiver::receiveSpace));
            enumValueSet = enumValueSet.withMarkers(ctx.receiveNonNullNode(enumValueSet.getMarkers(), ctx::receiveMarkers));
            enumValueSet = enumValueSet.getPadding().withEnums(ctx.receiveNonNullNodes(enumValueSet.getPadding().getEnums(), PythonReceiver::receiveRightPaddedTree));
            enumValueSet = enumValueSet.withTerminatedWithSemicolon(ctx.receiveNonNullValue(enumValueSet.isTerminatedWithSemicolon(), boolean.class));
            return enumValueSet;
        }

        @Override
        public J.FieldAccess visitFieldAccess(J.FieldAccess fieldAccess, ReceiverContext ctx) {
            fieldAccess = fieldAccess.withId(ctx.receiveNonNullValue(fieldAccess.getId(), UUID.class));
            fieldAccess = fieldAccess.withPrefix(ctx.receiveNonNullNode(fieldAccess.getPrefix(), PythonReceiver::receiveSpace));
            fieldAccess = fieldAccess.withMarkers(ctx.receiveNonNullNode(fieldAccess.getMarkers(), ctx::receiveMarkers));
            fieldAccess = fieldAccess.withTarget(ctx.receiveNonNullNode(fieldAccess.getTarget(), ctx::receiveTree));
            fieldAccess = fieldAccess.getPadding().withName(ctx.receiveNonNullNode(fieldAccess.getPadding().getName(), PythonReceiver::receiveLeftPaddedTree));
            fieldAccess = fieldAccess.withType(ctx.receiveValue(fieldAccess.getType(), JavaType.class));
            return fieldAccess;
        }

        @Override
        public J.ForEachLoop visitForEachLoop(J.ForEachLoop forEachLoop, ReceiverContext ctx) {
            forEachLoop = forEachLoop.withId(ctx.receiveNonNullValue(forEachLoop.getId(), UUID.class));
            forEachLoop = forEachLoop.withPrefix(ctx.receiveNonNullNode(forEachLoop.getPrefix(), PythonReceiver::receiveSpace));
            forEachLoop = forEachLoop.withMarkers(ctx.receiveNonNullNode(forEachLoop.getMarkers(), ctx::receiveMarkers));
            forEachLoop = forEachLoop.withControl(ctx.receiveNonNullNode(forEachLoop.getControl(), ctx::receiveTree));
            forEachLoop = forEachLoop.getPadding().withBody(ctx.receiveNonNullNode(forEachLoop.getPadding().getBody(), PythonReceiver::receiveRightPaddedTree));
            return forEachLoop;
        }

        @Override
        public J.ForEachLoop.Control visitForEachControl(J.ForEachLoop.Control control, ReceiverContext ctx) {
            control = control.withId(ctx.receiveNonNullValue(control.getId(), UUID.class));
            control = control.withPrefix(ctx.receiveNonNullNode(control.getPrefix(), PythonReceiver::receiveSpace));
            control = control.withMarkers(ctx.receiveNonNullNode(control.getMarkers(), ctx::receiveMarkers));
            control = control.getPadding().withVariable(ctx.receiveNonNullNode(control.getPadding().getVariable(), PythonReceiver::receiveRightPaddedTree));
            control = control.getPadding().withIterable(ctx.receiveNonNullNode(control.getPadding().getIterable(), PythonReceiver::receiveRightPaddedTree));
            return control;
        }

        @Override
        public J.ForLoop visitForLoop(J.ForLoop forLoop, ReceiverContext ctx) {
            forLoop = forLoop.withId(ctx.receiveNonNullValue(forLoop.getId(), UUID.class));
            forLoop = forLoop.withPrefix(ctx.receiveNonNullNode(forLoop.getPrefix(), PythonReceiver::receiveSpace));
            forLoop = forLoop.withMarkers(ctx.receiveNonNullNode(forLoop.getMarkers(), ctx::receiveMarkers));
            forLoop = forLoop.withControl(ctx.receiveNonNullNode(forLoop.getControl(), ctx::receiveTree));
            forLoop = forLoop.getPadding().withBody(ctx.receiveNonNullNode(forLoop.getPadding().getBody(), PythonReceiver::receiveRightPaddedTree));
            return forLoop;
        }

        @Override
        public J.ForLoop.Control visitForControl(J.ForLoop.Control control, ReceiverContext ctx) {
            control = control.withId(ctx.receiveNonNullValue(control.getId(), UUID.class));
            control = control.withPrefix(ctx.receiveNonNullNode(control.getPrefix(), PythonReceiver::receiveSpace));
            control = control.withMarkers(ctx.receiveNonNullNode(control.getMarkers(), ctx::receiveMarkers));
            control = control.getPadding().withInit(ctx.receiveNonNullNodes(control.getPadding().getInit(), PythonReceiver::receiveRightPaddedTree));
            control = control.getPadding().withCondition(ctx.receiveNonNullNode(control.getPadding().getCondition(), PythonReceiver::receiveRightPaddedTree));
            control = control.getPadding().withUpdate(ctx.receiveNonNullNodes(control.getPadding().getUpdate(), PythonReceiver::receiveRightPaddedTree));
            return control;
        }

        @Override
        public J.ParenthesizedTypeTree visitParenthesizedTypeTree(J.ParenthesizedTypeTree parenthesizedTypeTree, ReceiverContext ctx) {
            parenthesizedTypeTree = parenthesizedTypeTree.withId(ctx.receiveNonNullValue(parenthesizedTypeTree.getId(), UUID.class));
            parenthesizedTypeTree = parenthesizedTypeTree.withPrefix(ctx.receiveNonNullNode(parenthesizedTypeTree.getPrefix(), PythonReceiver::receiveSpace));
            parenthesizedTypeTree = parenthesizedTypeTree.withMarkers(ctx.receiveNonNullNode(parenthesizedTypeTree.getMarkers(), ctx::receiveMarkers));
            parenthesizedTypeTree = parenthesizedTypeTree.withAnnotations(ctx.receiveNonNullNodes(parenthesizedTypeTree.getAnnotations(), ctx::receiveTree));
            parenthesizedTypeTree = parenthesizedTypeTree.withParenthesizedType(ctx.receiveNonNullNode(parenthesizedTypeTree.getParenthesizedType(), ctx::receiveTree));
            return parenthesizedTypeTree;
        }

        @Override
        public J.Identifier visitIdentifier(J.Identifier identifier, ReceiverContext ctx) {
            identifier = identifier.withId(ctx.receiveNonNullValue(identifier.getId(), UUID.class));
            identifier = identifier.withPrefix(ctx.receiveNonNullNode(identifier.getPrefix(), PythonReceiver::receiveSpace));
            identifier = identifier.withMarkers(ctx.receiveNonNullNode(identifier.getMarkers(), ctx::receiveMarkers));
            identifier = identifier.withAnnotations(ctx.receiveNonNullNodes(identifier.getAnnotations(), ctx::receiveTree));
            identifier = identifier.withSimpleName(ctx.receiveNonNullValue(identifier.getSimpleName(), String.class));
            identifier = identifier.withType(ctx.receiveValue(identifier.getType(), JavaType.class));
            identifier = identifier.withFieldType(ctx.receiveValue(identifier.getFieldType(), JavaType.Variable.class));
            return identifier;
        }

        @Override
        public J.If visitIf(J.If if_, ReceiverContext ctx) {
            if_ = if_.withId(ctx.receiveNonNullValue(if_.getId(), UUID.class));
            if_ = if_.withPrefix(ctx.receiveNonNullNode(if_.getPrefix(), PythonReceiver::receiveSpace));
            if_ = if_.withMarkers(ctx.receiveNonNullNode(if_.getMarkers(), ctx::receiveMarkers));
            if_ = if_.withIfCondition(ctx.receiveNonNullNode(if_.getIfCondition(), ctx::receiveTree));
            if_ = if_.getPadding().withThenPart(ctx.receiveNonNullNode(if_.getPadding().getThenPart(), PythonReceiver::receiveRightPaddedTree));
            if_ = if_.withElsePart(ctx.receiveNode(if_.getElsePart(), ctx::receiveTree));
            return if_;
        }

        @Override
        public J.If.Else visitElse(J.If.Else else_, ReceiverContext ctx) {
            else_ = else_.withId(ctx.receiveNonNullValue(else_.getId(), UUID.class));
            else_ = else_.withPrefix(ctx.receiveNonNullNode(else_.getPrefix(), PythonReceiver::receiveSpace));
            else_ = else_.withMarkers(ctx.receiveNonNullNode(else_.getMarkers(), ctx::receiveMarkers));
            else_ = else_.getPadding().withBody(ctx.receiveNonNullNode(else_.getPadding().getBody(), PythonReceiver::receiveRightPaddedTree));
            return else_;
        }

        @Override
        public J.Import visitImport(J.Import import_, ReceiverContext ctx) {
            import_ = import_.withId(ctx.receiveNonNullValue(import_.getId(), UUID.class));
            import_ = import_.withPrefix(ctx.receiveNonNullNode(import_.getPrefix(), PythonReceiver::receiveSpace));
            import_ = import_.withMarkers(ctx.receiveNonNullNode(import_.getMarkers(), ctx::receiveMarkers));
            import_ = import_.getPadding().withStatic(ctx.receiveNonNullNode(import_.getPadding().getStatic(), leftPaddedValueReceiver(
		            Boolean.class)));
            import_ = import_.withQualid(ctx.receiveNonNullNode(import_.getQualid(), ctx::receiveTree));
            import_ = import_.getPadding().withAlias(ctx.receiveNode(import_.getPadding().getAlias(), PythonReceiver::receiveLeftPaddedTree));
            return import_;
        }

        @Override
        public J.InstanceOf visitInstanceOf(J.InstanceOf instanceOf, ReceiverContext ctx) {
            instanceOf = instanceOf.withId(ctx.receiveNonNullValue(instanceOf.getId(), UUID.class));
            instanceOf = instanceOf.withPrefix(ctx.receiveNonNullNode(instanceOf.getPrefix(), PythonReceiver::receiveSpace));
            instanceOf = instanceOf.withMarkers(ctx.receiveNonNullNode(instanceOf.getMarkers(), ctx::receiveMarkers));
            instanceOf = instanceOf.getPadding().withExpression(ctx.receiveNonNullNode(instanceOf.getPadding().getExpression(), PythonReceiver::receiveRightPaddedTree));
            instanceOf = instanceOf.withClazz(ctx.receiveNonNullNode(instanceOf.getClazz(), ctx::receiveTree));
            instanceOf = instanceOf.withPattern(ctx.receiveNode(instanceOf.getPattern(), ctx::receiveTree));
            instanceOf = instanceOf.withType(ctx.receiveValue(instanceOf.getType(), JavaType.class));
            return instanceOf;
        }

        @Override
        public J.IntersectionType visitIntersectionType(J.IntersectionType intersectionType, ReceiverContext ctx) {
            intersectionType = intersectionType.withId(ctx.receiveNonNullValue(intersectionType.getId(), UUID.class));
            intersectionType = intersectionType.withPrefix(ctx.receiveNonNullNode(intersectionType.getPrefix(), PythonReceiver::receiveSpace));
            intersectionType = intersectionType.withMarkers(ctx.receiveNonNullNode(intersectionType.getMarkers(), ctx::receiveMarkers));
            intersectionType = intersectionType.getPadding().withBounds(ctx.receiveNonNullNode(intersectionType.getPadding().getBounds(), PythonReceiver::receiveContainer));
            return intersectionType;
        }

        @Override
        public J.Label visitLabel(J.Label label, ReceiverContext ctx) {
            label = label.withId(ctx.receiveNonNullValue(label.getId(), UUID.class));
            label = label.withPrefix(ctx.receiveNonNullNode(label.getPrefix(), PythonReceiver::receiveSpace));
            label = label.withMarkers(ctx.receiveNonNullNode(label.getMarkers(), ctx::receiveMarkers));
            label = label.getPadding().withLabel(ctx.receiveNonNullNode(label.getPadding().getLabel(), PythonReceiver::receiveRightPaddedTree));
            label = label.withStatement(ctx.receiveNonNullNode(label.getStatement(), ctx::receiveTree));
            return label;
        }

        @Override
        public J.Lambda visitLambda(J.Lambda lambda, ReceiverContext ctx) {
            lambda = lambda.withId(ctx.receiveNonNullValue(lambda.getId(), UUID.class));
            lambda = lambda.withPrefix(ctx.receiveNonNullNode(lambda.getPrefix(), PythonReceiver::receiveSpace));
            lambda = lambda.withMarkers(ctx.receiveNonNullNode(lambda.getMarkers(), ctx::receiveMarkers));
            lambda = lambda.withParameters(ctx.receiveNonNullNode(lambda.getParameters(), PythonReceiver::receiveLambdaParameters));
            lambda = lambda.withArrow(ctx.receiveNonNullNode(lambda.getArrow(), PythonReceiver::receiveSpace));
            lambda = lambda.withBody(ctx.receiveNonNullNode(lambda.getBody(), ctx::receiveTree));
            lambda = lambda.withType(ctx.receiveValue(lambda.getType(), JavaType.class));
            return lambda;
        }

        @Override
        public J.Literal visitLiteral(J.Literal literal, ReceiverContext ctx) {
            literal = literal.withId(ctx.receiveNonNullValue(literal.getId(), UUID.class));
            literal = literal.withPrefix(ctx.receiveNonNullNode(literal.getPrefix(), PythonReceiver::receiveSpace));
            literal = literal.withMarkers(ctx.receiveNonNullNode(literal.getMarkers(), ctx::receiveMarkers));
            literal = literal.withValue(ctx.receiveValue(literal.getValue(), Object.class));
            literal = literal.withValueSource(ctx.receiveValue(literal.getValueSource(), String.class));
            literal = literal.withUnicodeEscapes(ctx.receiveValues(literal.getUnicodeEscapes(), J.Literal.UnicodeEscape.class));
            literal = literal.withType(ctx.receiveValue(literal.getType(), JavaType.Primitive.class));
            return literal;
        }

        @Override
        public J.MemberReference visitMemberReference(J.MemberReference memberReference, ReceiverContext ctx) {
            memberReference = memberReference.withId(ctx.receiveNonNullValue(memberReference.getId(), UUID.class));
            memberReference = memberReference.withPrefix(ctx.receiveNonNullNode(memberReference.getPrefix(), PythonReceiver::receiveSpace));
            memberReference = memberReference.withMarkers(ctx.receiveNonNullNode(memberReference.getMarkers(), ctx::receiveMarkers));
            memberReference = memberReference.getPadding().withContaining(ctx.receiveNonNullNode(memberReference.getPadding().getContaining(), PythonReceiver::receiveRightPaddedTree));
            memberReference = memberReference.getPadding().withTypeParameters(ctx.receiveNode(memberReference.getPadding().getTypeParameters(), PythonReceiver::receiveContainer));
            memberReference = memberReference.getPadding().withReference(ctx.receiveNonNullNode(memberReference.getPadding().getReference(), PythonReceiver::receiveLeftPaddedTree));
            memberReference = memberReference.withType(ctx.receiveValue(memberReference.getType(), JavaType.class));
            memberReference = memberReference.withMethodType(ctx.receiveValue(memberReference.getMethodType(), JavaType.Method.class));
            memberReference = memberReference.withVariableType(ctx.receiveValue(memberReference.getVariableType(), JavaType.Variable.class));
            return memberReference;
        }

        @Override
        public J.MethodDeclaration visitMethodDeclaration(J.MethodDeclaration methodDeclaration, ReceiverContext ctx) {
            methodDeclaration = methodDeclaration.withId(ctx.receiveNonNullValue(methodDeclaration.getId(), UUID.class));
            methodDeclaration = methodDeclaration.withPrefix(ctx.receiveNonNullNode(methodDeclaration.getPrefix(), PythonReceiver::receiveSpace));
            methodDeclaration = methodDeclaration.withMarkers(ctx.receiveNonNullNode(methodDeclaration.getMarkers(), ctx::receiveMarkers));
            methodDeclaration = methodDeclaration.withLeadingAnnotations(ctx.receiveNonNullNodes(methodDeclaration.getLeadingAnnotations(), ctx::receiveTree));
            methodDeclaration = methodDeclaration.withModifiers(ctx.receiveNonNullNodes(methodDeclaration.getModifiers(), PythonReceiver::receiveModifier));
            methodDeclaration = methodDeclaration.getAnnotations().withTypeParameters(ctx.receiveNode(methodDeclaration.getAnnotations().getTypeParameters(), PythonReceiver::receiveMethodTypeParameters));
            methodDeclaration = methodDeclaration.withReturnTypeExpression(ctx.receiveNode(methodDeclaration.getReturnTypeExpression(), ctx::receiveTree));
            methodDeclaration = methodDeclaration.getAnnotations().withName(ctx.receiveNonNullNode(methodDeclaration.getAnnotations().getName(), PythonReceiver::receiveMethodIdentifierWithAnnotations));
            methodDeclaration = methodDeclaration.getPadding().withParameters(ctx.receiveNonNullNode(methodDeclaration.getPadding().getParameters(), PythonReceiver::receiveContainer));
            methodDeclaration = methodDeclaration.getPadding().withThrows(ctx.receiveNode(methodDeclaration.getPadding().getThrows(), PythonReceiver::receiveContainer));
            methodDeclaration = methodDeclaration.withBody(ctx.receiveNode(methodDeclaration.getBody(), ctx::receiveTree));
            methodDeclaration = methodDeclaration.getPadding().withDefaultValue(ctx.receiveNode(methodDeclaration.getPadding().getDefaultValue(), PythonReceiver::receiveLeftPaddedTree));
            methodDeclaration = methodDeclaration.withMethodType(ctx.receiveValue(methodDeclaration.getMethodType(), JavaType.Method.class));
            return methodDeclaration;
        }

        @Override
        public J.MethodInvocation visitMethodInvocation(J.MethodInvocation methodInvocation, ReceiverContext ctx) {
            methodInvocation = methodInvocation.withId(ctx.receiveNonNullValue(methodInvocation.getId(), UUID.class));
            methodInvocation = methodInvocation.withPrefix(ctx.receiveNonNullNode(methodInvocation.getPrefix(), PythonReceiver::receiveSpace));
            methodInvocation = methodInvocation.withMarkers(ctx.receiveNonNullNode(methodInvocation.getMarkers(), ctx::receiveMarkers));
            methodInvocation = methodInvocation.getPadding().withSelect(ctx.receiveNode(methodInvocation.getPadding().getSelect(), PythonReceiver::receiveRightPaddedTree));
            methodInvocation = methodInvocation.getPadding().withTypeParameters(ctx.receiveNode(methodInvocation.getPadding().getTypeParameters(), PythonReceiver::receiveContainer));
            methodInvocation = methodInvocation.withName(ctx.receiveNonNullNode(methodInvocation.getName(), ctx::receiveTree));
            methodInvocation = methodInvocation.getPadding().withArguments(ctx.receiveNonNullNode(methodInvocation.getPadding().getArguments(), PythonReceiver::receiveContainer));
            methodInvocation = methodInvocation.withMethodType(ctx.receiveValue(methodInvocation.getMethodType(), JavaType.Method.class));
            return methodInvocation;
        }

        @Override
        public J.MultiCatch visitMultiCatch(J.MultiCatch multiCatch, ReceiverContext ctx) {
            multiCatch = multiCatch.withId(ctx.receiveNonNullValue(multiCatch.getId(), UUID.class));
            multiCatch = multiCatch.withPrefix(ctx.receiveNonNullNode(multiCatch.getPrefix(), PythonReceiver::receiveSpace));
            multiCatch = multiCatch.withMarkers(ctx.receiveNonNullNode(multiCatch.getMarkers(), ctx::receiveMarkers));
            multiCatch = multiCatch.getPadding().withAlternatives(ctx.receiveNonNullNodes(multiCatch.getPadding().getAlternatives(), PythonReceiver::receiveRightPaddedTree));
            return multiCatch;
        }

        @Override
        public J.NewArray visitNewArray(J.NewArray newArray, ReceiverContext ctx) {
            newArray = newArray.withId(ctx.receiveNonNullValue(newArray.getId(), UUID.class));
            newArray = newArray.withPrefix(ctx.receiveNonNullNode(newArray.getPrefix(), PythonReceiver::receiveSpace));
            newArray = newArray.withMarkers(ctx.receiveNonNullNode(newArray.getMarkers(), ctx::receiveMarkers));
            newArray = newArray.withTypeExpression(ctx.receiveNode(newArray.getTypeExpression(), ctx::receiveTree));
            newArray = newArray.withDimensions(ctx.receiveNonNullNodes(newArray.getDimensions(), ctx::receiveTree));
            newArray = newArray.getPadding().withInitializer(ctx.receiveNode(newArray.getPadding().getInitializer(), PythonReceiver::receiveContainer));
            newArray = newArray.withType(ctx.receiveValue(newArray.getType(), JavaType.class));
            return newArray;
        }

        @Override
        public J.ArrayDimension visitArrayDimension(J.ArrayDimension arrayDimension, ReceiverContext ctx) {
            arrayDimension = arrayDimension.withId(ctx.receiveNonNullValue(arrayDimension.getId(), UUID.class));
            arrayDimension = arrayDimension.withPrefix(ctx.receiveNonNullNode(arrayDimension.getPrefix(), PythonReceiver::receiveSpace));
            arrayDimension = arrayDimension.withMarkers(ctx.receiveNonNullNode(arrayDimension.getMarkers(), ctx::receiveMarkers));
            arrayDimension = arrayDimension.getPadding().withIndex(ctx.receiveNonNullNode(arrayDimension.getPadding().getIndex(), PythonReceiver::receiveRightPaddedTree));
            return arrayDimension;
        }

        @Override
        public J.NewClass visitNewClass(J.NewClass newClass, ReceiverContext ctx) {
            newClass = newClass.withId(ctx.receiveNonNullValue(newClass.getId(), UUID.class));
            newClass = newClass.withPrefix(ctx.receiveNonNullNode(newClass.getPrefix(), PythonReceiver::receiveSpace));
            newClass = newClass.withMarkers(ctx.receiveNonNullNode(newClass.getMarkers(), ctx::receiveMarkers));
            newClass = newClass.getPadding().withEnclosing(ctx.receiveNode(newClass.getPadding().getEnclosing(), PythonReceiver::receiveRightPaddedTree));
            newClass = newClass.withNew(ctx.receiveNonNullNode(newClass.getNew(), PythonReceiver::receiveSpace));
            newClass = newClass.withClazz(ctx.receiveNode(newClass.getClazz(), ctx::receiveTree));
            newClass = newClass.getPadding().withArguments(ctx.receiveNonNullNode(newClass.getPadding().getArguments(), PythonReceiver::receiveContainer));
            newClass = newClass.withBody(ctx.receiveNode(newClass.getBody(), ctx::receiveTree));
            newClass = newClass.withConstructorType(ctx.receiveValue(newClass.getConstructorType(), JavaType.Method.class));
            return newClass;
        }

        @Override
        public J.NullableType visitNullableType(J.NullableType nullableType, ReceiverContext ctx) {
            nullableType = nullableType.withId(ctx.receiveNonNullValue(nullableType.getId(), UUID.class));
            nullableType = nullableType.withPrefix(ctx.receiveNonNullNode(nullableType.getPrefix(), PythonReceiver::receiveSpace));
            nullableType = nullableType.withMarkers(ctx.receiveNonNullNode(nullableType.getMarkers(), ctx::receiveMarkers));
            nullableType = nullableType.withAnnotations(ctx.receiveNonNullNodes(nullableType.getAnnotations(), ctx::receiveTree));
            nullableType = nullableType.getPadding().withTypeTree(ctx.receiveNonNullNode(nullableType.getPadding().getTypeTree(), PythonReceiver::receiveRightPaddedTree));
            return nullableType;
        }

        @Override
        public J.Package visitPackage(J.Package package_, ReceiverContext ctx) {
            package_ = package_.withId(ctx.receiveNonNullValue(package_.getId(), UUID.class));
            package_ = package_.withPrefix(ctx.receiveNonNullNode(package_.getPrefix(), PythonReceiver::receiveSpace));
            package_ = package_.withMarkers(ctx.receiveNonNullNode(package_.getMarkers(), ctx::receiveMarkers));
            package_ = package_.withExpression(ctx.receiveNonNullNode(package_.getExpression(), ctx::receiveTree));
            package_ = package_.withAnnotations(ctx.receiveNonNullNodes(package_.getAnnotations(), ctx::receiveTree));
            return package_;
        }

        @Override
        public J.ParameterizedType visitParameterizedType(J.ParameterizedType parameterizedType, ReceiverContext ctx) {
            parameterizedType = parameterizedType.withId(ctx.receiveNonNullValue(parameterizedType.getId(), UUID.class));
            parameterizedType = parameterizedType.withPrefix(ctx.receiveNonNullNode(parameterizedType.getPrefix(), PythonReceiver::receiveSpace));
            parameterizedType = parameterizedType.withMarkers(ctx.receiveNonNullNode(parameterizedType.getMarkers(), ctx::receiveMarkers));
            parameterizedType = parameterizedType.withClazz(ctx.receiveNonNullNode(parameterizedType.getClazz(), ctx::receiveTree));
            parameterizedType = parameterizedType.getPadding().withTypeParameters(ctx.receiveNode(parameterizedType.getPadding().getTypeParameters(), PythonReceiver::receiveContainer));
            parameterizedType = parameterizedType.withType(ctx.receiveValue(parameterizedType.getType(), JavaType.class));
            return parameterizedType;
        }

        @Override
        public <J2 extends J> J.Parentheses<J2> visitParentheses(J.Parentheses<J2> parentheses, ReceiverContext ctx) {
            parentheses = parentheses.withId(ctx.receiveNonNullValue(parentheses.getId(), UUID.class));
            parentheses = parentheses.withPrefix(ctx.receiveNonNullNode(parentheses.getPrefix(), PythonReceiver::receiveSpace));
            parentheses = parentheses.withMarkers(ctx.receiveNonNullNode(parentheses.getMarkers(), ctx::receiveMarkers));
            parentheses = parentheses.getPadding().withTree(ctx.receiveNonNullNode(parentheses.getPadding().getTree(), PythonReceiver::receiveRightPaddedTree));
            return parentheses;
        }

        @Override
        public <J2 extends J> J.ControlParentheses<J2> visitControlParentheses(J.ControlParentheses<J2> controlParentheses, ReceiverContext ctx) {
            controlParentheses = controlParentheses.withId(ctx.receiveNonNullValue(controlParentheses.getId(), UUID.class));
            controlParentheses = controlParentheses.withPrefix(ctx.receiveNonNullNode(controlParentheses.getPrefix(), PythonReceiver::receiveSpace));
            controlParentheses = controlParentheses.withMarkers(ctx.receiveNonNullNode(controlParentheses.getMarkers(), ctx::receiveMarkers));
            controlParentheses = controlParentheses.getPadding().withTree(ctx.receiveNonNullNode(controlParentheses.getPadding().getTree(), PythonReceiver::receiveRightPaddedTree));
            return controlParentheses;
        }

        @Override
        public J.Primitive visitPrimitive(J.Primitive primitive, ReceiverContext ctx) {
            primitive = primitive.withId(ctx.receiveNonNullValue(primitive.getId(), UUID.class));
            primitive = primitive.withPrefix(ctx.receiveNonNullNode(primitive.getPrefix(), PythonReceiver::receiveSpace));
            primitive = primitive.withMarkers(ctx.receiveNonNullNode(primitive.getMarkers(), ctx::receiveMarkers));
            primitive = primitive.withType(ctx.receiveValue(primitive.getType(), JavaType.Primitive.class));
            return primitive;
        }

        @Override
        public J.Return visitReturn(J.Return return_, ReceiverContext ctx) {
            return_ = return_.withId(ctx.receiveNonNullValue(return_.getId(), UUID.class));
            return_ = return_.withPrefix(ctx.receiveNonNullNode(return_.getPrefix(), PythonReceiver::receiveSpace));
            return_ = return_.withMarkers(ctx.receiveNonNullNode(return_.getMarkers(), ctx::receiveMarkers));
            return_ = return_.withExpression(ctx.receiveNode(return_.getExpression(), ctx::receiveTree));
            return return_;
        }

        @Override
        public J.Switch visitSwitch(J.Switch switch_, ReceiverContext ctx) {
            switch_ = switch_.withId(ctx.receiveNonNullValue(switch_.getId(), UUID.class));
            switch_ = switch_.withPrefix(ctx.receiveNonNullNode(switch_.getPrefix(), PythonReceiver::receiveSpace));
            switch_ = switch_.withMarkers(ctx.receiveNonNullNode(switch_.getMarkers(), ctx::receiveMarkers));
            switch_ = switch_.withSelector(ctx.receiveNonNullNode(switch_.getSelector(), ctx::receiveTree));
            switch_ = switch_.withCases(ctx.receiveNonNullNode(switch_.getCases(), ctx::receiveTree));
            return switch_;
        }

        @Override
        public J.SwitchExpression visitSwitchExpression(J.SwitchExpression switchExpression, ReceiverContext ctx) {
            switchExpression = switchExpression.withId(ctx.receiveNonNullValue(switchExpression.getId(), UUID.class));
            switchExpression = switchExpression.withPrefix(ctx.receiveNonNullNode(switchExpression.getPrefix(), PythonReceiver::receiveSpace));
            switchExpression = switchExpression.withMarkers(ctx.receiveNonNullNode(switchExpression.getMarkers(), ctx::receiveMarkers));
            switchExpression = switchExpression.withSelector(ctx.receiveNonNullNode(switchExpression.getSelector(), ctx::receiveTree));
            switchExpression = switchExpression.withCases(ctx.receiveNonNullNode(switchExpression.getCases(), ctx::receiveTree));
            return switchExpression;
        }

        @Override
        public J.Synchronized visitSynchronized(J.Synchronized synchronized_, ReceiverContext ctx) {
            synchronized_ = synchronized_.withId(ctx.receiveNonNullValue(synchronized_.getId(), UUID.class));
            synchronized_ = synchronized_.withPrefix(ctx.receiveNonNullNode(synchronized_.getPrefix(), PythonReceiver::receiveSpace));
            synchronized_ = synchronized_.withMarkers(ctx.receiveNonNullNode(synchronized_.getMarkers(), ctx::receiveMarkers));
            synchronized_ = synchronized_.withLock(ctx.receiveNonNullNode(synchronized_.getLock(), ctx::receiveTree));
            synchronized_ = synchronized_.withBody(ctx.receiveNonNullNode(synchronized_.getBody(), ctx::receiveTree));
            return synchronized_;
        }

        @Override
        public J.Ternary visitTernary(J.Ternary ternary, ReceiverContext ctx) {
            ternary = ternary.withId(ctx.receiveNonNullValue(ternary.getId(), UUID.class));
            ternary = ternary.withPrefix(ctx.receiveNonNullNode(ternary.getPrefix(), PythonReceiver::receiveSpace));
            ternary = ternary.withMarkers(ctx.receiveNonNullNode(ternary.getMarkers(), ctx::receiveMarkers));
            ternary = ternary.withCondition(ctx.receiveNonNullNode(ternary.getCondition(), ctx::receiveTree));
            ternary = ternary.getPadding().withTruePart(ctx.receiveNonNullNode(ternary.getPadding().getTruePart(), PythonReceiver::receiveLeftPaddedTree));
            ternary = ternary.getPadding().withFalsePart(ctx.receiveNonNullNode(ternary.getPadding().getFalsePart(), PythonReceiver::receiveLeftPaddedTree));
            ternary = ternary.withType(ctx.receiveValue(ternary.getType(), JavaType.class));
            return ternary;
        }

        @Override
        public J.Throw visitThrow(J.Throw throw_, ReceiverContext ctx) {
            throw_ = throw_.withId(ctx.receiveNonNullValue(throw_.getId(), UUID.class));
            throw_ = throw_.withPrefix(ctx.receiveNonNullNode(throw_.getPrefix(), PythonReceiver::receiveSpace));
            throw_ = throw_.withMarkers(ctx.receiveNonNullNode(throw_.getMarkers(), ctx::receiveMarkers));
            throw_ = throw_.withException(ctx.receiveNonNullNode(throw_.getException(), ctx::receiveTree));
            return throw_;
        }

        @Override
        public J.Try visitTry(J.Try try_, ReceiverContext ctx) {
            try_ = try_.withId(ctx.receiveNonNullValue(try_.getId(), UUID.class));
            try_ = try_.withPrefix(ctx.receiveNonNullNode(try_.getPrefix(), PythonReceiver::receiveSpace));
            try_ = try_.withMarkers(ctx.receiveNonNullNode(try_.getMarkers(), ctx::receiveMarkers));
            try_ = try_.getPadding().withResources(ctx.receiveNode(try_.getPadding().getResources(), PythonReceiver::receiveContainer));
            try_ = try_.withBody(ctx.receiveNonNullNode(try_.getBody(), ctx::receiveTree));
            try_ = try_.withCatches(ctx.receiveNonNullNodes(try_.getCatches(), ctx::receiveTree));
            try_ = try_.getPadding().withFinally(ctx.receiveNode(try_.getPadding().getFinally(), PythonReceiver::receiveLeftPaddedTree));
            return try_;
        }

        @Override
        public J.Try.Resource visitTryResource(J.Try.Resource resource, ReceiverContext ctx) {
            resource = resource.withId(ctx.receiveNonNullValue(resource.getId(), UUID.class));
            resource = resource.withPrefix(ctx.receiveNonNullNode(resource.getPrefix(), PythonReceiver::receiveSpace));
            resource = resource.withMarkers(ctx.receiveNonNullNode(resource.getMarkers(), ctx::receiveMarkers));
            resource = resource.withVariableDeclarations(ctx.receiveNonNullNode(resource.getVariableDeclarations(), ctx::receiveTree));
            resource = resource.withTerminatedWithSemicolon(ctx.receiveNonNullValue(resource.isTerminatedWithSemicolon(), boolean.class));
            return resource;
        }

        @Override
        public J.Try.Catch visitCatch(J.Try.Catch catch_, ReceiverContext ctx) {
            catch_ = catch_.withId(ctx.receiveNonNullValue(catch_.getId(), UUID.class));
            catch_ = catch_.withPrefix(ctx.receiveNonNullNode(catch_.getPrefix(), PythonReceiver::receiveSpace));
            catch_ = catch_.withMarkers(ctx.receiveNonNullNode(catch_.getMarkers(), ctx::receiveMarkers));
            catch_ = catch_.withParameter(ctx.receiveNonNullNode(catch_.getParameter(), ctx::receiveTree));
            catch_ = catch_.withBody(ctx.receiveNonNullNode(catch_.getBody(), ctx::receiveTree));
            return catch_;
        }

        @Override
        public J.TypeCast visitTypeCast(J.TypeCast typeCast, ReceiverContext ctx) {
            typeCast = typeCast.withId(ctx.receiveNonNullValue(typeCast.getId(), UUID.class));
            typeCast = typeCast.withPrefix(ctx.receiveNonNullNode(typeCast.getPrefix(), PythonReceiver::receiveSpace));
            typeCast = typeCast.withMarkers(ctx.receiveNonNullNode(typeCast.getMarkers(), ctx::receiveMarkers));
            typeCast = typeCast.withClazz(ctx.receiveNonNullNode(typeCast.getClazz(), ctx::receiveTree));
            typeCast = typeCast.withExpression(ctx.receiveNonNullNode(typeCast.getExpression(), ctx::receiveTree));
            return typeCast;
        }

        @Override
        public J.TypeParameter visitTypeParameter(J.TypeParameter typeParameter, ReceiverContext ctx) {
            typeParameter = typeParameter.withId(ctx.receiveNonNullValue(typeParameter.getId(), UUID.class));
            typeParameter = typeParameter.withPrefix(ctx.receiveNonNullNode(typeParameter.getPrefix(), PythonReceiver::receiveSpace));
            typeParameter = typeParameter.withMarkers(ctx.receiveNonNullNode(typeParameter.getMarkers(), ctx::receiveMarkers));
            typeParameter = typeParameter.withAnnotations(ctx.receiveNonNullNodes(typeParameter.getAnnotations(), ctx::receiveTree));
            typeParameter = typeParameter.withModifiers(ctx.receiveNonNullNodes(typeParameter.getModifiers(), PythonReceiver::receiveModifier));
            typeParameter = typeParameter.withName(ctx.receiveNonNullNode(typeParameter.getName(), ctx::receiveTree));
            typeParameter = typeParameter.getPadding().withBounds(ctx.receiveNode(typeParameter.getPadding().getBounds(), PythonReceiver::receiveContainer));
            return typeParameter;
        }

        @Override
        public J.Unary visitUnary(J.Unary unary, ReceiverContext ctx) {
            unary = unary.withId(ctx.receiveNonNullValue(unary.getId(), UUID.class));
            unary = unary.withPrefix(ctx.receiveNonNullNode(unary.getPrefix(), PythonReceiver::receiveSpace));
            unary = unary.withMarkers(ctx.receiveNonNullNode(unary.getMarkers(), ctx::receiveMarkers));
            unary = unary.getPadding().withOperator(ctx.receiveNonNullNode(unary.getPadding().getOperator(), leftPaddedValueReceiver(
		            J.Unary.Type.class)));
            unary = unary.withExpression(ctx.receiveNonNullNode(unary.getExpression(), ctx::receiveTree));
            unary = unary.withType(ctx.receiveValue(unary.getType(), JavaType.class));
            return unary;
        }

        @Override
        public J.VariableDeclarations visitVariableDeclarations(J.VariableDeclarations variableDeclarations, ReceiverContext ctx) {
            variableDeclarations = variableDeclarations.withId(ctx.receiveNonNullValue(variableDeclarations.getId(), UUID.class));
            variableDeclarations = variableDeclarations.withPrefix(ctx.receiveNonNullNode(variableDeclarations.getPrefix(), PythonReceiver::receiveSpace));
            variableDeclarations = variableDeclarations.withMarkers(ctx.receiveNonNullNode(variableDeclarations.getMarkers(), ctx::receiveMarkers));
            variableDeclarations = variableDeclarations.withLeadingAnnotations(ctx.receiveNonNullNodes(variableDeclarations.getLeadingAnnotations(), ctx::receiveTree));
            variableDeclarations = variableDeclarations.withModifiers(ctx.receiveNonNullNodes(variableDeclarations.getModifiers(), PythonReceiver::receiveModifier));
            variableDeclarations = variableDeclarations.withTypeExpression(ctx.receiveNode(variableDeclarations.getTypeExpression(), ctx::receiveTree));
            variableDeclarations = variableDeclarations.withVarargs(ctx.receiveNode(variableDeclarations.getVarargs(), PythonReceiver::receiveSpace));
            variableDeclarations = variableDeclarations.withDimensionsBeforeName(ctx.receiveNonNullNodes(variableDeclarations.getDimensionsBeforeName(), leftPaddedNodeReceiver(
		            Space.class)));
            variableDeclarations = variableDeclarations.getPadding().withVariables(ctx.receiveNonNullNodes(variableDeclarations.getPadding().getVariables(), PythonReceiver::receiveRightPaddedTree));
            return variableDeclarations;
        }

        @Override
        public J.VariableDeclarations.NamedVariable visitVariable(J.VariableDeclarations.NamedVariable namedVariable, ReceiverContext ctx) {
            namedVariable = namedVariable.withId(ctx.receiveNonNullValue(namedVariable.getId(), UUID.class));
            namedVariable = namedVariable.withPrefix(ctx.receiveNonNullNode(namedVariable.getPrefix(), PythonReceiver::receiveSpace));
            namedVariable = namedVariable.withMarkers(ctx.receiveNonNullNode(namedVariable.getMarkers(), ctx::receiveMarkers));
            namedVariable = namedVariable.withName(ctx.receiveNonNullNode(namedVariable.getName(), ctx::receiveTree));
            namedVariable = namedVariable.withDimensionsAfterName(ctx.receiveNonNullNodes(namedVariable.getDimensionsAfterName(), leftPaddedNodeReceiver(
		            Space.class)));
            namedVariable = namedVariable.getPadding().withInitializer(ctx.receiveNode(namedVariable.getPadding().getInitializer(), PythonReceiver::receiveLeftPaddedTree));
            namedVariable = namedVariable.withVariableType(ctx.receiveValue(namedVariable.getVariableType(), JavaType.Variable.class));
            return namedVariable;
        }

        @Override
        public J.WhileLoop visitWhileLoop(J.WhileLoop whileLoop, ReceiverContext ctx) {
            whileLoop = whileLoop.withId(ctx.receiveNonNullValue(whileLoop.getId(), UUID.class));
            whileLoop = whileLoop.withPrefix(ctx.receiveNonNullNode(whileLoop.getPrefix(), PythonReceiver::receiveSpace));
            whileLoop = whileLoop.withMarkers(ctx.receiveNonNullNode(whileLoop.getMarkers(), ctx::receiveMarkers));
            whileLoop = whileLoop.withCondition(ctx.receiveNonNullNode(whileLoop.getCondition(), ctx::receiveTree));
            whileLoop = whileLoop.getPadding().withBody(ctx.receiveNonNullNode(whileLoop.getPadding().getBody(), PythonReceiver::receiveRightPaddedTree));
            return whileLoop;
        }

        @Override
        public J.Wildcard visitWildcard(J.Wildcard wildcard, ReceiverContext ctx) {
            wildcard = wildcard.withId(ctx.receiveNonNullValue(wildcard.getId(), UUID.class));
            wildcard = wildcard.withPrefix(ctx.receiveNonNullNode(wildcard.getPrefix(), PythonReceiver::receiveSpace));
            wildcard = wildcard.withMarkers(ctx.receiveNonNullNode(wildcard.getMarkers(), ctx::receiveMarkers));
            wildcard = wildcard.getPadding().withBound(ctx.receiveNode(wildcard.getPadding().getBound(), leftPaddedValueReceiver(
		            J.Wildcard.Bound.class)));
            wildcard = wildcard.withBoundedType(ctx.receiveNode(wildcard.getBoundedType(), ctx::receiveTree));
            return wildcard;
        }

        @Override
        public J.Yield visitYield(J.Yield yield, ReceiverContext ctx) {
            yield = yield.withId(ctx.receiveNonNullValue(yield.getId(), UUID.class));
            yield = yield.withPrefix(ctx.receiveNonNullNode(yield.getPrefix(), PythonReceiver::receiveSpace));
            yield = yield.withMarkers(ctx.receiveNonNullNode(yield.getMarkers(), ctx::receiveMarkers));
            yield = yield.withImplicit(ctx.receiveNonNullValue(yield.isImplicit(), boolean.class));
            yield = yield.withValue(ctx.receiveNonNullNode(yield.getValue(), ctx::receiveTree));
            return yield;
        }

        @Override
        public J.Unknown visitUnknown(J.Unknown unknown, ReceiverContext ctx) {
            unknown = unknown.withId(ctx.receiveNonNullValue(unknown.getId(), UUID.class));
            unknown = unknown.withPrefix(ctx.receiveNonNullNode(unknown.getPrefix(), PythonReceiver::receiveSpace));
            unknown = unknown.withMarkers(ctx.receiveNonNullNode(unknown.getMarkers(), ctx::receiveMarkers));
            unknown = unknown.withSource(ctx.receiveNonNullNode(unknown.getSource(), ctx::receiveTree));
            return unknown;
        }

        @Override
        public J.Unknown.Source visitUnknownSource(J.Unknown.Source source, ReceiverContext ctx) {
            source = source.withId(ctx.receiveNonNullValue(source.getId(), UUID.class));
            source = source.withPrefix(ctx.receiveNonNullNode(source.getPrefix(), PythonReceiver::receiveSpace));
            source = source.withMarkers(ctx.receiveNonNullNode(source.getMarkers(), ctx::receiveMarkers));
            source = source.withText(ctx.receiveNonNullValue(source.getText(), String.class));
            return source;
        }

    }

    private static class Factory implements ReceiverFactory {

        @Override
        @SuppressWarnings("unchecked")
        public <T> T create(Class<T> type, ReceiverContext ctx) {
            if (type == Py.Binary.class) {
                return (T) new Py.Binary(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, leftPaddedValueReceiver(org.openrewrite.python.tree.Py.Binary.Type.class)),
                    ctx.receiveNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.ExceptionType.class) {
                return (T) new Py.ExceptionType(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveValue(null, JavaType.class),
                    ctx.receiveNonNullValue(null, boolean.class),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == Py.TypeHint.class) {
                return (T) new Py.TypeHint(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.CompilationUnit.class) {
                return (T) new Py.CompilationUnit(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, Path.class),
                    ctx.receiveValue(null, FileAttributes.class),
                    ctx.receiveValue(null, String.class),
                    ctx.receiveNonNullValue(null, boolean.class),
                    ctx.receiveValue(null, Checksum.class),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace)
                );
            }

            if (type == Py.ExpressionStatement.class) {
                return (T) new Py.ExpressionStatement(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == Py.StatementExpression.class) {
                return (T) new Py.StatementExpression(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == Py.MultiImport.class) {
                return (T) new Py.MultiImport(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullValue(null, boolean.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer)
                );
            }

            if (type == Py.KeyValue.class) {
                return (T) new Py.KeyValue(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.DictLiteral.class) {
                return (T) new Py.DictLiteral(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.CollectionLiteral.class) {
                return (T) new Py.CollectionLiteral(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, Py.CollectionLiteral.Kind.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.FormattedString.class) {
                return (T) new Py.FormattedString(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, String.class),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree)
                );
            }

            if (type == Py.FormattedString.Value.class) {
                return (T) new Py.FormattedString.Value(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNode(null, rightPaddedValueReceiver(Boolean.class)),
                    ctx.receiveValue(null, Py.FormattedString.Value.Conversion.class),
                    ctx.receiveNode(null, ctx::receiveTree)
                );
            }

            if (type == Py.Pass.class) {
                return (T) new Py.Pass(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers)
                );
            }

            if (type == Py.TrailingElseWrapper.class) {
                return (T) new Py.TrailingElseWrapper(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree)
                );
            }

            if (type == Py.ComprehensionExpression.class) {
                return (T) new Py.ComprehensionExpression(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, Py.ComprehensionExpression.Kind.class),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.ComprehensionExpression.Condition.class) {
                return (T) new Py.ComprehensionExpression.Condition(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == Py.ComprehensionExpression.Clause.class) {
                return (T) new Py.ComprehensionExpression.Clause(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveNodes(null, ctx::receiveTree)
                );
            }

            if (type == Py.Await.class) {
                return (T) new Py.Await(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.YieldFrom.class) {
                return (T) new Py.YieldFrom(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.VariableScope.class) {
                return (T) new Py.VariableScope(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, Py.VariableScope.Kind.class),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == Py.Del.class) {
                return (T) new Py.Del(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == Py.SpecialParameter.class) {
                return (T) new Py.SpecialParameter(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, Py.SpecialParameter.Kind.class),
                    ctx.receiveNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.Star.class) {
                return (T) new Py.Star(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, Py.Star.Kind.class),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.NamedArgument.class) {
                return (T) new Py.NamedArgument(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.TypeHintedExpression.class) {
                return (T) new Py.TypeHintedExpression(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.ErrorFrom.class) {
                return (T) new Py.ErrorFrom(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.MatchCase.class) {
                return (T) new Py.MatchCase(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.MatchCase.Pattern.class) {
                return (T) new Py.MatchCase.Pattern(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, Py.MatchCase.Pattern.Kind.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == Py.Slice.class) {
                return (T) new Py.Slice(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.AnnotatedType.class) {
                return (T) new J.AnnotatedType(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Annotation.class) {
                return (T) new J.Annotation(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer)
                );
            }

            if (type == J.ArrayAccess.class) {
                return (T) new J.ArrayAccess(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.ArrayType.class) {
                return (T) new J.ArrayType(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNodes(null, ctx::receiveTree),
                    ctx.receiveNode(null, leftPaddedNodeReceiver(Space.class)),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.Assert.class) {
                return (T) new J.Assert(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveLeftPaddedTree)
                );
            }

            if (type == J.Assignment.class) {
                return (T) new J.Assignment(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.AssignmentOperation.class) {
                return (T) new J.AssignmentOperation(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, leftPaddedValueReceiver(J.AssignmentOperation.Type.class)),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.Binary.class) {
                return (T) new J.Binary(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, leftPaddedValueReceiver(J.Binary.Type.class)),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.Block.class) {
                return (T) new J.Block(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, rightPaddedValueReceiver(Boolean.class)),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace)
                );
            }

            if (type == J.Break.class) {
                return (T) new J.Break(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Case.class) {
                return (T) new J.Case(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, J.Case.Type.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.ClassDeclaration.class) {
                return (T) new J.ClassDeclaration(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveModifier),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveClassDeclarationKind),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.FullyQualified.class)
                );
            }

            if (type == J.ClassDeclaration.Kind.class) {
                return (T) new J.ClassDeclaration.Kind(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullValue(null, J.ClassDeclaration.Kind.Type.class)
                );
            }

            if (type == J.Continue.class) {
                return (T) new J.Continue(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, ctx::receiveTree)
                );
            }

            if (type == J.DoWhileLoop.class) {
                return (T) new J.DoWhileLoop(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree)
                );
            }

            if (type == J.Empty.class) {
                return (T) new J.Empty(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers)
                );
            }

            if (type == J.EnumValue.class) {
                return (T) new J.EnumValue(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, ctx::receiveTree)
                );
            }

            if (type == J.EnumValueSet.class) {
                return (T) new J.EnumValueSet(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullValue(null, boolean.class)
                );
            }

            if (type == J.FieldAccess.class) {
                return (T) new J.FieldAccess(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.ForEachLoop.class) {
                return (T) new J.ForEachLoop(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.ForEachLoop.Control.class) {
                return (T) new J.ForEachLoop.Control(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.ForLoop.class) {
                return (T) new J.ForLoop(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.ForLoop.Control.class) {
                return (T) new J.ForLoop.Control(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.ParenthesizedTypeTree.class) {
                return (T) new J.ParenthesizedTypeTree(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Identifier.class) {
                return (T) new J.Identifier(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullValue(null, String.class),
                    ctx.receiveValue(null, JavaType.class),
                    ctx.receiveValue(null, JavaType.Variable.class)
                );
            }

            if (type == J.If.class) {
                return (T) new J.If(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNode(null, ctx::receiveTree)
                );
            }

            if (type == J.If.Else.class) {
                return (T) new J.If.Else(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.Import.class) {
                return (T) new J.Import(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, leftPaddedValueReceiver(Boolean.class)),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveLeftPaddedTree)
                );
            }

            if (type == J.InstanceOf.class) {
                return (T) new J.InstanceOf(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.IntersectionType.class) {
                return (T) new J.IntersectionType(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer)
                );
            }

            if (type == J.Label.class) {
                return (T) new J.Label(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Lambda.class) {
                return (T) new J.Lambda(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLambdaParameters),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.Lambda.Parameters.class) {
                return (T) new J.Lambda.Parameters(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, boolean.class),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.Literal.class) {
                return (T) new J.Literal(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveValue(null, Object.class),
                    ctx.receiveValue(null, String.class),
                    ctx.receiveValues(null, J.Literal.UnicodeEscape.class),
                    ctx.receiveValue(null, JavaType.Primitive.class)
                );
            }

            if (type == J.MemberReference.class) {
                return (T) new J.MemberReference(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveValue(null, JavaType.class),
                    ctx.receiveValue(null, JavaType.Method.class),
                    ctx.receiveValue(null, JavaType.Variable.class)
                );
            }

            if (type == J.MethodDeclaration.class) {
                return (T) new J.MethodDeclaration(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveModifier),
                    ctx.receiveNode(null, PythonReceiver::receiveMethodTypeParameters),
                    ctx.receiveNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveMethodIdentifierWithAnnotations),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveValue(null, JavaType.Method.class)
                );
            }

            if (type == J.MethodInvocation.class) {
                return (T) new J.MethodInvocation(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveValue(null, JavaType.Method.class)
                );
            }

            if (type == J.Modifier.class) {
                return (T) new J.Modifier(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveValue(null, String.class),
                    ctx.receiveNonNullValue(null, J.Modifier.Type.class),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree)
                );
            }

            if (type == J.MultiCatch.class) {
                return (T) new J.MultiCatch(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.NewArray.class) {
                return (T) new J.NewArray(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.ArrayDimension.class) {
                return (T) new J.ArrayDimension(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.NewClass.class) {
                return (T) new J.NewClass(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, PythonReceiver::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.Method.class)
                );
            }

            if (type == J.NullableType.class) {
                return (T) new J.NullableType(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.Package.class) {
                return (T) new J.Package(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree)
                );
            }

            if (type == J.ParameterizedType.class) {
                return (T) new J.ParameterizedType(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.Parentheses.class) {
                return (T) new J.Parentheses(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.ControlParentheses.class) {
                return (T) new J.ControlParentheses(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.Primitive.class) {
                return (T) new J.Primitive(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveValue(null, JavaType.Primitive.class)
                );
            }

            if (type == J.Return.class) {
                return (T) new J.Return(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Switch.class) {
                return (T) new J.Switch(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.SwitchExpression.class) {
                return (T) new J.SwitchExpression(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Synchronized.class) {
                return (T) new J.Synchronized(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Ternary.class) {
                return (T) new J.Ternary(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.Throw.class) {
                return (T) new J.Throw(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Try.class) {
                return (T) new J.Try(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveLeftPaddedTree)
                );
            }

            if (type == J.Try.Resource.class) {
                return (T) new J.Try.Resource(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullValue(null, boolean.class)
                );
            }

            if (type == J.Try.Catch.class) {
                return (T) new J.Try.Catch(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.TypeCast.class) {
                return (T) new J.TypeCast(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.TypeParameter.class) {
                return (T) new J.TypeParameter(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveModifier),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveContainer)
                );
            }

            if (type == J.TypeParameters.class) {
                return (T) new J.TypeParameters(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.Unary.class) {
                return (T) new J.Unary(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, leftPaddedValueReceiver(J.Unary.Type.class)),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveValue(null, JavaType.class)
                );
            }

            if (type == J.VariableDeclarations.class) {
                return (T) new J.VariableDeclarations(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveModifier),
                    ctx.receiveNode(null, ctx::receiveTree),
                    ctx.receiveNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNodes(null, leftPaddedNodeReceiver(Space.class)),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.VariableDeclarations.NamedVariable.class) {
                return (T) new J.VariableDeclarations.NamedVariable(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, leftPaddedNodeReceiver(Space.class)),
                    ctx.receiveNode(null, PythonReceiver::receiveLeftPaddedTree),
                    ctx.receiveValue(null, JavaType.Variable.class)
                );
            }

            if (type == J.WhileLoop.class) {
                return (T) new J.WhileLoop(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveRightPaddedTree)
                );
            }

            if (type == J.Wildcard.class) {
                return (T) new J.Wildcard(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNode(null, leftPaddedValueReceiver(J.Wildcard.Bound.class)),
                    ctx.receiveNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Yield.class) {
                return (T) new J.Yield(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, boolean.class),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Unknown.class) {
                return (T) new J.Unknown(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullNode(null, ctx::receiveTree)
                );
            }

            if (type == J.Unknown.Source.class) {
                return (T) new J.Unknown.Source(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, String.class)
                );
            }

            throw new IllegalArgumentException("Unknown type: " + type);
        }
    }

    private static J.ClassDeclaration.Kind receiveClassDeclarationKind(J.ClassDeclaration.@Nullable Kind kind, @Nullable Class<?> type, ReceiverContext ctx) {
        if (kind != null) {
            kind = kind.withId(ctx.receiveNonNullValue(kind.getId(), UUID.class));
            kind = kind.withPrefix(ctx.receiveNonNullNode(kind.getPrefix(), PythonReceiver::receiveSpace));
            kind = kind.withMarkers(ctx.receiveNonNullNode(kind.getMarkers(), ctx::receiveMarkers));
            kind = kind.withAnnotations(ctx.receiveNonNullNodes(kind.getAnnotations(), ctx::receiveTree));
            kind = kind.withType(ctx.receiveNonNullValue(kind.getType(), J.ClassDeclaration.Kind.Type.class));
        } else {
            kind = new J.ClassDeclaration.Kind(
                ctx.receiveNonNullValue(null, UUID.class),
                ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                ctx.receiveNonNullNodes(null, ctx::receiveTree),
                ctx.receiveNonNullValue(null, J.ClassDeclaration.Kind.Type.class)
            );
        }
        return kind;
    }

    private static J.Lambda.Parameters receiveLambdaParameters(J.Lambda.@Nullable Parameters parameters, @Nullable Class<?> type, ReceiverContext ctx) {
        if (parameters != null) {
            parameters = parameters.withId(ctx.receiveNonNullValue(parameters.getId(), UUID.class));
            parameters = parameters.withPrefix(ctx.receiveNonNullNode(parameters.getPrefix(), PythonReceiver::receiveSpace));
            parameters = parameters.withMarkers(ctx.receiveNonNullNode(parameters.getMarkers(), ctx::receiveMarkers));
            parameters = parameters.withParenthesized(ctx.receiveNonNullValue(parameters.isParenthesized(), boolean.class));
            parameters = parameters.getPadding().withParameters(ctx.receiveNonNullNodes(parameters.getPadding().getParameters(), PythonReceiver::receiveRightPaddedTree));
        } else {
            parameters = new J.Lambda.Parameters(
                    ctx.receiveNonNullValue(null, UUID.class),
                    ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                    ctx.receiveNonNullValue(null, boolean.class),
                    ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree)
            );
        }
        return parameters;
    }

    private static J.MethodDeclaration.IdentifierWithAnnotations receiveMethodIdentifierWithAnnotations(J.MethodDeclaration.@Nullable IdentifierWithAnnotations identifierWithAnnotations, @Nullable Class<?> identifierWithAnnotationsClass, ReceiverContext ctx) {
        if (identifierWithAnnotations != null) {
            identifierWithAnnotations = identifierWithAnnotations.withIdentifier(ctx.receiveNonNullNode(identifierWithAnnotations.getIdentifier(), ctx::receiveTree));
            identifierWithAnnotations = identifierWithAnnotations.withAnnotations(ctx.receiveNonNullNodes(identifierWithAnnotations.getAnnotations(), ctx::receiveTree));
        } else {
            identifierWithAnnotations = new J.MethodDeclaration.IdentifierWithAnnotations(
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNodes(null, ctx::receiveTree)
            );
        }
        return identifierWithAnnotations;
    }

    private static J.Modifier receiveModifier(J.@Nullable Modifier modifier, @Nullable Class<?> type, ReceiverContext ctx) {
        if (modifier != null) {
            modifier = modifier.withId(ctx.receiveNonNullValue(modifier.getId(), UUID.class));
            modifier = modifier.withPrefix(ctx.receiveNonNullNode(modifier.getPrefix(), PythonReceiver::receiveSpace));
            modifier = modifier.withMarkers(ctx.receiveNonNullNode(modifier.getMarkers(), ctx::receiveMarkers));
            modifier = modifier.withKeyword(ctx.receiveValue(modifier.getKeyword(), String.class));
            modifier = modifier.withType(ctx.receiveNonNullValue(modifier.getType(), J.Modifier.Type.class));
            modifier = modifier.withAnnotations(ctx.receiveNonNullNodes(modifier.getAnnotations(), ctx::receiveTree));
        } else {
            modifier = new J.Modifier(
                ctx.receiveNonNullValue(null, UUID.class),
                ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                ctx.receiveValue(null, String.class),
                ctx.receiveNonNullValue(null, J.Modifier.Type.class),
                ctx.receiveNonNullNodes(null, ctx::receiveTree)
            );
        }
        return modifier;
    }

    private static J.TypeParameters receiveMethodTypeParameters(J.@Nullable TypeParameters typeParameters, @Nullable Class<?> type, ReceiverContext ctx) {
        if (typeParameters != null) {
            typeParameters = typeParameters.withId(ctx.receiveNonNullValue(typeParameters.getId(), UUID.class));
            typeParameters = typeParameters.withPrefix(ctx.receiveNonNullNode(typeParameters.getPrefix(), PythonReceiver::receiveSpace));
            typeParameters = typeParameters.withMarkers(ctx.receiveNonNullNode(typeParameters.getMarkers(), ctx::receiveMarkers));
            typeParameters = typeParameters.withAnnotations(ctx.receiveNonNullNodes(typeParameters.getAnnotations(), ctx::receiveTree));
            typeParameters = typeParameters.getPadding().withTypeParameters(ctx.receiveNonNullNodes(typeParameters.getPadding().getTypeParameters(), PythonReceiver::receiveRightPaddedTree));
        } else {
            typeParameters = new J.TypeParameters(
                ctx.receiveNonNullValue(null, UUID.class),
                ctx.receiveNonNullNode(null, PythonReceiver::receiveSpace),
                ctx.receiveNonNullNode(null, ctx::receiveMarkers),
                ctx.receiveNonNullNodes(null, ctx::receiveTree),
                ctx.receiveNonNullNodes(null, PythonReceiver::receiveRightPaddedTree)
            );
        }
        return typeParameters;
    }

    private static <T extends J> JContainer<T> receiveContainer(@Nullable JContainer<T> container, @Nullable Class<?> type, ReceiverContext ctx) {
        return Extensions.receiveContainer(container, type, ctx);
    }

    private static <T> ReceiverContext.DetailsReceiver<JLeftPadded<T>> leftPaddedValueReceiver(Class<T> valueType) {
        return Extensions.leftPaddedValueReceiver(valueType);
    }

    private static <T> ReceiverContext.DetailsReceiver<JLeftPadded<T>> leftPaddedNodeReceiver(Class<T> nodeType) {
        return Extensions.leftPaddedNodeReceiver(nodeType);
    }

    private static <T extends J> JLeftPadded<T> receiveLeftPaddedTree(@Nullable JLeftPadded<T> leftPadded, @Nullable Class<?> type, ReceiverContext ctx) {
        return Extensions.receiveLeftPaddedTree(leftPadded, type, ctx);
    }

    private static <T> ReceiverContext.DetailsReceiver<JRightPadded<T>> rightPaddedValueReceiver(Class<T> valueType) {
        return Extensions.rightPaddedValueReceiver(valueType);
    }

    private static <T> ReceiverContext.DetailsReceiver<JRightPadded<T>> rightPaddedNodeReceiver(Class<T> nodeType) {
        return Extensions.rightPaddedNodeReceiver(nodeType);
    }

    private static <T extends J> JRightPadded<T> receiveRightPaddedTree(@Nullable JRightPadded<T> rightPadded, @Nullable Class<?> type, ReceiverContext ctx) {
        return Extensions.receiveRightPaddedTree(rightPadded, type, ctx);
    }

    private static Space receiveSpace(@Nullable Space space, @Nullable Class<?> type, ReceiverContext ctx) {
        return Extensions.receiveSpace(space, type, ctx);
    }

    private static Comment receiveComment(@Nullable Comment comment, @Nullable Class<Comment> type, ReceiverContext ctx) {
        return Extensions.receiveComment(comment, type, ctx);
    }

}
