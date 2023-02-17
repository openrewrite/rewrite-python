package org.openrewrite.python.experimental;

import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiComment;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiWhiteSpace;
import com.intellij.psi.tree.IElementType;
import com.jetbrains.python.PyTokenTypes;
import com.jetbrains.python.psi.*;
import org.openrewrite.InMemoryExecutionContext;
import org.openrewrite.Parser;
import org.openrewrite.python.experimental.tree.*;
import org.openrewrite.python.experimental.tree.common.BetweenItemsList;
import org.openrewrite.python.experimental.tree.common.ItemList;
import org.openrewrite.python.experimental.tree.padding.*;
import org.openrewrite.python.internal.IntelliJUtils;

import java.io.File;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.function.Function;

public class PythonIntelliJMapper {

    public static void main(String[] args) {
        String filename = "example.py";
        Parser.Input input = new Parser.Input(
                new File(filename).toPath(),
                () -> PythonIntelliJMapper.class.getClassLoader().getResourceAsStream("examples/" + filename)
        );
        InMemoryExecutionContext ctx = new InMemoryExecutionContext();
        PyFile file = IntelliJUtils.parsePythonSource(input, ctx);
        CompilationUnit compilationUnit = new PythonIntelliJMapper().mapFile(file);
    }

    public CompilationUnit mapFile(PyFile element) {
        new IntelliJUtils.PsiPrinter().print(element.getNode());
        List<Statement> statements = new ArrayList<>();
        for (ASTNode child : element.getNode().getChildren(null)) {
            Statement statement = mapStatement(child.getPsi());
            if (statement != null) {
                System.out.println(statement);
                statements.add(statement);
            }
        }
        return new CompilationUnit(ItemList.from(statements));
    }

    public Statement mapStatement(PsiElement element) {
        if (element instanceof PyFunction) {
            PyFunction pyFunction = (PyFunction) element;
            System.out.println("indent = `" + PyIndentUtil.getElementIndent(((PyFunction) element).getStatementList()) + "`");
        } else if (element instanceof PyClass) {
            return mapClassDeclaration((PyClass) element);
        }
        return null;
    }

    public ClassDeclaration mapClassDeclaration(PyClass element) {
        ColonPadding colonPadding = extractColonPadding(element);
        ClassDeclaration.ExtendingPart extendingPart = null;
        if (element.getSuperClassExpressionList() != null) {
            Padding prefix = getPaddingBefore(element.getSuperClassExpressionList());
            Padding initial = getPaddingAfter(element, PyTokenTypes.LPAR);
            Padding ending;
            if (element.getSuperClassExpressions().length == 0) {
                ending = Padding.EMPTY;
            } else {
                ending = getPaddingBefore(element, PyTokenTypes.RPAR);
            }
            extendingPart = new ClassDeclaration.ExtendingPart(
                    prefix,
                    initial,
                    extractDelimitedList(element.getSuperClassExpressions(), PyTokenTypes.COMMA, this::mapExpression),
                    ending
            );
        }
        return new ClassDeclaration(
                new Identifier(element.getName()),
                Optional.ofNullable(extendingPart),
                colonPadding,
                mapStatementList(element.getStatementList())
        );
    }

    public StatementList mapStatementList(PyStatementList element) {
        final String parentIndent = getFullIndent(element.getParent());
        final String insideIndent = getFullIndent(element);
        if (!insideIndent.startsWith(parentIndent)) {
            throw new IllegalStateException("indents do not match");
        }
        final Indent indent = new Indent(insideIndent.substring(parentIndent.length()));

        final PyStatement[] pyStatements = element.getStatements();
        List<Statement> statements = new ArrayList<>();
        List<BlankLines> blankLinesBetween = new ArrayList<>();

        for (int i = 0; i < pyStatements.length; i++) {
            statements.add(mapStatement(pyStatements[i]));
            if (i < pyStatements.length - 1) {
                final Padding rawPadding = getPaddingAfter(pyStatements[i]);
                final Padding between = verifyAndStripIndent(rawPadding, insideIndent);

            }
        }

        return new StatementList(indent, BetweenItemsList.from(statements, blankLinesBetween));
    }

    public Expression mapExpression(PyExpression element) {
        return null;
    }

    private String getFullIndent(PsiElement element) {
        return PyIndentUtil.getElementIndent(element);
    }

    private Padding getPaddingBefore(PsiElement element) {
        return getPaddingImpl(element, true);
    }

    private Padding getPaddingBefore(PsiElement parent, IElementType elementType) {
        ASTNode found = parent.getNode().findChildByType(elementType);
        return found == null ? Padding.EMPTY : getPaddingBefore(found.getPsi());
    }

    private Padding getPaddingAfter(PsiElement element) {
        return getPaddingImpl(element, false);
    }

    private Padding getPaddingAfter(PsiElement parent, IElementType elementType) {
        ASTNode found = parent.getNode().findChildByType(elementType);
        return found == null ? Padding.EMPTY : getPaddingAfter(found.getPsi());
    }

    private Padding getPaddingImpl(PsiElement element, boolean reverse) {
        final List<PaddingElement> paddingElements = new ArrayList<>();
        final Function<PsiElement, PsiElement> getNextElement =
                reverse ? PsiElement::getPrevSibling : PsiElement::getNextSibling;

        element = getNextElement.apply(element);
        while (element != null) {
            if (element instanceof PsiWhiteSpace) {
                paddingElements.add(new WhiteSpace(element.getText()));
            } else if (element instanceof PsiComment) {
                paddingElements.add(new Comment(element.getText().substring(1)));
            } else {
                break;
            }
            element = getNextElement.apply(element);
        }
        if (reverse) {
            Collections.reverse(paddingElements);
        }
        return new Padding(ItemList.from(paddingElements));
    }

    private Padding verifyAndStripIndent(Padding original, String expectedIndent) {
        final int lastIndex = original.getElements().size() - 1;
        PaddingElement last = original.getElements().get(lastIndex);
        if (!(last instanceof WhiteSpace)) {
            throw new IllegalArgumentException("when an indent is expected in a Padding instance, it must end with whitespace");
        }
        String text = ((WhiteSpace) last).getText();
        if (!text.endsWith("\n" + expectedIndent)) {
            throw new IllegalArgumentException("expected indent was not found");
        }
        text = text.substring(0, text.length() - expectedIndent.length());
        return new Padding(original.getElements().withElementReplaced(lastIndex, new WhiteSpace(text)));
    }


    private ColonPadding extractColonPadding(PyStatementListContainer element) {
        final PsiElement colon = element.getNode().findChildByType(PyTokenTypes.COLON).getPsi();

        final String classLevelIndent = getFullIndent(element);
        final String insideIndent = getFullIndent(element.getStatementList());
        if (!insideIndent.startsWith(classLevelIndent)) {
            throw new IllegalStateException("indents do not match");
        }

        final Padding beforeColon = getPaddingBefore(colon);
        final ItemList<PaddingElement> afterColonWithBlankLines = verifyAndStripIndent(getPaddingAfter(colon), insideIndent).getElements();

        List<PaddingElement> afterColon = new ArrayList<>();
        List<PaddingElement> blankLinesFollowing = new ArrayList<>();

        boolean afterNewline = false;
        for (int index = 0; index < afterColonWithBlankLines.size(); index++) {
            final PaddingElement paddingElement = afterColonWithBlankLines.get(index);
            if (afterNewline) {
                blankLinesFollowing.add(paddingElement);
            } else if (paddingElement instanceof WhiteSpace) {
                final String text = ((WhiteSpace) paddingElement).getText();
                final int firstNewlineIndex = text.indexOf('\n');
                if (firstNewlineIndex < 0) {
                    afterColon.add(paddingElement);
                } else {
                    afterNewline = true;
                    afterColon.add(new WhiteSpace(text.substring(0, firstNewlineIndex)));
                    final String remaining = text.substring(firstNewlineIndex + 1);
                    if (!remaining.isEmpty()) {
                        blankLinesFollowing.add(new WhiteSpace(remaining));
                    }
                }
            } else if (paddingElement instanceof Comment) {
                // this ends the `afterColon` padding because it must be followed with a newline
                afterNewline = true;
                final String text = ((Comment) paddingElement).getText();
                if (text.contains("\n")) {
                    throw new IllegalStateException("comment should not contain a newline");
                }
                afterColon.add(paddingElement);
                index++;
                if (index >= afterColonWithBlankLines.size()) {
                    throw new IllegalStateException("expected initial-newline whitespace after comment");
                }
                final PaddingElement nextPaddingElement = afterColonWithBlankLines.get(index);
                if (!(nextPaddingElement instanceof WhiteSpace)) {
                    throw new IllegalStateException("expected initial-newline whitespace after comment");
                }
                String nextText = ((WhiteSpace) nextPaddingElement).getText();
                if (!nextText.startsWith("\n")) {
                    throw new IllegalStateException("expected initial-newline whitespace after comment");
                }
                nextText = nextText.substring(1);
                if (!nextText.isEmpty()) {
                    blankLinesFollowing.add(new WhiteSpace(nextText));
                }
            }
        }

        return new ColonPadding(
                beforeColon,
                new Padding(ItemList.from(afterColon)),
                new BlankLines(ItemList.from(blankLinesFollowing))
        );
    }

    private <T extends PsiElement, U extends PythonNode>
    BetweenItemsList<U, WrapPadding> extractDelimitedList(T[] elements, IElementType delimiterType, Function<T, U> mapper) {
        final List<U> nodes = new ArrayList<>();
        final List<WrapPadding> paddings = new ArrayList<>();
        for (int i = 0; i < elements.length; i++) {
            nodes.add(mapper.apply(elements[i]));
            if (i < elements.length - 1) {
                final PsiElement delimiter = findElementBetween(elements[i], delimiterType, elements[i + 1]);
                final Padding paddingBefore = getPaddingBefore(delimiter);
                final Padding paddingAfter = getPaddingAfter(delimiter);
                paddings.add(new WrapPadding(paddingBefore, paddingAfter));
            }
        }
        return BetweenItemsList.from(nodes, paddings);
    }

    private <T extends PsiElement> PsiElement findElementBetween(PsiElement start, IElementType findType, PsiElement end) {
        for (PsiElement element = start.getNextSibling(); element != null && element != end; element = element.getNextSibling()) {
            if (element.getNode().getElementType() == findType) {
                return element;
            }
        }
        throw new IllegalStateException("could not find matching element of type " + findType);
    }

}
