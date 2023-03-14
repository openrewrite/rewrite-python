/*
 * Copyright 2021 the original author or authors.
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
package org.openrewrite.python.internal;

import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiComment;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiWhiteSpace;
import com.intellij.psi.impl.source.tree.LeafPsiElement;
import com.jetbrains.python.psi.PyElementType;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.Comment;
import org.openrewrite.java.tree.Space;
import org.openrewrite.python.tree.PyComment;
import org.openrewrite.python.tree.PySpace;

import java.util.ArrayList;
import java.util.List;

import static java.util.Collections.emptyList;
import static org.openrewrite.marker.Markers.EMPTY;

public abstract class PsiUtils {
    private PsiUtils() {
    }

    public static boolean isHiddenElement(PsiElement element) {
        return element.getTextLength() == 0;
    }

    public static boolean isLeafToken(@Nullable PsiElement element, PyElementType elementType) {
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

    public static PsiElement findFirstChildToken(PsiElement parent, PyElementType elementType, PyElementType... otherElementTypes) {
        PsiElement maybeMatch = maybeFindChildToken(parent, elementType);
        for (PyElementType otherElementType : otherElementTypes) {
            PsiElement maybeOtherMatch = maybeFindChildToken(parent, otherElementType);
            if (maybeOtherMatch != null) {
                if (maybeMatch == null || maybeMatch.getTextOffset() > maybeOtherMatch.getTextOffset()) {
                    maybeMatch = maybeOtherMatch;
                }
            }
        }

        if (maybeMatch == null) {
            throw new IllegalStateException(
                    String.format(
                            "Expected to find a child node of type %s (+%d others) match but found none",
                            elementType,
                            otherElementTypes.length
                    )
            );
        }

        return maybeMatch;
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

    public static @Nullable PsiElement nextSiblingSkipWhitespace(@Nullable PsiElement element) {
        if (element == null) return null;

        do {
            element = element.getNextSibling();
        } while (element instanceof PsiWhiteSpace || element instanceof PsiComment);

        return element;
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

    /**
     * Finds the space immediately preceding the element in the document text.
     * <br/>
     * This is *not the same* as {@link #spaceBefore}, which only collects space from preceding sibling PSI nodes.
     *<br/>
     * This method will also look in preceding sibling nodes, but will also continue up the tree to parent nodes
     * (and their preceding siblings) until either whitespace is found or the current text offset has changed.
     */
    public static Space findLeadingSpaceInTree(PsiElement current) {
        List<PsiElement> spaceElements = null;
        final int startOffset = current.getNode().getStartOffset();
        do {
            if (current.getPrevSibling() != null) {
                current = current.getPrevSibling();
            } else {
                current = current.getParent();
            }

            if (isWhitespaceOrComment(current)) {
                if (spaceElements == null) {
                    spaceElements = new ArrayList<>();
                }
                spaceElements.add(current);
            } else if (spaceElements != null) {
                break;
            }
        } while (current != null && current.getNode().getStartOffset() == startOffset);

        if (spaceElements == null) {
            return Space.EMPTY;
        }

        final PySpace.SpaceBuilder builder = new PySpace.SpaceBuilder();
        for (int i = spaceElements.size() - 1; i >= 0; i--) {
            final PsiElement spaceOrComment = spaceElements.get(i);
            if (current instanceof PsiComment) {
                builder.addComment(spaceOrComment.getText());
            } else if (current instanceof PsiWhiteSpace) {
                builder.addWhitespace(spaceOrComment.getText());
            } else {
                throw new IllegalStateException("unexpected");
            }
        }
        return builder.build();
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

    public static PsiElement findSpaceStart(@Nullable PsiElement spaceElement) {
        if (spaceElement == null) {
            return null;
        }
        if (!isWhitespaceOrComment(spaceElement)) {
            throw new IllegalArgumentException("expected whitespace element; found: " + spaceElement);
        }
        while (isWhitespaceOrComment(spaceElement.getPrevSibling())) {
            spaceElement = spaceElement.getPrevSibling();
        }
        return spaceElement;
    }

    public static PsiElement findSpaceEnd(@Nullable PsiElement spaceElement) {
        if (spaceElement == null) {
            return null;
        }
        if (!isWhitespaceOrComment(spaceElement)) {
            throw new IllegalArgumentException("expected whitespace element; found: " + spaceElement);
        }
        while (isWhitespaceOrComment(spaceElement.getNextSibling())) {
            spaceElement = spaceElement.getNextSibling();
        }
        return spaceElement;
    }

    /**
     * Collects all continuous space (whitespace and comments) that immediately precedes an element as a sibling.
     * This method will skip zero-length placeholder elements before looking for whitespace.
     */
    public static Space spaceBefore(@Nullable PsiElement element) {
        if (element == null) {
            return Space.EMPTY;
        }

        PsiElement end = element.getPrevSibling();
        while (end != null && isHiddenElement(end)) {
            end = end.getPrevSibling();
        }
        if (!isWhitespaceOrComment(end)) {
            return Space.EMPTY;
        }

        return mergeSpace(findSpaceStart(end), end);
    }

    /**
     * Collects all continuous space (whitespace and comments) that immediately follows an element as a sibling.
     * This method will skip zero-length placeholder elements before looking for whitespace.
     */
    public static Space spaceAfter(@Nullable PsiElement element) {
        if (element == null) {
            return Space.EMPTY;
        }

        PsiElement begin = element.getNextSibling();
        while (begin != null && isHiddenElement(begin)) {
            begin = begin.getNextSibling();
        }
        if (!isWhitespaceOrComment(begin)) {
            return Space.EMPTY;
        }

        return mergeSpace(begin, findSpaceEnd(begin));
    }

    /**
     * Collects trailing space <b>inside</b> of an element.
     * <p>
     * The PSI model for some elements (including statements) stores whitespace following an element inside of that
     * element, up to the first newline. This includes trailing comments.
     */
    public static Space trailingSpace(@Nullable PsiElement element) {
        if (element == null) {
            return Space.EMPTY;
        }

        PsiElement end = element.getLastChild();
        if (!isWhitespaceOrComment(end)) {
            return Space.EMPTY;
        }

        PsiElement begin = end;
        while (isWhitespaceOrComment(begin.getPrevSibling())) {
            begin = begin.getPrevSibling();
        }

        return mergeSpace(begin, end);
    }


    public static Space mergeSpace(PsiElement firstSpaceOrComment, PsiElement lastSpaceOrComment) {
        PsiUtils.PsiElementCursor psiElementCursor = PsiUtils.elementsBetween(firstSpaceOrComment, lastSpaceOrComment);

        final String prefix = psiElementCursor.consumeWhitespace();

        List<Comment> comments = null;
        while (!psiElementCursor.isPastEnd()) {
            if (comments == null) {
                comments = new ArrayList<>();
            }
            String commentText = psiElementCursor.consumeExpectingType(PsiComment.class).getText();
            final String suffix = psiElementCursor.consumeWhitespace();

            if (!commentText.startsWith("#")) {
                throw new IllegalStateException(
                        String.format(
                                "expected Python comment to start with `#`; found: `%s`",
                                commentText.charAt(0)
                        )
                );
            }
            commentText = commentText.substring(1);

            comments.add(new PyComment(commentText, suffix, false, EMPTY));
        }

        return Space.build(prefix, comments == null ? emptyList() : comments);
    }

    public static boolean isWhitespaceOrComment(@Nullable PsiElement element) {
        return element instanceof PsiComment || element instanceof PsiWhiteSpace;
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
