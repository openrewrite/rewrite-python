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

import org.jspecify.annotations.Nullable;
import org.openrewrite.*;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.marker.Markers;
import org.openrewrite.tree.*;
import org.openrewrite.java.JavaVisitor;
import org.openrewrite.java.tree.*;
import org.openrewrite.python.PythonIsoVisitor;
import org.openrewrite.python.tree.*;

import java.util.List;

class PythonValidator<P> extends PythonIsoVisitor<P> {

    private <T extends Tree> @Nullable T visitAndValidate(@Nullable T tree, Class<? extends Tree> expected, P p) {
        if (tree != null && !expected.isInstance(tree)) {
            throw new ClassCastException("Type " + tree.getClass() + " is not assignable to " + expected);
        }
        // noinspection unchecked
        return (T) visit(tree, p);
    }

    private <T extends Tree> @Nullable List<T> visitAndValidate(@Nullable List<@Nullable T> list, Class<? extends Tree> expected, P p) {
        return list == null ? null : ListUtils.map(list, e -> visitAndValidate(e, expected, p));
    }

    @Override
    public Py.Async visitAsync(Py.Async async, P p) {
        visitAndValidate(async.getStatement(), Statement.class, p);
        return async;
    }

    @Override
    public Py.Await visitAwait(Py.Await await, P p) {
        visitAndValidate(await.getExpression(), Expression.class, p);
        return await;
    }

    @Override
    public Py.Binary visitBinary(Py.Binary binary, P p) {
        visitAndValidate(binary.getLeft(), Expression.class, p);
        visitAndValidate(binary.getRight(), Expression.class, p);
        return binary;
    }

    @Override
    public Py.ChainedAssignment visitChainedAssignment(Py.ChainedAssignment chainedAssignment, P p) {
        ListUtils.map(chainedAssignment.getVariables(), el -> visitAndValidate(el, Expression.class, p));
        visitAndValidate(chainedAssignment.getAssignment(), Expression.class, p);
        return chainedAssignment;
    }

    @Override
    public Py.ExceptionType visitExceptionType(Py.ExceptionType exceptionType, P p) {
        visitAndValidate(exceptionType.getExpression(), Expression.class, p);
        return exceptionType;
    }

    @Override
    public Py.ForLoop visitForLoop(Py.ForLoop forLoop, P p) {
        visitAndValidate(forLoop.getTarget(), Expression.class, p);
        visitAndValidate(forLoop.getIterable(), Expression.class, p);
        visitAndValidate(forLoop.getBody(), Statement.class, p);
        return forLoop;
    }

    @Override
    public Py.LiteralType visitLiteralType(Py.LiteralType literalType, P p) {
        visitAndValidate(literalType.getLiteral(), Expression.class, p);
        return literalType;
    }

    @Override
    public Py.TypeHint visitTypeHint(Py.TypeHint typeHint, P p) {
        visitAndValidate(typeHint.getTypeTree(), Expression.class, p);
        return typeHint;
    }

    @Override
    public Py.CompilationUnit visitCompilationUnit(Py.CompilationUnit compilationUnit, P p) {
        ListUtils.map(compilationUnit.getImports(), el -> visitAndValidate(el, J.Import.class, p));
        ListUtils.map(compilationUnit.getStatements(), el -> visitAndValidate(el, Statement.class, p));
        return compilationUnit;
    }

    @Override
    public Py.ExpressionStatement visitExpressionStatement(Py.ExpressionStatement expressionStatement, P p) {
        visitAndValidate(expressionStatement.getExpression(), Expression.class, p);
        return expressionStatement;
    }

    @Override
    public Py.ExpressionTypeTree visitExpressionTypeTree(Py.ExpressionTypeTree expressionTypeTree, P p) {
        visitAndValidate(expressionTypeTree.getReference(), J.class, p);
        return expressionTypeTree;
    }

    @Override
    public Py.StatementExpression visitStatementExpression(Py.StatementExpression statementExpression, P p) {
        visitAndValidate(statementExpression.getStatement(), Statement.class, p);
        return statementExpression;
    }

    @Override
    public Py.MultiImport visitMultiImport(Py.MultiImport multiImport, P p) {
        visitAndValidate(multiImport.getFrom(), NameTree.class, p);
        visitAndValidate(multiImport.getNames(), J.Import.class, p);
        return multiImport;
    }

    @Override
    public Py.KeyValue visitKeyValue(Py.KeyValue keyValue, P p) {
        visitAndValidate(keyValue.getKey(), Expression.class, p);
        visitAndValidate(keyValue.getValue(), Expression.class, p);
        return keyValue;
    }

    @Override
    public Py.DictLiteral visitDictLiteral(Py.DictLiteral dictLiteral, P p) {
        visitAndValidate(dictLiteral.getElements(), Expression.class, p);
        return dictLiteral;
    }

    @Override
    public Py.CollectionLiteral visitCollectionLiteral(Py.CollectionLiteral collectionLiteral, P p) {
        visitAndValidate(collectionLiteral.getElements(), Expression.class, p);
        return collectionLiteral;
    }

    @Override
    public Py.FormattedString visitFormattedString(Py.FormattedString formattedString, P p) {
        ListUtils.map(formattedString.getParts(), el -> visitAndValidate(el, Expression.class, p));
        return formattedString;
    }

    @Override
    public Py.FormattedString.Value visitFormattedStringValue(Py.FormattedString.Value value, P p) {
        visitAndValidate(value.getExpression(), Expression.class, p);
        visitAndValidate(value.getFormat(), Expression.class, p);
        return value;
    }

    @Override
    public Py.Pass visitPass(Py.Pass pass, P p) {
        return pass;
    }

    @Override
    public Py.TrailingElseWrapper visitTrailingElseWrapper(Py.TrailingElseWrapper trailingElseWrapper, P p) {
        visitAndValidate(trailingElseWrapper.getStatement(), Statement.class, p);
        visitAndValidate(trailingElseWrapper.getElseBlock(), J.Block.class, p);
        return trailingElseWrapper;
    }

    @Override
    public Py.ComprehensionExpression visitComprehensionExpression(Py.ComprehensionExpression comprehensionExpression, P p) {
        visitAndValidate(comprehensionExpression.getResult(), Expression.class, p);
        ListUtils.map(comprehensionExpression.getClauses(), el -> visitAndValidate(el, Py.ComprehensionExpression.Clause.class, p));
        return comprehensionExpression;
    }

    @Override
    public Py.ComprehensionExpression.Condition visitComprehensionCondition(Py.ComprehensionExpression.Condition condition, P p) {
        visitAndValidate(condition.getExpression(), Expression.class, p);
        return condition;
    }

    @Override
    public Py.ComprehensionExpression.Clause visitComprehensionClause(Py.ComprehensionExpression.Clause clause, P p) {
        visitAndValidate(clause.getIteratorVariable(), Expression.class, p);
        visitAndValidate(clause.getIteratedList(), Expression.class, p);
        ListUtils.map(clause.getConditions(), el -> visitAndValidate(el, Py.ComprehensionExpression.Condition.class, p));
        return clause;
    }

    @Override
    public Py.TypeAlias visitTypeAlias(Py.TypeAlias typeAlias, P p) {
        visitAndValidate(typeAlias.getName(), J.Identifier.class, p);
        visitAndValidate(typeAlias.getValue(), J.class, p);
        return typeAlias;
    }

    @Override
    public Py.YieldFrom visitYieldFrom(Py.YieldFrom yieldFrom, P p) {
        visitAndValidate(yieldFrom.getExpression(), Expression.class, p);
        return yieldFrom;
    }

    @Override
    public Py.UnionType visitUnionType(Py.UnionType unionType, P p) {
        ListUtils.map(unionType.getTypes(), el -> visitAndValidate(el, Expression.class, p));
        return unionType;
    }

    @Override
    public Py.VariableScope visitVariableScope(Py.VariableScope variableScope, P p) {
        ListUtils.map(variableScope.getNames(), el -> visitAndValidate(el, J.Identifier.class, p));
        return variableScope;
    }

    @Override
    public Py.Del visitDel(Py.Del del, P p) {
        ListUtils.map(del.getTargets(), el -> visitAndValidate(el, Expression.class, p));
        return del;
    }

    @Override
    public Py.SpecialParameter visitSpecialParameter(Py.SpecialParameter specialParameter, P p) {
        visitAndValidate(specialParameter.getTypeHint(), Py.TypeHint.class, p);
        return specialParameter;
    }

    @Override
    public Py.Star visitStar(Py.Star star, P p) {
        visitAndValidate(star.getExpression(), Expression.class, p);
        return star;
    }

    @Override
    public Py.NamedArgument visitNamedArgument(Py.NamedArgument namedArgument, P p) {
        visitAndValidate(namedArgument.getName(), J.Identifier.class, p);
        visitAndValidate(namedArgument.getValue(), Expression.class, p);
        return namedArgument;
    }

    @Override
    public Py.TypeHintedExpression visitTypeHintedExpression(Py.TypeHintedExpression typeHintedExpression, P p) {
        visitAndValidate(typeHintedExpression.getExpression(), Expression.class, p);
        visitAndValidate(typeHintedExpression.getTypeHint(), Py.TypeHint.class, p);
        return typeHintedExpression;
    }

    @Override
    public Py.ErrorFrom visitErrorFrom(Py.ErrorFrom errorFrom, P p) {
        visitAndValidate(errorFrom.getError(), Expression.class, p);
        visitAndValidate(errorFrom.getFrom(), Expression.class, p);
        return errorFrom;
    }

    @Override
    public Py.MatchCase visitMatchCase(Py.MatchCase matchCase, P p) {
        visitAndValidate(matchCase.getPattern(), Py.MatchCase.Pattern.class, p);
        visitAndValidate(matchCase.getGuard(), Expression.class, p);
        return matchCase;
    }

    @Override
    public Py.MatchCase.Pattern visitMatchCasePattern(Py.MatchCase.Pattern pattern, P p) {
        visitAndValidate(pattern.getChildren(), Expression.class, p);
        return pattern;
    }

    @Override
    public Py.Slice visitSlice(Py.Slice slice, P p) {
        visitAndValidate(slice.getStart(), Expression.class, p);
        visitAndValidate(slice.getStop(), Expression.class, p);
        visitAndValidate(slice.getStep(), Expression.class, p);
        return slice;
    }

    @Override
    public J.AnnotatedType visitAnnotatedType(J.AnnotatedType annotatedType, P p) {
        ListUtils.map(annotatedType.getAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        visitAndValidate(annotatedType.getTypeExpression(), TypeTree.class, p);
        return annotatedType;
    }

    @Override
    public J.Annotation visitAnnotation(J.Annotation annotation, P p) {
        visitAndValidate(annotation.getAnnotationType(), NameTree.class, p);
        visitAndValidate(annotation.getArguments(), Expression.class, p);
        return annotation;
    }

    @Override
    public J.ArrayAccess visitArrayAccess(J.ArrayAccess arrayAccess, P p) {
        visitAndValidate(arrayAccess.getIndexed(), Expression.class, p);
        visitAndValidate(arrayAccess.getDimension(), J.ArrayDimension.class, p);
        return arrayAccess;
    }

    @Override
    public J.ArrayType visitArrayType(J.ArrayType arrayType, P p) {
        visitAndValidate(arrayType.getElementType(), TypeTree.class, p);
        ListUtils.map(arrayType.getAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        return arrayType;
    }

    @Override
    public J.Assert visitAssert(J.Assert assert_, P p) {
        visitAndValidate(assert_.getCondition(), Expression.class, p);
        visitAndValidate(assert_.getDetail() != null ? assert_.getDetail().getElement() : null, Expression.class, p);
        return assert_;
    }

    @Override
    public J.Assignment visitAssignment(J.Assignment assignment, P p) {
        visitAndValidate(assignment.getVariable(), Expression.class, p);
        visitAndValidate(assignment.getAssignment(), Expression.class, p);
        return assignment;
    }

    @Override
    public J.AssignmentOperation visitAssignmentOperation(J.AssignmentOperation assignmentOperation, P p) {
        visitAndValidate(assignmentOperation.getVariable(), Expression.class, p);
        visitAndValidate(assignmentOperation.getAssignment(), Expression.class, p);
        return assignmentOperation;
    }

    @Override
    public J.Binary visitBinary(J.Binary binary, P p) {
        visitAndValidate(binary.getLeft(), Expression.class, p);
        visitAndValidate(binary.getRight(), Expression.class, p);
        return binary;
    }

    @Override
    public J.Block visitBlock(J.Block block, P p) {
        ListUtils.map(block.getStatements(), el -> visitAndValidate(el, Statement.class, p));
        return block;
    }

    @Override
    public J.Break visitBreak(J.Break break_, P p) {
        visitAndValidate(break_.getLabel(), J.Identifier.class, p);
        return break_;
    }

    @Override
    public J.Case visitCase(J.Case case_, P p) {
        visitAndValidate(case_.getExpressions(), Expression.class, p);
        visitAndValidate(case_.getStatements(), Statement.class, p);
        visitAndValidate(case_.getBody(), J.class, p);
        return case_;
    }

    @Override
    public J.ClassDeclaration visitClassDeclaration(J.ClassDeclaration classDeclaration, P p) {
        ListUtils.map(classDeclaration.getLeadingAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        ListUtils.map(classDeclaration.getModifiers(), el -> visitAndValidate(el, J.Modifier.class, p));
        visit(classDeclaration.getPadding().getKind(), p);
        visitAndValidate(classDeclaration.getName(), J.Identifier.class, p);
        visitAndValidate(classDeclaration.getTypeParameters(), J.TypeParameter.class, p);
        visitAndValidate(classDeclaration.getPrimaryConstructor(), Statement.class, p);
        visitAndValidate(classDeclaration.getExtends(), TypeTree.class, p);
        visitAndValidate(classDeclaration.getImplements(), TypeTree.class, p);
        visitAndValidate(classDeclaration.getPermits(), TypeTree.class, p);
        visitAndValidate(classDeclaration.getBody(), J.Block.class, p);
        return classDeclaration;
    }

    @Override
    public J.Continue visitContinue(J.Continue continue_, P p) {
        visitAndValidate(continue_.getLabel(), J.Identifier.class, p);
        return continue_;
    }

    @Override
    public J.DoWhileLoop visitDoWhileLoop(J.DoWhileLoop doWhileLoop, P p) {
        visitAndValidate(doWhileLoop.getBody(), Statement.class, p);
        visitAndValidate(doWhileLoop.getWhileCondition(), Expression.class, p);
        return doWhileLoop;
    }

    @Override
    public J.Empty visitEmpty(J.Empty empty, P p) {
        return empty;
    }

    @Override
    public J.EnumValue visitEnumValue(J.EnumValue enumValue, P p) {
        ListUtils.map(enumValue.getAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        visitAndValidate(enumValue.getName(), J.Identifier.class, p);
        visitAndValidate(enumValue.getInitializer(), J.NewClass.class, p);
        return enumValue;
    }

    @Override
    public J.EnumValueSet visitEnumValueSet(J.EnumValueSet enumValueSet, P p) {
        ListUtils.map(enumValueSet.getEnums(), el -> visitAndValidate(el, J.EnumValue.class, p));
        return enumValueSet;
    }

    @Override
    public J.FieldAccess visitFieldAccess(J.FieldAccess fieldAccess, P p) {
        visitAndValidate(fieldAccess.getTarget(), Expression.class, p);
        visitAndValidate(fieldAccess.getName(), J.Identifier.class, p);
        return fieldAccess;
    }

    @Override
    public J.ForEachLoop visitForEachLoop(J.ForEachLoop forEachLoop, P p) {
        visitAndValidate(forEachLoop.getControl(), J.ForEachLoop.Control.class, p);
        visitAndValidate(forEachLoop.getBody(), Statement.class, p);
        return forEachLoop;
    }

    @Override
    public J.ForEachLoop.Control visitForEachControl(J.ForEachLoop.Control control, P p) {
        visitAndValidate(control.getVariable(), J.VariableDeclarations.class, p);
        visitAndValidate(control.getIterable(), Expression.class, p);
        return control;
    }

    @Override
    public J.ForLoop visitForLoop(J.ForLoop forLoop, P p) {
        visitAndValidate(forLoop.getControl(), J.ForLoop.Control.class, p);
        visitAndValidate(forLoop.getBody(), Statement.class, p);
        return forLoop;
    }

    @Override
    public J.ForLoop.Control visitForControl(J.ForLoop.Control control, P p) {
        ListUtils.map(control.getInit(), el -> visitAndValidate(el, Statement.class, p));
        visitAndValidate(control.getCondition(), Expression.class, p);
        ListUtils.map(control.getUpdate(), el -> visitAndValidate(el, Statement.class, p));
        return control;
    }

    @Override
    public J.ParenthesizedTypeTree visitParenthesizedTypeTree(J.ParenthesizedTypeTree parenthesizedTypeTree, P p) {
        ListUtils.map(parenthesizedTypeTree.getAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        visitAndValidate(parenthesizedTypeTree.getParenthesizedType(), J.Parentheses.class, p);
        return parenthesizedTypeTree;
    }

    @Override
    public J.Identifier visitIdentifier(J.Identifier identifier, P p) {
        ListUtils.map(identifier.getAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        return identifier;
    }

    @Override
    public J.If visitIf(J.If if_, P p) {
        visitAndValidate(if_.getIfCondition(), J.ControlParentheses.class, p);
        visitAndValidate(if_.getThenPart(), Statement.class, p);
        visitAndValidate(if_.getElsePart(), J.If.Else.class, p);
        return if_;
    }

    @Override
    public J.If.Else visitElse(J.If.Else else_, P p) {
        visitAndValidate(else_.getBody(), Statement.class, p);
        return else_;
    }

    @Override
    public J.Import visitImport(J.Import import_, P p) {
        visitAndValidate(import_.getQualid(), J.FieldAccess.class, p);
        visitAndValidate(import_.getAlias(), J.Identifier.class, p);
        return import_;
    }

    @Override
    public J.InstanceOf visitInstanceOf(J.InstanceOf instanceOf, P p) {
        visitAndValidate(instanceOf.getExpression(), Expression.class, p);
        visitAndValidate(instanceOf.getClazz(), J.class, p);
        visitAndValidate(instanceOf.getPattern(), J.class, p);
        return instanceOf;
    }

    @Override
    public J.IntersectionType visitIntersectionType(J.IntersectionType intersectionType, P p) {
        visitAndValidate(intersectionType.getBounds(), TypeTree.class, p);
        return intersectionType;
    }

    @Override
    public J.Label visitLabel(J.Label label, P p) {
        visitAndValidate(label.getLabel(), J.Identifier.class, p);
        visitAndValidate(label.getStatement(), Statement.class, p);
        return label;
    }

    @Override
    public J.Lambda visitLambda(J.Lambda lambda, P p) {
        visitAndValidate(lambda.getParameters(), J.Lambda.Parameters.class, p);
        visitAndValidate(lambda.getBody(), J.class, p);
        return lambda;
    }

    @Override
    public J.Literal visitLiteral(J.Literal literal, P p) {
        return literal;
    }

    @Override
    public J.MemberReference visitMemberReference(J.MemberReference memberReference, P p) {
        visitAndValidate(memberReference.getContaining(), Expression.class, p);
        visitAndValidate(memberReference.getTypeParameters(), Expression.class, p);
        visitAndValidate(memberReference.getReference(), J.Identifier.class, p);
        return memberReference;
    }

    @Override
    public J.MethodDeclaration visitMethodDeclaration(J.MethodDeclaration methodDeclaration, P p) {
        ListUtils.map(methodDeclaration.getLeadingAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        ListUtils.map(methodDeclaration.getModifiers(), el -> visitAndValidate(el, J.Modifier.class, p));
        visitAndValidate(methodDeclaration.getPadding().getTypeParameters(), J.TypeParameters.class, p);
        visitAndValidate(methodDeclaration.getReturnTypeExpression(), TypeTree.class, p);
        visitAndValidate(methodDeclaration.getParameters(), Statement.class, p);
        visitAndValidate(methodDeclaration.getThrows(), NameTree.class, p);
        visitAndValidate(methodDeclaration.getBody(), J.Block.class, p);
        visitAndValidate(methodDeclaration.getDefaultValue(), Expression.class, p);
        return methodDeclaration;
    }

    @Override
    public J.MethodInvocation visitMethodInvocation(J.MethodInvocation methodInvocation, P p) {
        visitAndValidate(methodInvocation.getSelect(), Expression.class, p);
        visitAndValidate(methodInvocation.getTypeParameters(), Expression.class, p);
        visitAndValidate(methodInvocation.getName(), J.Identifier.class, p);
        visitAndValidate(methodInvocation.getArguments(), Expression.class, p);
        return methodInvocation;
    }

    @Override
    public J.MultiCatch visitMultiCatch(J.MultiCatch multiCatch, P p) {
        ListUtils.map(multiCatch.getAlternatives(), el -> visitAndValidate(el, NameTree.class, p));
        return multiCatch;
    }

    @Override
    public J.NewArray visitNewArray(J.NewArray newArray, P p) {
        visitAndValidate(newArray.getTypeExpression(), TypeTree.class, p);
        ListUtils.map(newArray.getDimensions(), el -> visitAndValidate(el, J.ArrayDimension.class, p));
        visitAndValidate(newArray.getInitializer(), Expression.class, p);
        return newArray;
    }

    @Override
    public J.ArrayDimension visitArrayDimension(J.ArrayDimension arrayDimension, P p) {
        visitAndValidate(arrayDimension.getIndex(), Expression.class, p);
        return arrayDimension;
    }

    @Override
    public J.NewClass visitNewClass(J.NewClass newClass, P p) {
        visitAndValidate(newClass.getEnclosing(), Expression.class, p);
        visitAndValidate(newClass.getClazz(), TypeTree.class, p);
        visitAndValidate(newClass.getArguments(), Expression.class, p);
        visitAndValidate(newClass.getBody(), J.Block.class, p);
        return newClass;
    }

    @Override
    public J.NullableType visitNullableType(J.NullableType nullableType, P p) {
        ListUtils.map(nullableType.getAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        visitAndValidate(nullableType.getTypeTree(), TypeTree.class, p);
        return nullableType;
    }

    @Override
    public J.Package visitPackage(J.Package package_, P p) {
        visitAndValidate(package_.getExpression(), Expression.class, p);
        ListUtils.map(package_.getAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        return package_;
    }

    @Override
    public J.ParameterizedType visitParameterizedType(J.ParameterizedType parameterizedType, P p) {
        visitAndValidate(parameterizedType.getClazz(), NameTree.class, p);
        visitAndValidate(parameterizedType.getTypeParameters(), Expression.class, p);
        return parameterizedType;
    }

    @Override
    public <J2 extends J> J.Parentheses<J2> visitParentheses(J.Parentheses<J2> parentheses, P p) {
        visitAndValidate(parentheses.getTree(), J.class, p);
        return parentheses;
    }

    @Override
    public <J2 extends J> J.ControlParentheses<J2> visitControlParentheses(J.ControlParentheses<J2> controlParentheses, P p) {
        visitAndValidate(controlParentheses.getTree(), J.class, p);
        return controlParentheses;
    }

    @Override
    public J.Primitive visitPrimitive(J.Primitive primitive, P p) {
        return primitive;
    }

    @Override
    public J.Return visitReturn(J.Return return_, P p) {
        visitAndValidate(return_.getExpression(), Expression.class, p);
        return return_;
    }

    @Override
    public J.Switch visitSwitch(J.Switch switch_, P p) {
        visitAndValidate(switch_.getSelector(), J.ControlParentheses.class, p);
        visitAndValidate(switch_.getCases(), J.Block.class, p);
        return switch_;
    }

    @Override
    public J.SwitchExpression visitSwitchExpression(J.SwitchExpression switchExpression, P p) {
        visitAndValidate(switchExpression.getSelector(), J.ControlParentheses.class, p);
        visitAndValidate(switchExpression.getCases(), J.Block.class, p);
        return switchExpression;
    }

    @Override
    public J.Synchronized visitSynchronized(J.Synchronized synchronized_, P p) {
        visitAndValidate(synchronized_.getLock(), J.ControlParentheses.class, p);
        visitAndValidate(synchronized_.getBody(), J.Block.class, p);
        return synchronized_;
    }

    @Override
    public J.Ternary visitTernary(J.Ternary ternary, P p) {
        visitAndValidate(ternary.getCondition(), Expression.class, p);
        visitAndValidate(ternary.getTruePart(), Expression.class, p);
        visitAndValidate(ternary.getFalsePart(), Expression.class, p);
        return ternary;
    }

    @Override
    public J.Throw visitThrow(J.Throw throw_, P p) {
        visitAndValidate(throw_.getException(), Expression.class, p);
        return throw_;
    }

    @Override
    public J.Try visitTry(J.Try try_, P p) {
        visitAndValidate(try_.getResources(), J.Try.Resource.class, p);
        visitAndValidate(try_.getBody(), J.Block.class, p);
        ListUtils.map(try_.getCatches(), el -> visitAndValidate(el, J.Try.Catch.class, p));
        visitAndValidate(try_.getFinally(), J.Block.class, p);
        return try_;
    }

    @Override
    public J.Try.Resource visitTryResource(J.Try.Resource resource, P p) {
        visitAndValidate(resource.getVariableDeclarations(), TypedTree.class, p);
        return resource;
    }

    @Override
    public J.Try.Catch visitCatch(J.Try.Catch catch_, P p) {
        visitAndValidate(catch_.getParameter(), J.ControlParentheses.class, p);
        visitAndValidate(catch_.getBody(), J.Block.class, p);
        return catch_;
    }

    @Override
    public J.TypeCast visitTypeCast(J.TypeCast typeCast, P p) {
        visitAndValidate(typeCast.getClazz(), J.ControlParentheses.class, p);
        visitAndValidate(typeCast.getExpression(), Expression.class, p);
        return typeCast;
    }

    @Override
    public J.TypeParameter visitTypeParameter(J.TypeParameter typeParameter, P p) {
        ListUtils.map(typeParameter.getAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        ListUtils.map(typeParameter.getModifiers(), el -> visitAndValidate(el, J.Modifier.class, p));
        visitAndValidate(typeParameter.getName(), Expression.class, p);
        visitAndValidate(typeParameter.getBounds(), TypeTree.class, p);
        return typeParameter;
    }

    @Override
    public J.Unary visitUnary(J.Unary unary, P p) {
        visitAndValidate(unary.getExpression(), Expression.class, p);
        return unary;
    }

    @Override
    public J.VariableDeclarations visitVariableDeclarations(J.VariableDeclarations variableDeclarations, P p) {
        ListUtils.map(variableDeclarations.getLeadingAnnotations(), el -> visitAndValidate(el, J.Annotation.class, p));
        ListUtils.map(variableDeclarations.getModifiers(), el -> visitAndValidate(el, J.Modifier.class, p));
        visitAndValidate(variableDeclarations.getTypeExpression(), TypeTree.class, p);
        ListUtils.map(variableDeclarations.getVariables(), el -> visitAndValidate(el, J.VariableDeclarations.NamedVariable.class, p));
        return variableDeclarations;
    }

    @Override
    public J.VariableDeclarations.NamedVariable visitVariable(J.VariableDeclarations.NamedVariable namedVariable, P p) {
        visitAndValidate(namedVariable.getName(), J.Identifier.class, p);
        visitAndValidate(namedVariable.getInitializer(), Expression.class, p);
        return namedVariable;
    }

    @Override
    public J.WhileLoop visitWhileLoop(J.WhileLoop whileLoop, P p) {
        visitAndValidate(whileLoop.getCondition(), J.ControlParentheses.class, p);
        visitAndValidate(whileLoop.getBody(), Statement.class, p);
        return whileLoop;
    }

    @Override
    public J.Wildcard visitWildcard(J.Wildcard wildcard, P p) {
        visitAndValidate(wildcard.getBoundedType(), NameTree.class, p);
        return wildcard;
    }

    @Override
    public J.Yield visitYield(J.Yield yield, P p) {
        visitAndValidate(yield.getValue(), Expression.class, p);
        return yield;
    }

    @Override
    public J.Unknown visitUnknown(J.Unknown unknown, P p) {
        visitAndValidate(unknown.getSource(), J.Unknown.Source.class, p);
        return unknown;
    }

    @Override
    public J.Unknown.Source visitUnknownSource(J.Unknown.Source source, P p) {
        return source;
    }

}