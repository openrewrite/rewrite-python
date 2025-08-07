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

/*
 * -------------------THIS FILE IS AUTO GENERATED--------------------------
 * Changes to this file may cause incorrect behavior and will be lost if
 * the code is regenerated.
*/

package org.openrewrite.python.remote;

import org.jspecify.annotations.Nullable;
import org.openrewrite.Tree;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.java.tree.*;
import org.openrewrite.python.PythonIsoVisitor;
import org.openrewrite.python.tree.Py;

import java.util.List;
import java.util.Objects;

class PythonValidator<P> extends PythonIsoVisitor<P> {

    private <T extends Tree> @Nullable T visitAndValidate(@Nullable T tree, Class<? extends Tree> expected, P p) {
        if (tree != null && !expected.isInstance(tree)) {
            throw new ClassCastException("Type " + tree.getClass() + " is not assignable to " + expected);
        }
        // noinspection unchecked
        return (T) visit(tree, p);
    }

    private <T extends Tree> T visitAndValidateNonNull(@Nullable T tree, Class<? extends Tree> expected, P p) {
        Objects.requireNonNull(tree);
        if (!expected.isInstance(tree)) {
            throw new ClassCastException("Type " + tree.getClass() + " is not assignable to " + expected);
        }
        // noinspection unchecked
        return (T) visitNonNull(tree, p);
    }

    private <T extends Tree> @Nullable List<T> visitAndValidate(@Nullable List<T> list, Class<? extends Tree> expected, P p) {
        return list == null ? null : ListUtils.map(list, e -> visitAndValidateNonNull(e, expected, p));
    }

    @Override
    public Py.Async visitAsync(Py.Async async, P p) {
        visitAndValidateNonNull(async.getStatement(), Statement.class, p);
        return async;
    }

    @Override
    public Py.Await visitAwait(Py.Await await, P p) {
        visitAndValidateNonNull(await.getExpression(), Expression.class, p);
        return await;
    }

    @Override
    public Py.Binary visitBinary(Py.Binary binary, P p) {
        visitAndValidateNonNull(binary.getLeft(), Expression.class, p);
        visitAndValidateNonNull(binary.getRight(), Expression.class, p);
        return binary;
    }

    @Override
    public Py.ChainedAssignment visitChainedAssignment(Py.ChainedAssignment chainedAssignment, P p) {
        ListUtils.map(chainedAssignment.getVariables(), el -> visitAndValidateNonNull(el, Expression.class, p));
        visitAndValidateNonNull(chainedAssignment.getAssignment(), Expression.class, p);
        return chainedAssignment;
    }

    @Override
    public Py.ExceptionType visitExceptionType(Py.ExceptionType exceptionType, P p) {
        visitAndValidateNonNull(exceptionType.getExpression(), Expression.class, p);
        return exceptionType;
    }

    @Override
    public Py.ForLoop visitForLoop(Py.ForLoop forLoop, P p) {
        visitAndValidateNonNull(forLoop.getTarget(), Expression.class, p);
        visitAndValidateNonNull(forLoop.getIterable(), Expression.class, p);
        visitAndValidateNonNull(forLoop.getBody(), Statement.class, p);
        return forLoop;
    }

    @Override
    public Py.LiteralType visitLiteralType(Py.LiteralType literalType, P p) {
        visitAndValidateNonNull(literalType.getLiteral(), Expression.class, p);
        return literalType;
    }

    @Override
    public Py.TypeHint visitTypeHint(Py.TypeHint typeHint, P p) {
        visitAndValidateNonNull(typeHint.getTypeTree(), Expression.class, p);
        return typeHint;
    }

    @Override
    public Py.CompilationUnit visitCompilationUnit(Py.CompilationUnit compilationUnit, P p) {
        ListUtils.map(compilationUnit.getImports(), el -> visitAndValidateNonNull(el, J.Import.class, p));
        ListUtils.map(compilationUnit.getStatements(), el -> visitAndValidateNonNull(el, Statement.class, p));
        return compilationUnit;
    }

    @Override
    public Py.ExpressionStatement visitExpressionStatement(Py.ExpressionStatement expressionStatement, P p) {
        visitAndValidateNonNull(expressionStatement.getExpression(), Expression.class, p);
        return expressionStatement;
    }

    @Override
    public Py.ExpressionTypeTree visitExpressionTypeTree(Py.ExpressionTypeTree expressionTypeTree, P p) {
        visitAndValidateNonNull(expressionTypeTree.getReference(), J.class, p);
        return expressionTypeTree;
    }

    @Override
    public Py.StatementExpression visitStatementExpression(Py.StatementExpression statementExpression, P p) {
        visitAndValidateNonNull(statementExpression.getStatement(), Statement.class, p);
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
        visitAndValidateNonNull(keyValue.getKey(), Expression.class, p);
        visitAndValidateNonNull(keyValue.getValue(), Expression.class, p);
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
        ListUtils.map(formattedString.getParts(), el -> visitAndValidateNonNull(el, Expression.class, p));
        return formattedString;
    }

    @Override
    public Py.FormattedString.Value visitFormattedStringValue(Py.FormattedString.Value value, P p) {
        visitAndValidateNonNull(value.getExpression(), Expression.class, p);
        visitAndValidate(value.getFormat(), Expression.class, p);
        return value;
    }

    @Override
    public Py.Pass visitPass(Py.Pass pass, P p) {
        return pass;
    }

    @Override
    public Py.TrailingElseWrapper visitTrailingElseWrapper(Py.TrailingElseWrapper trailingElseWrapper, P p) {
        visitAndValidateNonNull(trailingElseWrapper.getStatement(), Statement.class, p);
        visitAndValidateNonNull(trailingElseWrapper.getElseBlock(), J.Block.class, p);
        return trailingElseWrapper;
    }

    @Override
    public Py.ComprehensionExpression visitComprehensionExpression(Py.ComprehensionExpression comprehensionExpression, P p) {
        visitAndValidateNonNull(comprehensionExpression.getResult(), Expression.class, p);
        ListUtils.map(comprehensionExpression.getClauses(), el -> visitAndValidateNonNull(el, Py.ComprehensionExpression.Clause.class, p));
        return comprehensionExpression;
    }

    @Override
    public Py.ComprehensionExpression.Condition visitComprehensionCondition(Py.ComprehensionExpression.Condition condition, P p) {
        visitAndValidateNonNull(condition.getExpression(), Expression.class, p);
        return condition;
    }

    @Override
    public Py.ComprehensionExpression.Clause visitComprehensionClause(Py.ComprehensionExpression.Clause clause, P p) {
        visitAndValidateNonNull(clause.getIteratorVariable(), Expression.class, p);
        visitAndValidateNonNull(clause.getIteratedList(), Expression.class, p);
        ListUtils.map(clause.getConditions(), el -> visitAndValidateNonNull(el, Py.ComprehensionExpression.Condition.class, p));
        return clause;
    }

    @Override
    public Py.TypeAlias visitTypeAlias(Py.TypeAlias typeAlias, P p) {
        visitAndValidateNonNull(typeAlias.getName(), J.Identifier.class, p);
        visitAndValidateNonNull(typeAlias.getValue(), J.class, p);
        return typeAlias;
    }

    @Override
    public Py.YieldFrom visitYieldFrom(Py.YieldFrom yieldFrom, P p) {
        visitAndValidateNonNull(yieldFrom.getExpression(), Expression.class, p);
        return yieldFrom;
    }

    @Override
    public Py.UnionType visitUnionType(Py.UnionType unionType, P p) {
        ListUtils.map(unionType.getTypes(), el -> visitAndValidateNonNull(el, Expression.class, p));
        return unionType;
    }

    @Override
    public Py.VariableScope visitVariableScope(Py.VariableScope variableScope, P p) {
        ListUtils.map(variableScope.getNames(), el -> visitAndValidateNonNull(el, J.Identifier.class, p));
        return variableScope;
    }

    @Override
    public Py.Del visitDel(Py.Del del, P p) {
        ListUtils.map(del.getTargets(), el -> visitAndValidateNonNull(el, Expression.class, p));
        return del;
    }

    @Override
    public Py.SpecialParameter visitSpecialParameter(Py.SpecialParameter specialParameter, P p) {
        visitAndValidate(specialParameter.getTypeHint(), Py.TypeHint.class, p);
        return specialParameter;
    }

    @Override
    public Py.Star visitStar(Py.Star star, P p) {
        visitAndValidateNonNull(star.getExpression(), Expression.class, p);
        return star;
    }

    @Override
    public Py.NamedArgument visitNamedArgument(Py.NamedArgument namedArgument, P p) {
        visitAndValidateNonNull(namedArgument.getName(), J.Identifier.class, p);
        visitAndValidateNonNull(namedArgument.getValue(), Expression.class, p);
        return namedArgument;
    }

    @Override
    public Py.TypeHintedExpression visitTypeHintedExpression(Py.TypeHintedExpression typeHintedExpression, P p) {
        visitAndValidateNonNull(typeHintedExpression.getExpression(), Expression.class, p);
        visitAndValidateNonNull(typeHintedExpression.getTypeHint(), Py.TypeHint.class, p);
        return typeHintedExpression;
    }

    @Override
    public Py.ErrorFrom visitErrorFrom(Py.ErrorFrom errorFrom, P p) {
        visitAndValidateNonNull(errorFrom.getError(), Expression.class, p);
        visitAndValidateNonNull(errorFrom.getFrom(), Expression.class, p);
        return errorFrom;
    }

    @Override
    public Py.MatchCase visitMatchCase(Py.MatchCase matchCase, P p) {
        visitAndValidateNonNull(matchCase.getPattern(), Py.MatchCase.Pattern.class, p);
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
        ListUtils.map(annotatedType.getAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        visitAndValidateNonNull(annotatedType.getTypeExpression(), TypeTree.class, p);
        return annotatedType;
    }

    @Override
    public J.Annotation visitAnnotation(J.Annotation annotation, P p) {
        visitAndValidateNonNull(annotation.getAnnotationType(), NameTree.class, p);
        visitAndValidate(annotation.getArguments(), Expression.class, p);
        return annotation;
    }

    @Override
    public J.ArrayAccess visitArrayAccess(J.ArrayAccess arrayAccess, P p) {
        visitAndValidateNonNull(arrayAccess.getIndexed(), Expression.class, p);
        visitAndValidateNonNull(arrayAccess.getDimension(), J.ArrayDimension.class, p);
        return arrayAccess;
    }

    @Override
    public J.ArrayType visitArrayType(J.ArrayType arrayType, P p) {
        visitAndValidateNonNull(arrayType.getElementType(), TypeTree.class, p);
        ListUtils.map(arrayType.getAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        return arrayType;
    }

    @Override
    public J.Assert visitAssert(J.Assert assert_, P p) {
        visitAndValidateNonNull(assert_.getCondition(), Expression.class, p);
        visitAndValidate(assert_.getDetail() != null ? assert_.getDetail().getElement() : null, Expression.class, p);
        return assert_;
    }

    @Override
    public J.Assignment visitAssignment(J.Assignment assignment, P p) {
        visitAndValidateNonNull(assignment.getVariable(), Expression.class, p);
        visitAndValidateNonNull(assignment.getAssignment(), Expression.class, p);
        return assignment;
    }

    @Override
    public J.AssignmentOperation visitAssignmentOperation(J.AssignmentOperation assignmentOperation, P p) {
        visitAndValidateNonNull(assignmentOperation.getVariable(), Expression.class, p);
        visitAndValidateNonNull(assignmentOperation.getAssignment(), Expression.class, p);
        return assignmentOperation;
    }

    @Override
    public J.Binary visitBinary(J.Binary binary, P p) {
        visitAndValidateNonNull(binary.getLeft(), Expression.class, p);
        visitAndValidateNonNull(binary.getRight(), Expression.class, p);
        return binary;
    }

    @Override
    public J.Block visitBlock(J.Block block, P p) {
        ListUtils.map(block.getStatements(), el -> visitAndValidateNonNull(el, Statement.class, p));
        return block;
    }

    @Override
    public J.Break visitBreak(J.Break break_, P p) {
        visitAndValidate(break_.getLabel(), J.Identifier.class, p);
        return break_;
    }

    @Override
    public J.Case visitCase(J.Case case_, P p) {
        visitAndValidate(case_.getCaseLabels(), J.class, p);
        visitAndValidate(case_.getStatements(), Statement.class, p);
        visitAndValidate(case_.getBody(), J.class, p);
        visitAndValidate(case_.getGuard(), Expression.class, p);
        return case_;
    }

    @Override
    public J.ClassDeclaration visitClassDeclaration(J.ClassDeclaration classDeclaration, P p) {
        ListUtils.map(classDeclaration.getLeadingAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        ListUtils.map(classDeclaration.getModifiers(), el -> visitAndValidateNonNull(el, J.Modifier.class, p));
        visitAndValidate(classDeclaration.getPadding().getKind().getAnnotations(), J.Annotation.class, p);
        visitAndValidateNonNull(classDeclaration.getName(), J.Identifier.class, p);
        visitAndValidate(classDeclaration.getTypeParameters(), J.TypeParameter.class, p);
        visitAndValidate(classDeclaration.getPrimaryConstructor(), Statement.class, p);
        visitAndValidate(classDeclaration.getExtends(), TypeTree.class, p);
        visitAndValidate(classDeclaration.getImplements(), TypeTree.class, p);
        visitAndValidate(classDeclaration.getPermits(), TypeTree.class, p);
        visitAndValidateNonNull(classDeclaration.getBody(), J.Block.class, p);
        return classDeclaration;
    }

    @Override
    public J.Continue visitContinue(J.Continue continue_, P p) {
        visitAndValidate(continue_.getLabel(), J.Identifier.class, p);
        return continue_;
    }

    @Override
    public J.DoWhileLoop visitDoWhileLoop(J.DoWhileLoop doWhileLoop, P p) {
        visitAndValidateNonNull(doWhileLoop.getBody(), Statement.class, p);
        visitAndValidateNonNull(doWhileLoop.getWhileCondition(), Expression.class, p);
        return doWhileLoop;
    }

    @Override
    public J.Empty visitEmpty(J.Empty empty, P p) {
        return empty;
    }

    @Override
    public J.EnumValue visitEnumValue(J.EnumValue enumValue, P p) {
        ListUtils.map(enumValue.getAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        visitAndValidateNonNull(enumValue.getName(), J.Identifier.class, p);
        visitAndValidate(enumValue.getInitializer(), J.NewClass.class, p);
        return enumValue;
    }

    @Override
    public J.EnumValueSet visitEnumValueSet(J.EnumValueSet enumValueSet, P p) {
        ListUtils.map(enumValueSet.getEnums(), el -> visitAndValidateNonNull(el, J.EnumValue.class, p));
        return enumValueSet;
    }

    @Override
    public J.FieldAccess visitFieldAccess(J.FieldAccess fieldAccess, P p) {
        visitAndValidateNonNull(fieldAccess.getTarget(), Expression.class, p);
        visitAndValidateNonNull(fieldAccess.getName(), J.Identifier.class, p);
        return fieldAccess;
    }

    @Override
    public J.ForEachLoop visitForEachLoop(J.ForEachLoop forEachLoop, P p) {
        visitAndValidateNonNull(forEachLoop.getControl(), J.ForEachLoop.Control.class, p);
        visitAndValidateNonNull(forEachLoop.getBody(), Statement.class, p);
        return forEachLoop;
    }

    @Override
    public J.ForEachLoop.Control visitForEachControl(J.ForEachLoop.Control control, P p) {
        visitAndValidateNonNull(control.getVariable(), J.VariableDeclarations.class, p);
        visitAndValidateNonNull(control.getIterable(), Expression.class, p);
        return control;
    }

    @Override
    public J.ForLoop visitForLoop(J.ForLoop forLoop, P p) {
        visitAndValidateNonNull(forLoop.getControl(), J.ForLoop.Control.class, p);
        visitAndValidateNonNull(forLoop.getBody(), Statement.class, p);
        return forLoop;
    }

    @Override
    public J.ForLoop.Control visitForControl(J.ForLoop.Control control, P p) {
        ListUtils.map(control.getInit(), el -> visitAndValidateNonNull(el, Statement.class, p));
        visitAndValidateNonNull(control.getCondition(), Expression.class, p);
        ListUtils.map(control.getUpdate(), el -> visitAndValidateNonNull(el, Statement.class, p));
        return control;
    }

    @Override
    public J.ParenthesizedTypeTree visitParenthesizedTypeTree(J.ParenthesizedTypeTree parenthesizedTypeTree, P p) {
        ListUtils.map(parenthesizedTypeTree.getAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        visitAndValidateNonNull(parenthesizedTypeTree.getParenthesizedType(), J.Parentheses.class, p);
        return parenthesizedTypeTree;
    }

    @Override
    public J.Identifier visitIdentifier(J.Identifier identifier, P p) {
        ListUtils.map(identifier.getAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        return identifier;
    }

    @Override
    public J.If visitIf(J.If if_, P p) {
        visitAndValidateNonNull(if_.getIfCondition(), J.ControlParentheses.class, p);
        visitAndValidateNonNull(if_.getThenPart(), Statement.class, p);
        visitAndValidate(if_.getElsePart(), J.If.Else.class, p);
        return if_;
    }

    @Override
    public J.If.Else visitElse(J.If.Else else_, P p) {
        visitAndValidateNonNull(else_.getBody(), Statement.class, p);
        return else_;
    }

    @Override
    public J.Import visitImport(J.Import import_, P p) {
        visitAndValidateNonNull(import_.getQualid(), J.FieldAccess.class, p);
        visitAndValidate(import_.getAlias(), J.Identifier.class, p);
        return import_;
    }

    @Override
    public J.InstanceOf visitInstanceOf(J.InstanceOf instanceOf, P p) {
        visitAndValidateNonNull(instanceOf.getExpression(), Expression.class, p);
        visitAndValidateNonNull(instanceOf.getClazz(), J.class, p);
        visitAndValidate(instanceOf.getPattern(), J.class, p);
        return instanceOf;
    }

    @Override
    public J.DeconstructionPattern visitDeconstructionPattern(J.DeconstructionPattern deconstructionPattern, P p) {
        visitAndValidateNonNull(deconstructionPattern.getDeconstructor(), Expression.class, p);
        visitAndValidate(deconstructionPattern.getNested(), J.class, p);
        return deconstructionPattern;
    }

    @Override
    public J.IntersectionType visitIntersectionType(J.IntersectionType intersectionType, P p) {
        visitAndValidate(intersectionType.getBounds(), TypeTree.class, p);
        return intersectionType;
    }

    @Override
    public J.Label visitLabel(J.Label label, P p) {
        visitAndValidateNonNull(label.getLabel(), J.Identifier.class, p);
        visitAndValidateNonNull(label.getStatement(), Statement.class, p);
        return label;
    }

    @Override
    public J.Lambda visitLambda(J.Lambda lambda, P p) {
        visitAndValidate(lambda.getParameters().getParameters(), J.class, p);
        visitAndValidateNonNull(lambda.getBody(), J.class, p);
        return lambda;
    }

    @Override
    public J.Literal visitLiteral(J.Literal literal, P p) {
        return literal;
    }

    @Override
    public J.MemberReference visitMemberReference(J.MemberReference memberReference, P p) {
        visitAndValidateNonNull(memberReference.getContaining(), Expression.class, p);
        visitAndValidate(memberReference.getTypeParameters(), Expression.class, p);
        visitAndValidateNonNull(memberReference.getReference(), J.Identifier.class, p);
        return memberReference;
    }

    @Override
    public J.MethodDeclaration visitMethodDeclaration(J.MethodDeclaration methodDeclaration, P p) {
        ListUtils.map(methodDeclaration.getLeadingAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        ListUtils.map(methodDeclaration.getModifiers(), el -> visitAndValidateNonNull(el, J.Modifier.class, p));
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
        visitAndValidateNonNull(methodInvocation.getName(), J.Identifier.class, p);
        visitAndValidate(methodInvocation.getArguments(), Expression.class, p);
        return methodInvocation;
    }

    @Override
    public J.Modifier visitModifier(J.Modifier modifier, P p) {
        ListUtils.map(modifier.getAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        return modifier;
    }

    @Override
    public J.MultiCatch visitMultiCatch(J.MultiCatch multiCatch, P p) {
        ListUtils.map(multiCatch.getAlternatives(), el -> visitAndValidateNonNull(el, NameTree.class, p));
        return multiCatch;
    }

    @Override
    public J.NewArray visitNewArray(J.NewArray newArray, P p) {
        visitAndValidate(newArray.getTypeExpression(), TypeTree.class, p);
        ListUtils.map(newArray.getDimensions(), el -> visitAndValidateNonNull(el, J.ArrayDimension.class, p));
        visitAndValidate(newArray.getInitializer(), Expression.class, p);
        return newArray;
    }

    @Override
    public J.ArrayDimension visitArrayDimension(J.ArrayDimension arrayDimension, P p) {
        visitAndValidateNonNull(arrayDimension.getIndex(), Expression.class, p);
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
        ListUtils.map(nullableType.getAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        visitAndValidateNonNull(nullableType.getTypeTree(), TypeTree.class, p);
        return nullableType;
    }

    @Override
    public J.Package visitPackage(J.Package package_, P p) {
        visitAndValidateNonNull(package_.getExpression(), Expression.class, p);
        ListUtils.map(package_.getAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        return package_;
    }

    @Override
    public J.ParameterizedType visitParameterizedType(J.ParameterizedType parameterizedType, P p) {
        visitAndValidateNonNull(parameterizedType.getClazz(), NameTree.class, p);
        visitAndValidate(parameterizedType.getTypeParameters(), Expression.class, p);
        return parameterizedType;
    }

    @Override
    public <J2 extends J> J.Parentheses<J2> visitParentheses(J.Parentheses<J2> parentheses, P p) {
        visitAndValidateNonNull(parentheses.getTree(), J.class, p);
        return parentheses;
    }

    @Override
    public <J2 extends J> J.ControlParentheses<J2> visitControlParentheses(J.ControlParentheses<J2> controlParentheses, P p) {
        visitAndValidateNonNull(controlParentheses.getTree(), J.class, p);
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
        visitAndValidateNonNull(switch_.getSelector(), J.ControlParentheses.class, p);
        visitAndValidateNonNull(switch_.getCases(), J.Block.class, p);
        return switch_;
    }

    @Override
    public J.SwitchExpression visitSwitchExpression(J.SwitchExpression switchExpression, P p) {
        visitAndValidateNonNull(switchExpression.getSelector(), J.ControlParentheses.class, p);
        visitAndValidateNonNull(switchExpression.getCases(), J.Block.class, p);
        return switchExpression;
    }

    @Override
    public J.Synchronized visitSynchronized(J.Synchronized synchronized_, P p) {
        visitAndValidateNonNull(synchronized_.getLock(), J.ControlParentheses.class, p);
        visitAndValidateNonNull(synchronized_.getBody(), J.Block.class, p);
        return synchronized_;
    }

    @Override
    public J.Ternary visitTernary(J.Ternary ternary, P p) {
        visitAndValidateNonNull(ternary.getCondition(), Expression.class, p);
        visitAndValidateNonNull(ternary.getTruePart(), Expression.class, p);
        visitAndValidateNonNull(ternary.getFalsePart(), Expression.class, p);
        return ternary;
    }

    @Override
    public J.Throw visitThrow(J.Throw throw_, P p) {
        visitAndValidateNonNull(throw_.getException(), Expression.class, p);
        return throw_;
    }

    @Override
    public J.Try visitTry(J.Try try_, P p) {
        visitAndValidate(try_.getResources(), J.Try.Resource.class, p);
        visitAndValidateNonNull(try_.getBody(), J.Block.class, p);
        ListUtils.map(try_.getCatches(), el -> visitAndValidateNonNull(el, J.Try.Catch.class, p));
        visitAndValidate(try_.getFinally(), J.Block.class, p);
        return try_;
    }

    @Override
    public J.Try.Resource visitTryResource(J.Try.Resource resource, P p) {
        visitAndValidateNonNull(resource.getVariableDeclarations(), TypedTree.class, p);
        return resource;
    }

    @Override
    public J.Try.Catch visitCatch(J.Try.Catch catch_, P p) {
        visitAndValidateNonNull(catch_.getParameter(), J.ControlParentheses.class, p);
        visitAndValidateNonNull(catch_.getBody(), J.Block.class, p);
        return catch_;
    }

    @Override
    public J.TypeCast visitTypeCast(J.TypeCast typeCast, P p) {
        visitAndValidateNonNull(typeCast.getClazz(), J.ControlParentheses.class, p);
        visitAndValidateNonNull(typeCast.getExpression(), Expression.class, p);
        return typeCast;
    }

    @Override
    public J.TypeParameter visitTypeParameter(J.TypeParameter typeParameter, P p) {
        ListUtils.map(typeParameter.getAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        ListUtils.map(typeParameter.getModifiers(), el -> visitAndValidateNonNull(el, J.Modifier.class, p));
        visitAndValidateNonNull(typeParameter.getName(), Expression.class, p);
        visitAndValidate(typeParameter.getBounds(), TypeTree.class, p);
        return typeParameter;
    }

    @Override
    public J.Unary visitUnary(J.Unary unary, P p) {
        visitAndValidateNonNull(unary.getExpression(), Expression.class, p);
        return unary;
    }

    @Override
    public J.VariableDeclarations visitVariableDeclarations(J.VariableDeclarations variableDeclarations, P p) {
        ListUtils.map(variableDeclarations.getLeadingAnnotations(), el -> visitAndValidateNonNull(el, J.Annotation.class, p));
        ListUtils.map(variableDeclarations.getModifiers(), el -> visitAndValidateNonNull(el, J.Modifier.class, p));
        visitAndValidate(variableDeclarations.getTypeExpression(), TypeTree.class, p);
        ListUtils.map(variableDeclarations.getVariables(), el -> visitAndValidateNonNull(el, J.VariableDeclarations.NamedVariable.class, p));
        return variableDeclarations;
    }

    @Override
    public J.VariableDeclarations.NamedVariable visitVariable(J.VariableDeclarations.NamedVariable namedVariable, P p) {
        visitAndValidateNonNull(namedVariable.getName(), J.Identifier.class, p);
        visitAndValidate(namedVariable.getInitializer(), Expression.class, p);
        return namedVariable;
    }

    @Override
    public J.WhileLoop visitWhileLoop(J.WhileLoop whileLoop, P p) {
        visitAndValidateNonNull(whileLoop.getCondition(), J.ControlParentheses.class, p);
        visitAndValidateNonNull(whileLoop.getBody(), Statement.class, p);
        return whileLoop;
    }

    @Override
    public J.Wildcard visitWildcard(J.Wildcard wildcard, P p) {
        visitAndValidate(wildcard.getBoundedType(), NameTree.class, p);
        return wildcard;
    }

    @Override
    public J.Yield visitYield(J.Yield yield, P p) {
        visitAndValidateNonNull(yield.getValue(), Expression.class, p);
        return yield;
    }

    @Override
    public J.Unknown visitUnknown(J.Unknown unknown, P p) {
        visitAndValidateNonNull(unknown.getSource(), J.Unknown.Source.class, p);
        return unknown;
    }

    @Override
    public J.Unknown.Source visitUnknownSource(J.Unknown.Source source, P p) {
        return source;
    }

    @Override
    public J.Erroneous visitErroneous(J.Erroneous erroneous, P p) {
        return erroneous;
    }

}
