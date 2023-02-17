package org.openrewrite.python.experimental;

import org.openrewrite.python.experimental.tree.*;

public interface PythonVisitor extends FunctionDeclaration.ParameterVisitor {
    void visitCompilationUnit(CompilationUnit compilationUnit);
    void visitIfStatement(IfStatement ifStatement);
    void visitStatementList(StatementList statementList);
    void visitIfPart(IfStatement.IfPart ifPart);
    void visitElsePart(IfStatement.ElsePart elsePart);
    void visitElIfPart(IfStatement.ElIfPart elIfPart);
    void visitStringLiteral(Literal.StringLiteral stringLiteral);
    void visitNumericLiteral(Literal.NumericLiteral numericLiteral);
    void visitBooleanLiteral(Literal.BooleanLiteral booleanLiteral);
    void visitMemberAccess(MemberAccess memberAccess);
    void visitVariableReference(VariableReference variableReference);
    void visitCallExpression(CallExpression callExpression);
    void visitIdentifier(Identifier identifier);
    void visitKeywordArgument(CallExpression.KeywordArgument namedArgument);
    void visitPositionalArgument(CallExpression.PositionalArgument positionalArgument);
    void visitArgumentList(CallExpression.ArgumentList argumentList);
    void visitClassDeclaration(ClassDeclaration classDeclaration);
    void visitExtendingPart(ClassDeclaration.ExtendingPart extendingPart);
    void visitExpressionStatement(ExpressionStatement expressionStatement);
    void visitFunctionDeclaration(FunctionDeclaration functionDeclaration);
    void visitBinaryOperatorExpression(BinaryOperatorExpression binaryOperatorExpression);
}
