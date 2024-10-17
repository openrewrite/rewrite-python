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

/*
 * -------------------THIS FILE IS AUTO GENERATED--------------------------
 * Changes to this file may cause incorrect behavior and will be lost if
 * the code is regenerated.
*/

package org.openrewrite.python.remote;

import lombok.Value;
import org.jspecify.annotations.Nullable;
import org.openrewrite.Cursor;
import org.openrewrite.Tree;
import org.openrewrite.python.PythonVisitor;
import org.openrewrite.python.tree.*;
import org.openrewrite.java.*;
import org.openrewrite.java.tree.*;
import org.openrewrite.remote.Sender;
import org.openrewrite.remote.SenderContext;

import java.util.function.Function;

@Value
public class PythonSender implements Sender<Py> {

    @Override
    public void send(Py after, @Nullable Py before, SenderContext ctx) {
        Visitor visitor = new Visitor();
        visitor.visit(after, ctx.fork(visitor, before));
        ctx.flush();
    }

    private static class Visitor extends PythonVisitor<SenderContext> {

        @Override
        public @Nullable J visit(@Nullable Tree tree, SenderContext ctx) {
            setCursor(new Cursor(getCursor(), tree));
            ctx.sendNode(tree, Function.identity(), ctx::sendTree);
            setCursor(getCursor().getParent());

            return (J) tree;
        }

        @Override
        public Py.Await visitAwait(Py.Await await, SenderContext ctx) {
            ctx.sendValue(await, Py.Await::getId);
            ctx.sendNode(await, Py.Await::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(await, Py.Await::getMarkers, ctx::sendMarkers);
            ctx.sendNode(await, Py.Await::getExpression, ctx::sendTree);
            ctx.sendTypedValue(await, Py.Await::getType);
            return await;
        }

        @Override
        public Py.Binary visitBinary(Py.Binary binary, SenderContext ctx) {
            ctx.sendValue(binary, Py.Binary::getId);
            ctx.sendNode(binary, Py.Binary::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(binary, Py.Binary::getMarkers, ctx::sendMarkers);
            ctx.sendNode(binary, Py.Binary::getLeft, ctx::sendTree);
            ctx.sendNode(binary, e -> e.getPadding().getOperator(), PythonSender::sendLeftPadded);
            ctx.sendNode(binary, Py.Binary::getNegation, PythonSender::sendSpace);
            ctx.sendNode(binary, Py.Binary::getRight, ctx::sendTree);
            ctx.sendTypedValue(binary, Py.Binary::getType);
            return binary;
        }

        @Override
        public Py.ChainedAssignment visitChainedAssignment(Py.ChainedAssignment chainedAssignment, SenderContext ctx) {
            ctx.sendValue(chainedAssignment, Py.ChainedAssignment::getId);
            ctx.sendNode(chainedAssignment, Py.ChainedAssignment::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(chainedAssignment, Py.ChainedAssignment::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(chainedAssignment, e -> e.getPadding().getVariables(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            ctx.sendNode(chainedAssignment, Py.ChainedAssignment::getAssignment, ctx::sendTree);
            ctx.sendTypedValue(chainedAssignment, Py.ChainedAssignment::getType);
            return chainedAssignment;
        }

        @Override
        public Py.ExceptionType visitExceptionType(Py.ExceptionType exceptionType, SenderContext ctx) {
            ctx.sendValue(exceptionType, Py.ExceptionType::getId);
            ctx.sendNode(exceptionType, Py.ExceptionType::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(exceptionType, Py.ExceptionType::getMarkers, ctx::sendMarkers);
            ctx.sendTypedValue(exceptionType, Py.ExceptionType::getType);
            ctx.sendValue(exceptionType, Py.ExceptionType::isExceptionGroup);
            ctx.sendNode(exceptionType, Py.ExceptionType::getExpression, ctx::sendTree);
            return exceptionType;
        }

        @Override
        public Py.LiteralType visitLiteralType(Py.LiteralType literalType, SenderContext ctx) {
            ctx.sendValue(literalType, Py.LiteralType::getId);
            ctx.sendNode(literalType, Py.LiteralType::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(literalType, Py.LiteralType::getMarkers, ctx::sendMarkers);
            ctx.sendNode(literalType, Py.LiteralType::getLiteral, ctx::sendTree);
            ctx.sendTypedValue(literalType, Py.LiteralType::getType);
            return literalType;
        }

        @Override
        public Py.TypeHint visitTypeHint(Py.TypeHint typeHint, SenderContext ctx) {
            ctx.sendValue(typeHint, Py.TypeHint::getId);
            ctx.sendNode(typeHint, Py.TypeHint::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(typeHint, Py.TypeHint::getMarkers, ctx::sendMarkers);
            ctx.sendNode(typeHint, Py.TypeHint::getTypeTree, ctx::sendTree);
            ctx.sendTypedValue(typeHint, Py.TypeHint::getType);
            return typeHint;
        }

        @Override
        public Py.CompilationUnit visitCompilationUnit(Py.CompilationUnit compilationUnit, SenderContext ctx) {
            ctx.sendValue(compilationUnit, Py.CompilationUnit::getId);
            ctx.sendNode(compilationUnit, Py.CompilationUnit::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(compilationUnit, Py.CompilationUnit::getMarkers, ctx::sendMarkers);
            ctx.sendValue(compilationUnit, Py.CompilationUnit::getSourcePath);
            ctx.sendTypedValue(compilationUnit, Py.CompilationUnit::getFileAttributes);
            ctx.sendValue(compilationUnit, e -> e.getCharset() != null ? e.getCharset().name() : "UTF-8");
            ctx.sendValue(compilationUnit, Py.CompilationUnit::isCharsetBomMarked);
            ctx.sendTypedValue(compilationUnit, Py.CompilationUnit::getChecksum);
            ctx.sendNodes(compilationUnit, e -> e.getPadding().getImports(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            ctx.sendNodes(compilationUnit, e -> e.getPadding().getStatements(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            ctx.sendNode(compilationUnit, Py.CompilationUnit::getEof, PythonSender::sendSpace);
            return compilationUnit;
        }

        @Override
        public Py.ExpressionStatement visitExpressionStatement(Py.ExpressionStatement expressionStatement, SenderContext ctx) {
            ctx.sendValue(expressionStatement, Py.ExpressionStatement::getId);
            ctx.sendNode(expressionStatement, Py.ExpressionStatement::getExpression, ctx::sendTree);
            return expressionStatement;
        }

        @Override
        public Py.StatementExpression visitStatementExpression(Py.StatementExpression statementExpression, SenderContext ctx) {
            ctx.sendValue(statementExpression, Py.StatementExpression::getId);
            ctx.sendNode(statementExpression, Py.StatementExpression::getStatement, ctx::sendTree);
            return statementExpression;
        }

        @Override
        public Py.MultiImport visitMultiImport(Py.MultiImport multiImport, SenderContext ctx) {
            ctx.sendValue(multiImport, Py.MultiImport::getId);
            ctx.sendNode(multiImport, Py.MultiImport::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(multiImport, Py.MultiImport::getMarkers, ctx::sendMarkers);
            ctx.sendNode(multiImport, e -> e.getPadding().getFrom(), PythonSender::sendRightPadded);
            ctx.sendValue(multiImport, Py.MultiImport::isParenthesized);
            ctx.sendNode(multiImport, e -> e.getPadding().getNames(), PythonSender::sendContainer);
            return multiImport;
        }

        @Override
        public Py.KeyValue visitKeyValue(Py.KeyValue keyValue, SenderContext ctx) {
            ctx.sendValue(keyValue, Py.KeyValue::getId);
            ctx.sendNode(keyValue, Py.KeyValue::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(keyValue, Py.KeyValue::getMarkers, ctx::sendMarkers);
            ctx.sendNode(keyValue, e -> e.getPadding().getKey(), PythonSender::sendRightPadded);
            ctx.sendNode(keyValue, Py.KeyValue::getValue, ctx::sendTree);
            ctx.sendTypedValue(keyValue, Py.KeyValue::getType);
            return keyValue;
        }

        @Override
        public Py.DictLiteral visitDictLiteral(Py.DictLiteral dictLiteral, SenderContext ctx) {
            ctx.sendValue(dictLiteral, Py.DictLiteral::getId);
            ctx.sendNode(dictLiteral, Py.DictLiteral::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(dictLiteral, Py.DictLiteral::getMarkers, ctx::sendMarkers);
            ctx.sendNode(dictLiteral, e -> e.getPadding().getElements(), PythonSender::sendContainer);
            ctx.sendTypedValue(dictLiteral, Py.DictLiteral::getType);
            return dictLiteral;
        }

        @Override
        public Py.CollectionLiteral visitCollectionLiteral(Py.CollectionLiteral collectionLiteral, SenderContext ctx) {
            ctx.sendValue(collectionLiteral, Py.CollectionLiteral::getId);
            ctx.sendNode(collectionLiteral, Py.CollectionLiteral::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(collectionLiteral, Py.CollectionLiteral::getMarkers, ctx::sendMarkers);
            ctx.sendValue(collectionLiteral, Py.CollectionLiteral::getKind);
            ctx.sendNode(collectionLiteral, e -> e.getPadding().getElements(), PythonSender::sendContainer);
            ctx.sendTypedValue(collectionLiteral, Py.CollectionLiteral::getType);
            return collectionLiteral;
        }

        @Override
        public Py.FormattedString visitFormattedString(Py.FormattedString formattedString, SenderContext ctx) {
            ctx.sendValue(formattedString, Py.FormattedString::getId);
            ctx.sendNode(formattedString, Py.FormattedString::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(formattedString, Py.FormattedString::getMarkers, ctx::sendMarkers);
            ctx.sendValue(formattedString, Py.FormattedString::getDelimiter);
            ctx.sendNodes(formattedString, Py.FormattedString::getParts, ctx::sendTree, Tree::getId);
            return formattedString;
        }

        @Override
        public Py.FormattedString.Value visitFormattedStringValue(Py.FormattedString.Value value, SenderContext ctx) {
            ctx.sendValue(value, Py.FormattedString.Value::getId);
            ctx.sendNode(value, Py.FormattedString.Value::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(value, Py.FormattedString.Value::getMarkers, ctx::sendMarkers);
            ctx.sendNode(value, e -> e.getPadding().getExpression(), PythonSender::sendRightPadded);
            ctx.sendNode(value, e -> e.getPadding().getDebug(), PythonSender::sendRightPadded);
            ctx.sendValue(value, Py.FormattedString.Value::getConversion);
            ctx.sendNode(value, Py.FormattedString.Value::getFormat, ctx::sendTree);
            return value;
        }

        @Override
        public Py.Pass visitPass(Py.Pass pass, SenderContext ctx) {
            ctx.sendValue(pass, Py.Pass::getId);
            ctx.sendNode(pass, Py.Pass::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(pass, Py.Pass::getMarkers, ctx::sendMarkers);
            return pass;
        }

        @Override
        public Py.TrailingElseWrapper visitTrailingElseWrapper(Py.TrailingElseWrapper trailingElseWrapper, SenderContext ctx) {
            ctx.sendValue(trailingElseWrapper, Py.TrailingElseWrapper::getId);
            ctx.sendNode(trailingElseWrapper, Py.TrailingElseWrapper::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(trailingElseWrapper, Py.TrailingElseWrapper::getMarkers, ctx::sendMarkers);
            ctx.sendNode(trailingElseWrapper, Py.TrailingElseWrapper::getStatement, ctx::sendTree);
            ctx.sendNode(trailingElseWrapper, e -> e.getPadding().getElseBlock(), PythonSender::sendLeftPadded);
            return trailingElseWrapper;
        }

        @Override
        public Py.ComprehensionExpression visitComprehensionExpression(Py.ComprehensionExpression comprehensionExpression, SenderContext ctx) {
            ctx.sendValue(comprehensionExpression, Py.ComprehensionExpression::getId);
            ctx.sendNode(comprehensionExpression, Py.ComprehensionExpression::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(comprehensionExpression, Py.ComprehensionExpression::getMarkers, ctx::sendMarkers);
            ctx.sendValue(comprehensionExpression, Py.ComprehensionExpression::getKind);
            ctx.sendNode(comprehensionExpression, Py.ComprehensionExpression::getResult, ctx::sendTree);
            ctx.sendNodes(comprehensionExpression, Py.ComprehensionExpression::getClauses, ctx::sendTree, Tree::getId);
            ctx.sendNode(comprehensionExpression, Py.ComprehensionExpression::getSuffix, PythonSender::sendSpace);
            ctx.sendTypedValue(comprehensionExpression, Py.ComprehensionExpression::getType);
            return comprehensionExpression;
        }

        @Override
        public Py.ComprehensionExpression.Condition visitComprehensionCondition(Py.ComprehensionExpression.Condition condition, SenderContext ctx) {
            ctx.sendValue(condition, Py.ComprehensionExpression.Condition::getId);
            ctx.sendNode(condition, Py.ComprehensionExpression.Condition::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(condition, Py.ComprehensionExpression.Condition::getMarkers, ctx::sendMarkers);
            ctx.sendNode(condition, Py.ComprehensionExpression.Condition::getExpression, ctx::sendTree);
            return condition;
        }

        @Override
        public Py.ComprehensionExpression.Clause visitComprehensionClause(Py.ComprehensionExpression.Clause clause, SenderContext ctx) {
            ctx.sendValue(clause, Py.ComprehensionExpression.Clause::getId);
            ctx.sendNode(clause, Py.ComprehensionExpression.Clause::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(clause, Py.ComprehensionExpression.Clause::getMarkers, ctx::sendMarkers);
            ctx.sendNode(clause, Py.ComprehensionExpression.Clause::getIteratorVariable, ctx::sendTree);
            ctx.sendNode(clause, e -> e.getPadding().getIteratedList(), PythonSender::sendLeftPadded);
            ctx.sendNodes(clause, Py.ComprehensionExpression.Clause::getConditions, ctx::sendTree, Tree::getId);
            return clause;
        }

        @Override
        public Py.YieldFrom visitYieldFrom(Py.YieldFrom yieldFrom, SenderContext ctx) {
            ctx.sendValue(yieldFrom, Py.YieldFrom::getId);
            ctx.sendNode(yieldFrom, Py.YieldFrom::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(yieldFrom, Py.YieldFrom::getMarkers, ctx::sendMarkers);
            ctx.sendNode(yieldFrom, Py.YieldFrom::getExpression, ctx::sendTree);
            ctx.sendTypedValue(yieldFrom, Py.YieldFrom::getType);
            return yieldFrom;
        }

        @Override
        public Py.UnionType visitUnionType(Py.UnionType unionType, SenderContext ctx) {
            ctx.sendValue(unionType, Py.UnionType::getId);
            ctx.sendNode(unionType, Py.UnionType::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(unionType, Py.UnionType::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(unionType, e -> e.getPadding().getTypes(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            ctx.sendTypedValue(unionType, Py.UnionType::getType);
            return unionType;
        }

        @Override
        public Py.VariableScope visitVariableScope(Py.VariableScope variableScope, SenderContext ctx) {
            ctx.sendValue(variableScope, Py.VariableScope::getId);
            ctx.sendNode(variableScope, Py.VariableScope::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(variableScope, Py.VariableScope::getMarkers, ctx::sendMarkers);
            ctx.sendValue(variableScope, Py.VariableScope::getKind);
            ctx.sendNodes(variableScope, e -> e.getPadding().getNames(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            return variableScope;
        }

        @Override
        public Py.Del visitDel(Py.Del del, SenderContext ctx) {
            ctx.sendValue(del, Py.Del::getId);
            ctx.sendNode(del, Py.Del::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(del, Py.Del::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(del, e -> e.getPadding().getTargets(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            return del;
        }

        @Override
        public Py.SpecialParameter visitSpecialParameter(Py.SpecialParameter specialParameter, SenderContext ctx) {
            ctx.sendValue(specialParameter, Py.SpecialParameter::getId);
            ctx.sendNode(specialParameter, Py.SpecialParameter::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(specialParameter, Py.SpecialParameter::getMarkers, ctx::sendMarkers);
            ctx.sendValue(specialParameter, Py.SpecialParameter::getKind);
            ctx.sendNode(specialParameter, Py.SpecialParameter::getTypeHint, ctx::sendTree);
            ctx.sendTypedValue(specialParameter, Py.SpecialParameter::getType);
            return specialParameter;
        }

        @Override
        public Py.Star visitStar(Py.Star star, SenderContext ctx) {
            ctx.sendValue(star, Py.Star::getId);
            ctx.sendNode(star, Py.Star::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(star, Py.Star::getMarkers, ctx::sendMarkers);
            ctx.sendValue(star, Py.Star::getKind);
            ctx.sendNode(star, Py.Star::getExpression, ctx::sendTree);
            ctx.sendTypedValue(star, Py.Star::getType);
            return star;
        }

        @Override
        public Py.NamedArgument visitNamedArgument(Py.NamedArgument namedArgument, SenderContext ctx) {
            ctx.sendValue(namedArgument, Py.NamedArgument::getId);
            ctx.sendNode(namedArgument, Py.NamedArgument::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(namedArgument, Py.NamedArgument::getMarkers, ctx::sendMarkers);
            ctx.sendNode(namedArgument, Py.NamedArgument::getName, ctx::sendTree);
            ctx.sendNode(namedArgument, e -> e.getPadding().getValue(), PythonSender::sendLeftPadded);
            ctx.sendTypedValue(namedArgument, Py.NamedArgument::getType);
            return namedArgument;
        }

        @Override
        public Py.TypeHintedExpression visitTypeHintedExpression(Py.TypeHintedExpression typeHintedExpression, SenderContext ctx) {
            ctx.sendValue(typeHintedExpression, Py.TypeHintedExpression::getId);
            ctx.sendNode(typeHintedExpression, Py.TypeHintedExpression::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(typeHintedExpression, Py.TypeHintedExpression::getMarkers, ctx::sendMarkers);
            ctx.sendNode(typeHintedExpression, Py.TypeHintedExpression::getExpression, ctx::sendTree);
            ctx.sendNode(typeHintedExpression, Py.TypeHintedExpression::getTypeHint, ctx::sendTree);
            ctx.sendTypedValue(typeHintedExpression, Py.TypeHintedExpression::getType);
            return typeHintedExpression;
        }

        @Override
        public Py.ErrorFrom visitErrorFrom(Py.ErrorFrom errorFrom, SenderContext ctx) {
            ctx.sendValue(errorFrom, Py.ErrorFrom::getId);
            ctx.sendNode(errorFrom, Py.ErrorFrom::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(errorFrom, Py.ErrorFrom::getMarkers, ctx::sendMarkers);
            ctx.sendNode(errorFrom, Py.ErrorFrom::getError, ctx::sendTree);
            ctx.sendNode(errorFrom, e -> e.getPadding().getFrom(), PythonSender::sendLeftPadded);
            ctx.sendTypedValue(errorFrom, Py.ErrorFrom::getType);
            return errorFrom;
        }

        @Override
        public Py.MatchCase visitMatchCase(Py.MatchCase matchCase, SenderContext ctx) {
            ctx.sendValue(matchCase, Py.MatchCase::getId);
            ctx.sendNode(matchCase, Py.MatchCase::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(matchCase, Py.MatchCase::getMarkers, ctx::sendMarkers);
            ctx.sendNode(matchCase, Py.MatchCase::getPattern, ctx::sendTree);
            ctx.sendNode(matchCase, e -> e.getPadding().getGuard(), PythonSender::sendLeftPadded);
            ctx.sendTypedValue(matchCase, Py.MatchCase::getType);
            return matchCase;
        }

        @Override
        public Py.MatchCase.Pattern visitMatchCasePattern(Py.MatchCase.Pattern pattern, SenderContext ctx) {
            ctx.sendValue(pattern, Py.MatchCase.Pattern::getId);
            ctx.sendNode(pattern, Py.MatchCase.Pattern::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(pattern, Py.MatchCase.Pattern::getMarkers, ctx::sendMarkers);
            ctx.sendValue(pattern, Py.MatchCase.Pattern::getKind);
            ctx.sendNode(pattern, e -> e.getPadding().getChildren(), PythonSender::sendContainer);
            ctx.sendTypedValue(pattern, Py.MatchCase.Pattern::getType);
            return pattern;
        }

        @Override
        public Py.Slice visitSlice(Py.Slice slice, SenderContext ctx) {
            ctx.sendValue(slice, Py.Slice::getId);
            ctx.sendNode(slice, Py.Slice::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(slice, Py.Slice::getMarkers, ctx::sendMarkers);
            ctx.sendNode(slice, e -> e.getPadding().getStart(), PythonSender::sendRightPadded);
            ctx.sendNode(slice, e -> e.getPadding().getStop(), PythonSender::sendRightPadded);
            ctx.sendNode(slice, e -> e.getPadding().getStep(), PythonSender::sendRightPadded);
            return slice;
        }

        @Override
        public J.AnnotatedType visitAnnotatedType(J.AnnotatedType annotatedType, SenderContext ctx) {
            ctx.sendValue(annotatedType, J.AnnotatedType::getId);
            ctx.sendNode(annotatedType, J.AnnotatedType::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(annotatedType, J.AnnotatedType::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(annotatedType, J.AnnotatedType::getAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNode(annotatedType, J.AnnotatedType::getTypeExpression, ctx::sendTree);
            return annotatedType;
        }

        @Override
        public J.Annotation visitAnnotation(J.Annotation annotation, SenderContext ctx) {
            ctx.sendValue(annotation, J.Annotation::getId);
            ctx.sendNode(annotation, J.Annotation::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(annotation, J.Annotation::getMarkers, ctx::sendMarkers);
            ctx.sendNode(annotation, J.Annotation::getAnnotationType, ctx::sendTree);
            ctx.sendNode(annotation, e -> e.getPadding().getArguments(), PythonSender::sendContainer);
            return annotation;
        }

        @Override
        public J.ArrayAccess visitArrayAccess(J.ArrayAccess arrayAccess, SenderContext ctx) {
            ctx.sendValue(arrayAccess, J.ArrayAccess::getId);
            ctx.sendNode(arrayAccess, J.ArrayAccess::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(arrayAccess, J.ArrayAccess::getMarkers, ctx::sendMarkers);
            ctx.sendNode(arrayAccess, J.ArrayAccess::getIndexed, ctx::sendTree);
            ctx.sendNode(arrayAccess, J.ArrayAccess::getDimension, ctx::sendTree);
            ctx.sendTypedValue(arrayAccess, J.ArrayAccess::getType);
            return arrayAccess;
        }

        @Override
        public J.ArrayType visitArrayType(J.ArrayType arrayType, SenderContext ctx) {
            ctx.sendValue(arrayType, J.ArrayType::getId);
            ctx.sendNode(arrayType, J.ArrayType::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(arrayType, J.ArrayType::getMarkers, ctx::sendMarkers);
            ctx.sendNode(arrayType, J.ArrayType::getElementType, ctx::sendTree);
            ctx.sendNodes(arrayType, J.ArrayType::getAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNode(arrayType, J.ArrayType::getDimension, PythonSender::sendLeftPadded);
            ctx.sendTypedValue(arrayType, J.ArrayType::getType);
            return arrayType;
        }

        @Override
        public J.Assert visitAssert(J.Assert assert_, SenderContext ctx) {
            ctx.sendValue(assert_, J.Assert::getId);
            ctx.sendNode(assert_, J.Assert::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(assert_, J.Assert::getMarkers, ctx::sendMarkers);
            ctx.sendNode(assert_, J.Assert::getCondition, ctx::sendTree);
            ctx.sendNode(assert_, J.Assert::getDetail, PythonSender::sendLeftPadded);
            return assert_;
        }

        @Override
        public J.Assignment visitAssignment(J.Assignment assignment, SenderContext ctx) {
            ctx.sendValue(assignment, J.Assignment::getId);
            ctx.sendNode(assignment, J.Assignment::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(assignment, J.Assignment::getMarkers, ctx::sendMarkers);
            ctx.sendNode(assignment, J.Assignment::getVariable, ctx::sendTree);
            ctx.sendNode(assignment, e -> e.getPadding().getAssignment(), PythonSender::sendLeftPadded);
            ctx.sendTypedValue(assignment, J.Assignment::getType);
            return assignment;
        }

        @Override
        public J.AssignmentOperation visitAssignmentOperation(J.AssignmentOperation assignmentOperation, SenderContext ctx) {
            ctx.sendValue(assignmentOperation, J.AssignmentOperation::getId);
            ctx.sendNode(assignmentOperation, J.AssignmentOperation::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(assignmentOperation, J.AssignmentOperation::getMarkers, ctx::sendMarkers);
            ctx.sendNode(assignmentOperation, J.AssignmentOperation::getVariable, ctx::sendTree);
            ctx.sendNode(assignmentOperation, e -> e.getPadding().getOperator(), PythonSender::sendLeftPadded);
            ctx.sendNode(assignmentOperation, J.AssignmentOperation::getAssignment, ctx::sendTree);
            ctx.sendTypedValue(assignmentOperation, J.AssignmentOperation::getType);
            return assignmentOperation;
        }

        @Override
        public J.Binary visitBinary(J.Binary binary, SenderContext ctx) {
            ctx.sendValue(binary, J.Binary::getId);
            ctx.sendNode(binary, J.Binary::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(binary, J.Binary::getMarkers, ctx::sendMarkers);
            ctx.sendNode(binary, J.Binary::getLeft, ctx::sendTree);
            ctx.sendNode(binary, e -> e.getPadding().getOperator(), PythonSender::sendLeftPadded);
            ctx.sendNode(binary, J.Binary::getRight, ctx::sendTree);
            ctx.sendTypedValue(binary, J.Binary::getType);
            return binary;
        }

        @Override
        public J.Block visitBlock(J.Block block, SenderContext ctx) {
            ctx.sendValue(block, J.Block::getId);
            ctx.sendNode(block, J.Block::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(block, J.Block::getMarkers, ctx::sendMarkers);
            ctx.sendNode(block, e -> e.getPadding().getStatic(), PythonSender::sendRightPadded);
            ctx.sendNodes(block, e -> e.getPadding().getStatements(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            ctx.sendNode(block, J.Block::getEnd, PythonSender::sendSpace);
            return block;
        }

        @Override
        public J.Break visitBreak(J.Break break_, SenderContext ctx) {
            ctx.sendValue(break_, J.Break::getId);
            ctx.sendNode(break_, J.Break::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(break_, J.Break::getMarkers, ctx::sendMarkers);
            ctx.sendNode(break_, J.Break::getLabel, ctx::sendTree);
            return break_;
        }

        @Override
        public J.Case visitCase(J.Case case_, SenderContext ctx) {
            ctx.sendValue(case_, J.Case::getId);
            ctx.sendNode(case_, J.Case::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(case_, J.Case::getMarkers, ctx::sendMarkers);
            ctx.sendValue(case_, J.Case::getType);
            ctx.sendNode(case_, e -> e.getPadding().getExpressions(), PythonSender::sendContainer);
            ctx.sendNode(case_, e -> e.getPadding().getStatements(), PythonSender::sendContainer);
            ctx.sendNode(case_, e -> e.getPadding().getBody(), PythonSender::sendRightPadded);
            return case_;
        }

        @Override
        public J.ClassDeclaration visitClassDeclaration(J.ClassDeclaration classDeclaration, SenderContext ctx) {
            ctx.sendValue(classDeclaration, J.ClassDeclaration::getId);
            ctx.sendNode(classDeclaration, J.ClassDeclaration::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(classDeclaration, J.ClassDeclaration::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(classDeclaration, J.ClassDeclaration::getLeadingAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNodes(classDeclaration, J.ClassDeclaration::getModifiers, this::sendModifier, Tree::getId);
            ctx.sendNode(classDeclaration, e -> e.getPadding().getKind(), this::sendClassDeclarationKind);
            ctx.sendNode(classDeclaration, J.ClassDeclaration::getName, ctx::sendTree);
            ctx.sendNode(classDeclaration, e -> e.getPadding().getTypeParameters(), PythonSender::sendContainer);
            ctx.sendNode(classDeclaration, e -> e.getPadding().getPrimaryConstructor(), PythonSender::sendContainer);
            ctx.sendNode(classDeclaration, e -> e.getPadding().getExtends(), PythonSender::sendLeftPadded);
            ctx.sendNode(classDeclaration, e -> e.getPadding().getImplements(), PythonSender::sendContainer);
            ctx.sendNode(classDeclaration, e -> e.getPadding().getPermits(), PythonSender::sendContainer);
            ctx.sendNode(classDeclaration, J.ClassDeclaration::getBody, ctx::sendTree);
            ctx.sendTypedValue(classDeclaration, J.ClassDeclaration::getType);
            return classDeclaration;
        }

        private void sendClassDeclarationKind(J.ClassDeclaration.Kind kind, SenderContext ctx) {
            ctx.sendValue(kind, J.ClassDeclaration.Kind::getId);
            ctx.sendNode(kind, J.ClassDeclaration.Kind::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(kind, J.ClassDeclaration.Kind::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(kind, J.ClassDeclaration.Kind::getAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendValue(kind, J.ClassDeclaration.Kind::getType);
        }

        @Override
        public J.Continue visitContinue(J.Continue continue_, SenderContext ctx) {
            ctx.sendValue(continue_, J.Continue::getId);
            ctx.sendNode(continue_, J.Continue::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(continue_, J.Continue::getMarkers, ctx::sendMarkers);
            ctx.sendNode(continue_, J.Continue::getLabel, ctx::sendTree);
            return continue_;
        }

        @Override
        public J.DoWhileLoop visitDoWhileLoop(J.DoWhileLoop doWhileLoop, SenderContext ctx) {
            ctx.sendValue(doWhileLoop, J.DoWhileLoop::getId);
            ctx.sendNode(doWhileLoop, J.DoWhileLoop::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(doWhileLoop, J.DoWhileLoop::getMarkers, ctx::sendMarkers);
            ctx.sendNode(doWhileLoop, e -> e.getPadding().getBody(), PythonSender::sendRightPadded);
            ctx.sendNode(doWhileLoop, e -> e.getPadding().getWhileCondition(), PythonSender::sendLeftPadded);
            return doWhileLoop;
        }

        @Override
        public J.Empty visitEmpty(J.Empty empty, SenderContext ctx) {
            ctx.sendValue(empty, J.Empty::getId);
            ctx.sendNode(empty, J.Empty::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(empty, J.Empty::getMarkers, ctx::sendMarkers);
            return empty;
        }

        @Override
        public J.EnumValue visitEnumValue(J.EnumValue enumValue, SenderContext ctx) {
            ctx.sendValue(enumValue, J.EnumValue::getId);
            ctx.sendNode(enumValue, J.EnumValue::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(enumValue, J.EnumValue::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(enumValue, J.EnumValue::getAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNode(enumValue, J.EnumValue::getName, ctx::sendTree);
            ctx.sendNode(enumValue, J.EnumValue::getInitializer, ctx::sendTree);
            return enumValue;
        }

        @Override
        public J.EnumValueSet visitEnumValueSet(J.EnumValueSet enumValueSet, SenderContext ctx) {
            ctx.sendValue(enumValueSet, J.EnumValueSet::getId);
            ctx.sendNode(enumValueSet, J.EnumValueSet::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(enumValueSet, J.EnumValueSet::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(enumValueSet, e -> e.getPadding().getEnums(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            ctx.sendValue(enumValueSet, J.EnumValueSet::isTerminatedWithSemicolon);
            return enumValueSet;
        }

        @Override
        public J.FieldAccess visitFieldAccess(J.FieldAccess fieldAccess, SenderContext ctx) {
            ctx.sendValue(fieldAccess, J.FieldAccess::getId);
            ctx.sendNode(fieldAccess, J.FieldAccess::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(fieldAccess, J.FieldAccess::getMarkers, ctx::sendMarkers);
            ctx.sendNode(fieldAccess, J.FieldAccess::getTarget, ctx::sendTree);
            ctx.sendNode(fieldAccess, e -> e.getPadding().getName(), PythonSender::sendLeftPadded);
            ctx.sendTypedValue(fieldAccess, J.FieldAccess::getType);
            return fieldAccess;
        }

        @Override
        public J.ForEachLoop visitForEachLoop(J.ForEachLoop forEachLoop, SenderContext ctx) {
            ctx.sendValue(forEachLoop, J.ForEachLoop::getId);
            ctx.sendNode(forEachLoop, J.ForEachLoop::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(forEachLoop, J.ForEachLoop::getMarkers, ctx::sendMarkers);
            ctx.sendNode(forEachLoop, J.ForEachLoop::getControl, ctx::sendTree);
            ctx.sendNode(forEachLoop, e -> e.getPadding().getBody(), PythonSender::sendRightPadded);
            return forEachLoop;
        }

        @Override
        public J.ForEachLoop.Control visitForEachControl(J.ForEachLoop.Control control, SenderContext ctx) {
            ctx.sendValue(control, J.ForEachLoop.Control::getId);
            ctx.sendNode(control, J.ForEachLoop.Control::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(control, J.ForEachLoop.Control::getMarkers, ctx::sendMarkers);
            ctx.sendNode(control, e -> e.getPadding().getVariable(), PythonSender::sendRightPadded);
            ctx.sendNode(control, e -> e.getPadding().getIterable(), PythonSender::sendRightPadded);
            return control;
        }

        @Override
        public J.ForLoop visitForLoop(J.ForLoop forLoop, SenderContext ctx) {
            ctx.sendValue(forLoop, J.ForLoop::getId);
            ctx.sendNode(forLoop, J.ForLoop::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(forLoop, J.ForLoop::getMarkers, ctx::sendMarkers);
            ctx.sendNode(forLoop, J.ForLoop::getControl, ctx::sendTree);
            ctx.sendNode(forLoop, e -> e.getPadding().getBody(), PythonSender::sendRightPadded);
            return forLoop;
        }

        @Override
        public J.ForLoop.Control visitForControl(J.ForLoop.Control control, SenderContext ctx) {
            ctx.sendValue(control, J.ForLoop.Control::getId);
            ctx.sendNode(control, J.ForLoop.Control::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(control, J.ForLoop.Control::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(control, e -> e.getPadding().getInit(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            ctx.sendNode(control, e -> e.getPadding().getCondition(), PythonSender::sendRightPadded);
            ctx.sendNodes(control, e -> e.getPadding().getUpdate(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            return control;
        }

        @Override
        public J.ParenthesizedTypeTree visitParenthesizedTypeTree(J.ParenthesizedTypeTree parenthesizedTypeTree, SenderContext ctx) {
            ctx.sendValue(parenthesizedTypeTree, J.ParenthesizedTypeTree::getId);
            ctx.sendNode(parenthesizedTypeTree, J.ParenthesizedTypeTree::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(parenthesizedTypeTree, J.ParenthesizedTypeTree::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(parenthesizedTypeTree, J.ParenthesizedTypeTree::getAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNode(parenthesizedTypeTree, J.ParenthesizedTypeTree::getParenthesizedType, ctx::sendTree);
            return parenthesizedTypeTree;
        }

        @Override
        public J.Identifier visitIdentifier(J.Identifier identifier, SenderContext ctx) {
            ctx.sendValue(identifier, J.Identifier::getId);
            ctx.sendNode(identifier, J.Identifier::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(identifier, J.Identifier::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(identifier, J.Identifier::getAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendValue(identifier, J.Identifier::getSimpleName);
            ctx.sendTypedValue(identifier, J.Identifier::getType);
            ctx.sendTypedValue(identifier, J.Identifier::getFieldType);
            return identifier;
        }

        @Override
        public J.If visitIf(J.If if_, SenderContext ctx) {
            ctx.sendValue(if_, J.If::getId);
            ctx.sendNode(if_, J.If::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(if_, J.If::getMarkers, ctx::sendMarkers);
            ctx.sendNode(if_, J.If::getIfCondition, ctx::sendTree);
            ctx.sendNode(if_, e -> e.getPadding().getThenPart(), PythonSender::sendRightPadded);
            ctx.sendNode(if_, J.If::getElsePart, ctx::sendTree);
            return if_;
        }

        @Override
        public J.If.Else visitElse(J.If.Else else_, SenderContext ctx) {
            ctx.sendValue(else_, J.If.Else::getId);
            ctx.sendNode(else_, J.If.Else::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(else_, J.If.Else::getMarkers, ctx::sendMarkers);
            ctx.sendNode(else_, e -> e.getPadding().getBody(), PythonSender::sendRightPadded);
            return else_;
        }

        @Override
        public J.Import visitImport(J.Import import_, SenderContext ctx) {
            ctx.sendValue(import_, J.Import::getId);
            ctx.sendNode(import_, J.Import::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(import_, J.Import::getMarkers, ctx::sendMarkers);
            ctx.sendNode(import_, e -> e.getPadding().getStatic(), PythonSender::sendLeftPadded);
            ctx.sendNode(import_, J.Import::getQualid, ctx::sendTree);
            ctx.sendNode(import_, e -> e.getPadding().getAlias(), PythonSender::sendLeftPadded);
            return import_;
        }

        @Override
        public J.InstanceOf visitInstanceOf(J.InstanceOf instanceOf, SenderContext ctx) {
            ctx.sendValue(instanceOf, J.InstanceOf::getId);
            ctx.sendNode(instanceOf, J.InstanceOf::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(instanceOf, J.InstanceOf::getMarkers, ctx::sendMarkers);
            ctx.sendNode(instanceOf, e -> e.getPadding().getExpression(), PythonSender::sendRightPadded);
            ctx.sendNode(instanceOf, J.InstanceOf::getClazz, ctx::sendTree);
            ctx.sendNode(instanceOf, J.InstanceOf::getPattern, ctx::sendTree);
            ctx.sendTypedValue(instanceOf, J.InstanceOf::getType);
            return instanceOf;
        }

        @Override
        public J.IntersectionType visitIntersectionType(J.IntersectionType intersectionType, SenderContext ctx) {
            ctx.sendValue(intersectionType, J.IntersectionType::getId);
            ctx.sendNode(intersectionType, J.IntersectionType::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(intersectionType, J.IntersectionType::getMarkers, ctx::sendMarkers);
            ctx.sendNode(intersectionType, e -> e.getPadding().getBounds(), PythonSender::sendContainer);
            return intersectionType;
        }

        @Override
        public J.Label visitLabel(J.Label label, SenderContext ctx) {
            ctx.sendValue(label, J.Label::getId);
            ctx.sendNode(label, J.Label::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(label, J.Label::getMarkers, ctx::sendMarkers);
            ctx.sendNode(label, e -> e.getPadding().getLabel(), PythonSender::sendRightPadded);
            ctx.sendNode(label, J.Label::getStatement, ctx::sendTree);
            return label;
        }

        @Override
        public J.Lambda visitLambda(J.Lambda lambda, SenderContext ctx) {
            ctx.sendValue(lambda, J.Lambda::getId);
            ctx.sendNode(lambda, J.Lambda::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(lambda, J.Lambda::getMarkers, ctx::sendMarkers);
            ctx.sendNode(lambda, J.Lambda::getParameters, this::sendLambdaParameters);
            ctx.sendNode(lambda, J.Lambda::getArrow, PythonSender::sendSpace);
            ctx.sendNode(lambda, J.Lambda::getBody, ctx::sendTree);
            ctx.sendTypedValue(lambda, J.Lambda::getType);
            return lambda;
        }

        private void sendLambdaParameters(J.Lambda.Parameters parameters, SenderContext ctx) {
            ctx.sendValue(parameters, J.Lambda.Parameters::getId);
            ctx.sendNode(parameters, J.Lambda.Parameters::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(parameters, J.Lambda.Parameters::getMarkers, ctx::sendMarkers);
            ctx.sendValue(parameters, J.Lambda.Parameters::isParenthesized);
            ctx.sendNodes(parameters, e -> e.getPadding().getParameters(), PythonSender::sendRightPadded, e -> e.getElement().getId());
        }

        @Override
        public J.Literal visitLiteral(J.Literal literal, SenderContext ctx) {
            ctx.sendValue(literal, J.Literal::getId);
            ctx.sendNode(literal, J.Literal::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(literal, J.Literal::getMarkers, ctx::sendMarkers);
            ctx.sendTypedValue(literal, J.Literal::getValue);
            ctx.sendValue(literal, J.Literal::getValueSource);
            ctx.sendValues(literal, J.Literal::getUnicodeEscapes, Function.identity());
            ctx.sendValue(literal, J.Literal::getType);
            return literal;
        }

        @Override
        public J.MemberReference visitMemberReference(J.MemberReference memberReference, SenderContext ctx) {
            ctx.sendValue(memberReference, J.MemberReference::getId);
            ctx.sendNode(memberReference, J.MemberReference::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(memberReference, J.MemberReference::getMarkers, ctx::sendMarkers);
            ctx.sendNode(memberReference, e -> e.getPadding().getContaining(), PythonSender::sendRightPadded);
            ctx.sendNode(memberReference, e -> e.getPadding().getTypeParameters(), PythonSender::sendContainer);
            ctx.sendNode(memberReference, e -> e.getPadding().getReference(), PythonSender::sendLeftPadded);
            ctx.sendTypedValue(memberReference, J.MemberReference::getType);
            ctx.sendTypedValue(memberReference, J.MemberReference::getMethodType);
            ctx.sendTypedValue(memberReference, J.MemberReference::getVariableType);
            return memberReference;
        }

        @Override
        public J.MethodDeclaration visitMethodDeclaration(J.MethodDeclaration methodDeclaration, SenderContext ctx) {
            ctx.sendValue(methodDeclaration, J.MethodDeclaration::getId);
            ctx.sendNode(methodDeclaration, J.MethodDeclaration::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(methodDeclaration, J.MethodDeclaration::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(methodDeclaration, J.MethodDeclaration::getLeadingAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNodes(methodDeclaration, J.MethodDeclaration::getModifiers, this::sendModifier, Tree::getId);
            ctx.sendNode(methodDeclaration, e -> e.getAnnotations().getTypeParameters(), this::sendMethodTypeParameters);
            ctx.sendNode(methodDeclaration, J.MethodDeclaration::getReturnTypeExpression, ctx::sendTree);
            ctx.sendNode(methodDeclaration, e -> e.getAnnotations().getName(), this::sendMethodIdentifierWithAnnotations);
            ctx.sendNode(methodDeclaration, e -> e.getPadding().getParameters(), PythonSender::sendContainer);
            ctx.sendNode(methodDeclaration, e -> e.getPadding().getThrows(), PythonSender::sendContainer);
            ctx.sendNode(methodDeclaration, J.MethodDeclaration::getBody, ctx::sendTree);
            ctx.sendNode(methodDeclaration, e -> e.getPadding().getDefaultValue(), PythonSender::sendLeftPadded);
            ctx.sendTypedValue(methodDeclaration, J.MethodDeclaration::getMethodType);
            return methodDeclaration;
        }

        private void sendMethodIdentifierWithAnnotations(J.MethodDeclaration.IdentifierWithAnnotations identifierWithAnnotations, SenderContext ctx) {
            ctx.sendNode(identifierWithAnnotations, J.MethodDeclaration.IdentifierWithAnnotations::getIdentifier, ctx::sendTree);
            ctx.sendNodes(identifierWithAnnotations, J.MethodDeclaration.IdentifierWithAnnotations::getAnnotations, ctx::sendTree, Tree::getId);
        }

        @Override
        public J.MethodInvocation visitMethodInvocation(J.MethodInvocation methodInvocation, SenderContext ctx) {
            ctx.sendValue(methodInvocation, J.MethodInvocation::getId);
            ctx.sendNode(methodInvocation, J.MethodInvocation::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(methodInvocation, J.MethodInvocation::getMarkers, ctx::sendMarkers);
            ctx.sendNode(methodInvocation, e -> e.getPadding().getSelect(), PythonSender::sendRightPadded);
            ctx.sendNode(methodInvocation, e -> e.getPadding().getTypeParameters(), PythonSender::sendContainer);
            ctx.sendNode(methodInvocation, J.MethodInvocation::getName, ctx::sendTree);
            ctx.sendNode(methodInvocation, e -> e.getPadding().getArguments(), PythonSender::sendContainer);
            ctx.sendTypedValue(methodInvocation, J.MethodInvocation::getMethodType);
            return methodInvocation;
        }

        private void sendModifier(J.Modifier modifier, SenderContext ctx) {
            ctx.sendValue(modifier, J.Modifier::getId);
            ctx.sendNode(modifier, J.Modifier::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(modifier, J.Modifier::getMarkers, ctx::sendMarkers);
            ctx.sendValue(modifier, J.Modifier::getKeyword);
            ctx.sendValue(modifier, J.Modifier::getType);
            ctx.sendNodes(modifier, J.Modifier::getAnnotations, ctx::sendTree, Tree::getId);
        }

        @Override
        public J.MultiCatch visitMultiCatch(J.MultiCatch multiCatch, SenderContext ctx) {
            ctx.sendValue(multiCatch, J.MultiCatch::getId);
            ctx.sendNode(multiCatch, J.MultiCatch::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(multiCatch, J.MultiCatch::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(multiCatch, e -> e.getPadding().getAlternatives(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            return multiCatch;
        }

        @Override
        public J.NewArray visitNewArray(J.NewArray newArray, SenderContext ctx) {
            ctx.sendValue(newArray, J.NewArray::getId);
            ctx.sendNode(newArray, J.NewArray::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(newArray, J.NewArray::getMarkers, ctx::sendMarkers);
            ctx.sendNode(newArray, J.NewArray::getTypeExpression, ctx::sendTree);
            ctx.sendNodes(newArray, J.NewArray::getDimensions, ctx::sendTree, Tree::getId);
            ctx.sendNode(newArray, e -> e.getPadding().getInitializer(), PythonSender::sendContainer);
            ctx.sendTypedValue(newArray, J.NewArray::getType);
            return newArray;
        }

        @Override
        public J.ArrayDimension visitArrayDimension(J.ArrayDimension arrayDimension, SenderContext ctx) {
            ctx.sendValue(arrayDimension, J.ArrayDimension::getId);
            ctx.sendNode(arrayDimension, J.ArrayDimension::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(arrayDimension, J.ArrayDimension::getMarkers, ctx::sendMarkers);
            ctx.sendNode(arrayDimension, e -> e.getPadding().getIndex(), PythonSender::sendRightPadded);
            return arrayDimension;
        }

        @Override
        public J.NewClass visitNewClass(J.NewClass newClass, SenderContext ctx) {
            ctx.sendValue(newClass, J.NewClass::getId);
            ctx.sendNode(newClass, J.NewClass::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(newClass, J.NewClass::getMarkers, ctx::sendMarkers);
            ctx.sendNode(newClass, e -> e.getPadding().getEnclosing(), PythonSender::sendRightPadded);
            ctx.sendNode(newClass, J.NewClass::getNew, PythonSender::sendSpace);
            ctx.sendNode(newClass, J.NewClass::getClazz, ctx::sendTree);
            ctx.sendNode(newClass, e -> e.getPadding().getArguments(), PythonSender::sendContainer);
            ctx.sendNode(newClass, J.NewClass::getBody, ctx::sendTree);
            ctx.sendTypedValue(newClass, J.NewClass::getConstructorType);
            return newClass;
        }

        @Override
        public J.NullableType visitNullableType(J.NullableType nullableType, SenderContext ctx) {
            ctx.sendValue(nullableType, J.NullableType::getId);
            ctx.sendNode(nullableType, J.NullableType::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(nullableType, J.NullableType::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(nullableType, J.NullableType::getAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNode(nullableType, e -> e.getPadding().getTypeTree(), PythonSender::sendRightPadded);
            return nullableType;
        }

        @Override
        public J.Package visitPackage(J.Package package_, SenderContext ctx) {
            ctx.sendValue(package_, J.Package::getId);
            ctx.sendNode(package_, J.Package::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(package_, J.Package::getMarkers, ctx::sendMarkers);
            ctx.sendNode(package_, J.Package::getExpression, ctx::sendTree);
            ctx.sendNodes(package_, J.Package::getAnnotations, ctx::sendTree, Tree::getId);
            return package_;
        }

        @Override
        public J.ParameterizedType visitParameterizedType(J.ParameterizedType parameterizedType, SenderContext ctx) {
            ctx.sendValue(parameterizedType, J.ParameterizedType::getId);
            ctx.sendNode(parameterizedType, J.ParameterizedType::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(parameterizedType, J.ParameterizedType::getMarkers, ctx::sendMarkers);
            ctx.sendNode(parameterizedType, J.ParameterizedType::getClazz, ctx::sendTree);
            ctx.sendNode(parameterizedType, e -> e.getPadding().getTypeParameters(), PythonSender::sendContainer);
            ctx.sendTypedValue(parameterizedType, J.ParameterizedType::getType);
            return parameterizedType;
        }

        @Override
        public <J2 extends J> J.Parentheses<J2> visitParentheses(J.Parentheses<J2> parentheses, SenderContext ctx) {
            ctx.sendValue(parentheses, J.Parentheses::getId);
            ctx.sendNode(parentheses, J.Parentheses::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(parentheses, J.Parentheses::getMarkers, ctx::sendMarkers);
            ctx.sendNode(parentheses, e -> e.getPadding().getTree(), PythonSender::sendRightPadded);
            return parentheses;
        }

        @Override
        public <J2 extends J> J.ControlParentheses<J2> visitControlParentheses(J.ControlParentheses<J2> controlParentheses, SenderContext ctx) {
            ctx.sendValue(controlParentheses, J.ControlParentheses::getId);
            ctx.sendNode(controlParentheses, J.ControlParentheses::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(controlParentheses, J.ControlParentheses::getMarkers, ctx::sendMarkers);
            ctx.sendNode(controlParentheses, e -> e.getPadding().getTree(), PythonSender::sendRightPadded);
            return controlParentheses;
        }

        @Override
        public J.Primitive visitPrimitive(J.Primitive primitive, SenderContext ctx) {
            ctx.sendValue(primitive, J.Primitive::getId);
            ctx.sendNode(primitive, J.Primitive::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(primitive, J.Primitive::getMarkers, ctx::sendMarkers);
            ctx.sendValue(primitive, J.Primitive::getType);
            return primitive;
        }

        @Override
        public J.Return visitReturn(J.Return return_, SenderContext ctx) {
            ctx.sendValue(return_, J.Return::getId);
            ctx.sendNode(return_, J.Return::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(return_, J.Return::getMarkers, ctx::sendMarkers);
            ctx.sendNode(return_, J.Return::getExpression, ctx::sendTree);
            return return_;
        }

        @Override
        public J.Switch visitSwitch(J.Switch switch_, SenderContext ctx) {
            ctx.sendValue(switch_, J.Switch::getId);
            ctx.sendNode(switch_, J.Switch::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(switch_, J.Switch::getMarkers, ctx::sendMarkers);
            ctx.sendNode(switch_, J.Switch::getSelector, ctx::sendTree);
            ctx.sendNode(switch_, J.Switch::getCases, ctx::sendTree);
            return switch_;
        }

        @Override
        public J.SwitchExpression visitSwitchExpression(J.SwitchExpression switchExpression, SenderContext ctx) {
            ctx.sendValue(switchExpression, J.SwitchExpression::getId);
            ctx.sendNode(switchExpression, J.SwitchExpression::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(switchExpression, J.SwitchExpression::getMarkers, ctx::sendMarkers);
            ctx.sendNode(switchExpression, J.SwitchExpression::getSelector, ctx::sendTree);
            ctx.sendNode(switchExpression, J.SwitchExpression::getCases, ctx::sendTree);
            return switchExpression;
        }

        @Override
        public J.Synchronized visitSynchronized(J.Synchronized synchronized_, SenderContext ctx) {
            ctx.sendValue(synchronized_, J.Synchronized::getId);
            ctx.sendNode(synchronized_, J.Synchronized::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(synchronized_, J.Synchronized::getMarkers, ctx::sendMarkers);
            ctx.sendNode(synchronized_, J.Synchronized::getLock, ctx::sendTree);
            ctx.sendNode(synchronized_, J.Synchronized::getBody, ctx::sendTree);
            return synchronized_;
        }

        @Override
        public J.Ternary visitTernary(J.Ternary ternary, SenderContext ctx) {
            ctx.sendValue(ternary, J.Ternary::getId);
            ctx.sendNode(ternary, J.Ternary::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(ternary, J.Ternary::getMarkers, ctx::sendMarkers);
            ctx.sendNode(ternary, J.Ternary::getCondition, ctx::sendTree);
            ctx.sendNode(ternary, e -> e.getPadding().getTruePart(), PythonSender::sendLeftPadded);
            ctx.sendNode(ternary, e -> e.getPadding().getFalsePart(), PythonSender::sendLeftPadded);
            ctx.sendTypedValue(ternary, J.Ternary::getType);
            return ternary;
        }

        @Override
        public J.Throw visitThrow(J.Throw throw_, SenderContext ctx) {
            ctx.sendValue(throw_, J.Throw::getId);
            ctx.sendNode(throw_, J.Throw::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(throw_, J.Throw::getMarkers, ctx::sendMarkers);
            ctx.sendNode(throw_, J.Throw::getException, ctx::sendTree);
            return throw_;
        }

        @Override
        public J.Try visitTry(J.Try try_, SenderContext ctx) {
            ctx.sendValue(try_, J.Try::getId);
            ctx.sendNode(try_, J.Try::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(try_, J.Try::getMarkers, ctx::sendMarkers);
            ctx.sendNode(try_, e -> e.getPadding().getResources(), PythonSender::sendContainer);
            ctx.sendNode(try_, J.Try::getBody, ctx::sendTree);
            ctx.sendNodes(try_, J.Try::getCatches, ctx::sendTree, Tree::getId);
            ctx.sendNode(try_, e -> e.getPadding().getFinally(), PythonSender::sendLeftPadded);
            return try_;
        }

        @Override
        public J.Try.Resource visitTryResource(J.Try.Resource resource, SenderContext ctx) {
            ctx.sendValue(resource, J.Try.Resource::getId);
            ctx.sendNode(resource, J.Try.Resource::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(resource, J.Try.Resource::getMarkers, ctx::sendMarkers);
            ctx.sendNode(resource, J.Try.Resource::getVariableDeclarations, ctx::sendTree);
            ctx.sendValue(resource, J.Try.Resource::isTerminatedWithSemicolon);
            return resource;
        }

        @Override
        public J.Try.Catch visitCatch(J.Try.Catch catch_, SenderContext ctx) {
            ctx.sendValue(catch_, J.Try.Catch::getId);
            ctx.sendNode(catch_, J.Try.Catch::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(catch_, J.Try.Catch::getMarkers, ctx::sendMarkers);
            ctx.sendNode(catch_, J.Try.Catch::getParameter, ctx::sendTree);
            ctx.sendNode(catch_, J.Try.Catch::getBody, ctx::sendTree);
            return catch_;
        }

        @Override
        public J.TypeCast visitTypeCast(J.TypeCast typeCast, SenderContext ctx) {
            ctx.sendValue(typeCast, J.TypeCast::getId);
            ctx.sendNode(typeCast, J.TypeCast::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(typeCast, J.TypeCast::getMarkers, ctx::sendMarkers);
            ctx.sendNode(typeCast, J.TypeCast::getClazz, ctx::sendTree);
            ctx.sendNode(typeCast, J.TypeCast::getExpression, ctx::sendTree);
            return typeCast;
        }

        @Override
        public J.TypeParameter visitTypeParameter(J.TypeParameter typeParameter, SenderContext ctx) {
            ctx.sendValue(typeParameter, J.TypeParameter::getId);
            ctx.sendNode(typeParameter, J.TypeParameter::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(typeParameter, J.TypeParameter::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(typeParameter, J.TypeParameter::getAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNodes(typeParameter, J.TypeParameter::getModifiers, this::sendModifier, Tree::getId);
            ctx.sendNode(typeParameter, J.TypeParameter::getName, ctx::sendTree);
            ctx.sendNode(typeParameter, e -> e.getPadding().getBounds(), PythonSender::sendContainer);
            return typeParameter;
        }

        private void sendMethodTypeParameters(J.TypeParameters typeParameters, SenderContext ctx) {
            ctx.sendValue(typeParameters, J.TypeParameters::getId);
            ctx.sendNode(typeParameters, J.TypeParameters::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(typeParameters, J.TypeParameters::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(typeParameters, J.TypeParameters::getAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNodes(typeParameters, e -> e.getPadding().getTypeParameters(), PythonSender::sendRightPadded, e -> e.getElement().getId());
        }

        @Override
        public J.Unary visitUnary(J.Unary unary, SenderContext ctx) {
            ctx.sendValue(unary, J.Unary::getId);
            ctx.sendNode(unary, J.Unary::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(unary, J.Unary::getMarkers, ctx::sendMarkers);
            ctx.sendNode(unary, e -> e.getPadding().getOperator(), PythonSender::sendLeftPadded);
            ctx.sendNode(unary, J.Unary::getExpression, ctx::sendTree);
            ctx.sendTypedValue(unary, J.Unary::getType);
            return unary;
        }

        @Override
        public J.VariableDeclarations visitVariableDeclarations(J.VariableDeclarations variableDeclarations, SenderContext ctx) {
            ctx.sendValue(variableDeclarations, J.VariableDeclarations::getId);
            ctx.sendNode(variableDeclarations, J.VariableDeclarations::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(variableDeclarations, J.VariableDeclarations::getMarkers, ctx::sendMarkers);
            ctx.sendNodes(variableDeclarations, J.VariableDeclarations::getLeadingAnnotations, ctx::sendTree, Tree::getId);
            ctx.sendNodes(variableDeclarations, J.VariableDeclarations::getModifiers, this::sendModifier, Tree::getId);
            ctx.sendNode(variableDeclarations, J.VariableDeclarations::getTypeExpression, ctx::sendTree);
            ctx.sendNode(variableDeclarations, J.VariableDeclarations::getVarargs, PythonSender::sendSpace);
            ctx.sendNodes(variableDeclarations, J.VariableDeclarations::getDimensionsBeforeName, PythonSender::sendLeftPadded, Function.identity());
            ctx.sendNodes(variableDeclarations, e -> e.getPadding().getVariables(), PythonSender::sendRightPadded, e -> e.getElement().getId());
            return variableDeclarations;
        }

        @Override
        public J.VariableDeclarations.NamedVariable visitVariable(J.VariableDeclarations.NamedVariable namedVariable, SenderContext ctx) {
            ctx.sendValue(namedVariable, J.VariableDeclarations.NamedVariable::getId);
            ctx.sendNode(namedVariable, J.VariableDeclarations.NamedVariable::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(namedVariable, J.VariableDeclarations.NamedVariable::getMarkers, ctx::sendMarkers);
            ctx.sendNode(namedVariable, J.VariableDeclarations.NamedVariable::getName, ctx::sendTree);
            ctx.sendNodes(namedVariable, J.VariableDeclarations.NamedVariable::getDimensionsAfterName, PythonSender::sendLeftPadded, Function.identity());
            ctx.sendNode(namedVariable, e -> e.getPadding().getInitializer(), PythonSender::sendLeftPadded);
            ctx.sendTypedValue(namedVariable, J.VariableDeclarations.NamedVariable::getVariableType);
            return namedVariable;
        }

        @Override
        public J.WhileLoop visitWhileLoop(J.WhileLoop whileLoop, SenderContext ctx) {
            ctx.sendValue(whileLoop, J.WhileLoop::getId);
            ctx.sendNode(whileLoop, J.WhileLoop::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(whileLoop, J.WhileLoop::getMarkers, ctx::sendMarkers);
            ctx.sendNode(whileLoop, J.WhileLoop::getCondition, ctx::sendTree);
            ctx.sendNode(whileLoop, e -> e.getPadding().getBody(), PythonSender::sendRightPadded);
            return whileLoop;
        }

        @Override
        public J.Wildcard visitWildcard(J.Wildcard wildcard, SenderContext ctx) {
            ctx.sendValue(wildcard, J.Wildcard::getId);
            ctx.sendNode(wildcard, J.Wildcard::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(wildcard, J.Wildcard::getMarkers, ctx::sendMarkers);
            ctx.sendNode(wildcard, e -> e.getPadding().getBound(), PythonSender::sendLeftPadded);
            ctx.sendNode(wildcard, J.Wildcard::getBoundedType, ctx::sendTree);
            return wildcard;
        }

        @Override
        public J.Yield visitYield(J.Yield yield, SenderContext ctx) {
            ctx.sendValue(yield, J.Yield::getId);
            ctx.sendNode(yield, J.Yield::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(yield, J.Yield::getMarkers, ctx::sendMarkers);
            ctx.sendValue(yield, J.Yield::isImplicit);
            ctx.sendNode(yield, J.Yield::getValue, ctx::sendTree);
            return yield;
        }

        @Override
        public J.Unknown visitUnknown(J.Unknown unknown, SenderContext ctx) {
            ctx.sendValue(unknown, J.Unknown::getId);
            ctx.sendNode(unknown, J.Unknown::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(unknown, J.Unknown::getMarkers, ctx::sendMarkers);
            ctx.sendNode(unknown, J.Unknown::getSource, ctx::sendTree);
            return unknown;
        }

        @Override
        public J.Unknown.Source visitUnknownSource(J.Unknown.Source source, SenderContext ctx) {
            ctx.sendValue(source, J.Unknown.Source::getId);
            ctx.sendNode(source, J.Unknown.Source::getPrefix, PythonSender::sendSpace);
            ctx.sendNode(source, J.Unknown.Source::getMarkers, ctx::sendMarkers);
            ctx.sendValue(source, J.Unknown.Source::getText);
            return source;
        }

    }

    private static <T extends J> void sendContainer(JContainer<T> container, SenderContext ctx) {
        Extensions.sendContainer(container, ctx);
    }

    private static <T> void sendLeftPadded(JLeftPadded<T> leftPadded, SenderContext ctx) {
        Extensions.sendLeftPadded(leftPadded, ctx);
    }

    private static <T> void sendRightPadded(JRightPadded<T> rightPadded, SenderContext ctx) {
        Extensions.sendRightPadded(rightPadded, ctx);
    }

    private static void sendSpace(Space space, SenderContext ctx) {
        Extensions.sendSpace(space, ctx);
    }

    private static void sendComment(Comment comment, SenderContext ctx) {
        Extensions.sendComment(comment, ctx);
    }

}
