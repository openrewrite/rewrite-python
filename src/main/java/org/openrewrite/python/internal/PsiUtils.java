package org.openrewrite.python.internal;

import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiWhiteSpace;
import com.intellij.psi.impl.source.tree.LeafPsiElement;
import com.jetbrains.python.PyTokenTypes;
import com.jetbrains.python.psi.PyElementType;
import org.openrewrite.internal.lang.Nullable;

public abstract class PsiUtils {
    private PsiUtils() {
    }

    public static boolean isHiddenElement(PsiElement element) {
        return element.getTextLength() == 0;
    }

    public static boolean isLeafToken(PsiElement element, PyElementType elementType) {
        if (element instanceof LeafPsiElement) {
            LeafPsiElement leaf = (LeafPsiElement) element;
            return leaf.getElementType() == elementType;
        }
        return false;
    }

    public static @Nullable PsiElement maybeFindChildToken(PsiElement parent, PyElementType elementType) {
        ASTNode node = parent.getNode().findChildByType(elementType);
        if (node == null) {
            return null;
        }
        return node.getPsi();
    }

    public static PsiElement findChildToken(PsiElement parent, PyElementType elementType) {
        PsiElement found = maybeFindChildToken(parent, elementType);
        if (found == null) {
            throw new IllegalStateException(
                    String.format(
                            "Expected to find a child node of type %s match but found none",
                            elementType
                    )
            );
        }
        return found;
    }

    public static @Nullable LeafPsiElement maybeFindPreviousSiblingToken(PsiElement element, PyElementType elementType) {
        while (element != null) {
            if (isLeafToken(element, elementType)) {
                return (LeafPsiElement) element;
            }
            element = element.getPrevSibling();
        }
        return null;
    }

    public static LeafPsiElement findPreviousSiblingToken(PsiElement element, PyElementType elementType) {
        LeafPsiElement found = maybeFindPreviousSiblingToken(element, elementType);
        if (found == null) {
            throw new IllegalStateException(
                    String.format(
                            "Expected to find a previous sibling of type %s match but found none",
                            elementType
                    )
            );
        }
        return found;
    }

    public static boolean matchesTokenSequence(PsiElement current, PyElementType... tokens) {
        for (PyElementType token : tokens) {
            if (current == null) {
                return false;
            }
            if (!isLeafToken(current, token)) {
                return false;
            }
            current = current.getNextSibling();
            while (current instanceof PsiWhiteSpace) {
                current = current.getNextSibling();
            }
        }
        return true;
    }

    public static PsiElementCursor elementsBetween(@Nullable PsiElement begin, @Nullable PsiElement endInclusive) {
        return new PsiElementCursor(begin, endInclusive);
    }

    public static class PsiElementCursor {
        private @Nullable PsiElement current;
        private final @Nullable PsiElement end;

        public PsiElementCursor(@Nullable PsiElement current, @Nullable PsiElement end) {
            this.current = current;
            this.end = end;
        }

        public void advance() {
            if (current == null || current == end) {
                current = null;
            } else {
                current = current.getNextSibling();
            }
        }

        public PsiElement consume() {
            PsiElement element = current();
            advance();
            return element;
        }

        public <T extends PsiElement> T consumeExpectingType(Class<T> clazz) {
            PsiElement element = consume();
            if (!clazz.isInstance(element)) {
                throw new IllegalStateException(String.format(
                        "expected a %s, but next element is a %s",
                        clazz.getName(),
                        element.getClass().getName()
                ));
            }
            //noinspection unchecked
            return (T) element;
        }

        public String consumeWhitespace() {
            String whitespace = null;
            while (this.current instanceof PsiWhiteSpace) {
                final String part = this.current.getText();
                if (whitespace == null) {
                    whitespace = part;
                } else {
                    // there are not typically adjacent PsiWhitespace elements, so this should be faster than StringBuilder
                    //noinspection StringConcatenationInLoop
                    whitespace += part;
                }
                this.advance();
            }
            return whitespace == null ? "" : whitespace;
        }

        public PsiElement current() {
            if (this.current == null) {
                throw new IllegalStateException("cannot call current() if cursor is past the end");
            }
            return this.current;
        }

        public boolean isPastEnd() {
            return this.current == null;
        }
    }

}
