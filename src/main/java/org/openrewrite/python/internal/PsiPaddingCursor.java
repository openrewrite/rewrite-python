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
import com.intellij.psi.PsiFile;
import com.intellij.psi.PsiWhiteSpace;
import lombok.Value;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.Space;

import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Function;
import java.util.function.Supplier;

import static org.openrewrite.python.tree.PySpace.appendComment;
import static org.openrewrite.python.tree.PySpace.appendWhitespace;

public class PsiPaddingCursor {

    @Value
    public static class WithStatus<T> {
        T value;
        boolean succeeded;
    }

    private static State attachAfter(PsiElement element) {
        ASTNode nextNode = nodeAfter(element.getNode());
        if (nextNode == null) {
            return new State.StoppedAtEOF(element.getContainingFile());
        }

        return attachAt(nextNode.getPsi());
    }

    private static State attachToSpaceBefore(PsiElement element) {
        State state = attachAt(element);
        while (element.getPrevSibling() != null) {
            element = element.getPrevSibling();
            State prevState = attachAt(element);
            if (prevState instanceof State.Consumable) {
                state = prevState;
            } else {
                return state;
            }
        }
        return state;
    }

    private static State attachAtTrailingSpaceWithin(PsiElement element) {
        PsiElement child = element.getLastChild();
        if (child == null) {
            return attachAfter(element);
        }
        State state = attachAt(child);
        if (!(state instanceof State.Consumable)) {
            return attachAfter(element);
        }

        while (child.getPrevSibling() != null) {
            child = child.getPrevSibling();
            State prevState = attachAt(child);
            if (prevState instanceof State.Consumable) {
                state = prevState;
            } else {
                return state;
            }
        }

        return state;
    }

    private static State attachAt(PsiElement element) {
        {
            ASTNode node;
            ASTNode next = element.getNode();
            do {
                node = next;
                next = nextNodeInTraversal(node);
            } while (next != null && next.getStartOffset() == node.getStartOffset());

            element = node.getPsi();
        }
        if (element instanceof PsiWhiteSpace) {
            return new State.WhitespaceNext((PsiWhiteSpace) element, 0);
        } else if (element instanceof PsiComment) {
            return new State.CommentNext((PsiComment) element);
        } else {
            return new State.StoppedAtElement(element);
        }
    }

    private static @Nullable ASTNode nextNodeInTraversal(ASTNode node) {
        if (node.getFirstChildNode() != null) {
            return node.getFirstChildNode();
        } else {
            return nodeAfter(node);
        }
    }

    private static @Nullable ASTNode nodeAfter(ASTNode node) {
        if (node.getTreeNext() != null) {
            return node.getTreeNext();
        }

        node = node.getTreeParent();
        while (node != null && node.getTreeNext() == null) {
            node = node.getTreeParent();
        }

        if (node == null) {
            return null;
        } else {
            return node.getTreeNext();
        }
    }

    private static int actualNodeOffset(PsiElement element) {
        return element.getNode().getStartOffset();
    }

    private interface State {
        @Nullable Integer getSourceOffset();

        interface Consumable extends State {
            State consume(AtomicReference<Space> acc);

            State consumeUntilFound(AtomicReference<Space> acc, String search);
        }

        /**
         * Marker interface; declares that discarding this state will not discard unused whitespace.
         */
        interface Discardable extends State {
        }

        @Value
        class Uninitialized implements State.Discardable {
            static final Uninitialized INSTANCE = new Uninitialized();

            private Uninitialized() {
            }

            @Override
            public @Nullable Integer getSourceOffset() {
                return null;
            }
        }

        @Value
        class WhitespaceNext implements State.Consumable {
            PsiWhiteSpace element;
            int startIndex;

            @Override
            public State consume(AtomicReference<Space> acc) {
                acc.updateAndGet(space -> appendWhitespace(space, element.getText().substring(startIndex)));
                return attachAfter(element);
            }

            @Override
            public State consumeUntilFound(AtomicReference<Space> acc, String search) {
                final String nextText = element.getText().substring(startIndex);
                final String prevText = acc.get().getLastWhitespace();
                final String combinedText = prevText + nextText;

                final int startIndexInCombined = combinedText.indexOf(
                        search,
                        // take one char from `prevText` for each char of `search` except the last
                        prevText.length() - (search.length() - 1)
                );
                if (startIndexInCombined < 0) {
                    return consume(acc);
                } else {
                    final int endIndexInCombined = startIndexInCombined + search.length();
                    final int endIndexInNext = endIndexInCombined - prevText.length();
                    final String upToMatch = nextText.substring(0, endIndexInNext);
                    acc.updateAndGet(space -> appendWhitespace(space, upToMatch));

                    return new FoundMatch(element, endIndexInNext, search);
                }
            }

            @Override
            public Integer getSourceOffset() {
                return actualNodeOffset(element) + startIndex;
            }
        }

        @Value
        class CommentNext implements State.Consumable {
            PsiComment element;

            @Override
            public State consume(AtomicReference<Space> acc) {
                acc.updateAndGet(space -> appendComment(space, element.getText()));
                return attachAfter(element);
            }

            @Override
            public State consumeUntilFound(AtomicReference<Space> acc, String search) {
                return consume(acc);
            }

            @Override
            public Integer getSourceOffset() {
                return actualNodeOffset(element);
            }
        }

        /**
         * The cursor was searching for a newline and found it.
         */
        @Value
        class FoundMatch implements State.Consumable {
            PsiWhiteSpace matchEndedInWhitespace;
            int matchEndIndexExclusive;
            String search;

            private WhitespaceNext nextState() {
                return new WhitespaceNext(matchEndedInWhitespace, matchEndIndexExclusive);
            }

            @Override
            public State consume(AtomicReference<Space> acc) {
                return nextState().consume(acc);
            }

            @Override
            public State consumeUntilFound(AtomicReference<Space> acc, String search) {
                return nextState().consumeUntilFound(acc, search);
            }

            @Override
            public Integer getSourceOffset() {
                return actualNodeOffset(matchEndedInWhitespace) + matchEndIndexExclusive - search.length();
            }
        }

        /**
         * The cursor ran into non-whitespace and stopped.
         */
        @Value
        class StoppedAtElement implements State.Discardable {
            PsiElement stoppedAt;

            @Override
            public Integer getSourceOffset() {
                return actualNodeOffset(stoppedAt);
            }
        }

        @Value
        class StoppedAtEOF implements State.Discardable {
            PsiElement file;

            @Override
            public Integer getSourceOffset() {
                return file.getTextRange().getEndOffset();
            }
        }
    }

    private State state = State.Uninitialized.INSTANCE;
    private final PsiFile file;

    public PsiPaddingCursor(PsiFile file) {
        this.file = file;
    }

    public @Nullable Integer offsetInFile() {
        return state.getSourceOffset();
    }

    public boolean isPast(PsiElement element) {
        @Nullable Integer offset = offsetInFile();
        if (offset == null) {
            throw new IllegalStateException("not attached");
        }
        return offset > actualNodeOffset(element);
    }

    public <T> T withRollback(Supplier<T> fn) {
        final State prev = this.state;
        T result = fn.get();
        this.state = prev;
        return result;
    }

    public Space consumeRemaining() {
        AtomicReference<Space> acc = new AtomicReference<>(Space.EMPTY);
        while (state instanceof State.Consumable) {
            state = ((State.Consumable) state).consume(acc);
        }
        return acc.get();
    }

    public Space consumeRemainingAndExpect(PsiElement expectedNext) {
        final Space space = consumeRemaining();
        expectNext(expectedNext);
        return space;
    }

    public Space consumeRemainingAndExpectEOF() {
        final Space space = consumeRemaining();
        expectEOF();
        return space;
    }

    public WithStatus<Space> consumeUntilNewlineWithStatus() {
        return consumeUntilFoundWithStatus("\n");
    }

    public WithStatus<Space> consumeUntilFoundWithStatus(String search) {
        final AtomicReference<Space> acc = new AtomicReference<>(Space.EMPTY);
        while (state instanceof State.Consumable) {
            state = ((State.Consumable) state).consumeUntilFound(acc, search);
            if (state instanceof State.FoundMatch) {
                break;
            }
        }
        final boolean success = state instanceof State.FoundMatch;
        return new WithStatus<>(acc.get(), success);
    }

    public Space consumeUntilNewline() {
        return consumeUntilNewlineWithStatus().value;
    }

    public Space consumeUntilFound(String search) {
        return consumeUntilFoundWithStatus(search).value;
    }

    public @Nullable Space consumeUntilNewlineOrRollback() {
        return consumeUntilFoundOrRollback("\n", space -> space);
    }

    public <T> @Nullable T consumeUntilNewlineOrRollback(Function<Space, T> fn) {
        return consumeUntilFoundOrRollback("\n", fn);
    }

    public <T> @Nullable T consumeUntilFoundOrRollback(String search, Function<Space, T> fn) {
        final State initialState = state;
        WithStatus<Space> result = consumeUntilFoundWithStatus(search);
        if (result.succeeded) {
            return fn.apply(result.value);
        } else {
            state = initialState;
            return null;
        }
    }

    public Space consumeUntilExpectedNewline() {
        return consumeUntilExpectedWhitespace("\n");
    }

    public Space consumeUntilExpectedWhitespace(String search) {
        WithStatus<Space> withStatus = consumeUntilFoundWithStatus(search);
        if (!withStatus.succeeded) {
            throw new IllegalStateException("did not find pattern as expected;\n" + printDebuggingMessage("STOPPED HERE"));
        }
        return withStatus.value;
    }

    private void assertDiscardable() {
        if (!(this.state instanceof State.Discardable)) {
            throw new IllegalStateException("resetting would discard an active whitespace position;\n" + printDebuggingMessage("ATTEMPTED TO RESET HERE"));
        }
    }

    public void resetTo(PsiElement next) {
        assertDiscardable();
        this.state = attachAt(next);
    }

    public void resetToSpaceBefore(PsiElement elementAfterSpace) {
        assertDiscardable();
        this.state = attachToSpaceBefore(elementAfterSpace);
    }

    public void resetToSpaceAfter(PsiElement next) {
        assertDiscardable();
        this.state = attachAfter(next);
    }

    public void resetToTrailingSpaceWithin(PsiElement within) {
        assertDiscardable();
        this.state = attachAtTrailingSpaceWithin(within);
    }

    public void expectNext(PsiElement expectedNext) {
        final @Nullable Integer currentOffset = state.getSourceOffset();
        final int expectedOffset = actualNodeOffset(expectedNext);
        if (currentOffset == null || currentOffset != expectedOffset) {
            throw new IllegalStateException(String.format(
                    "did not stop (%d) where expected (%d);\n%s\n%s",
                    currentOffset == null ? -1 : currentOffset,
                    expectedOffset,
                    printDebuggingMessage("STOPPED HERE"),
                    printDebuggingMessage("EXPECTED HERE", expectedOffset)
            ));
        }
    }

    public void expectEOF() {
        if (!(state instanceof State.StoppedAtEOF)) {
            throw new IllegalStateException(String.format(
                    "did not stop where expected (at eof);\n%s",
                    printDebuggingMessage("STOPPED HERE")
            ));
        }
    }

    private String printDebuggingMessage(String label) {
        return printDebuggingMessage(label, state.getSourceOffset());
    }

    private String printDebuggingMessage(String label, @Nullable Integer offset) {
        StringBuilder sb = new StringBuilder();
        sb.append("In file " + file.getName() + ":\n");
        sb.append("--\n");
        if (offset == null) {
            sb.append("<null position>\n");
        } else {
            String text = this.file.getText();
            final int lastNewlineBeforeHere = lastNewline(text, offset - 1);
            final int nextNewline = nextNewline(text, offset);

            final int previewStart = lastNewline(text, lastNewlineBeforeHere - 80);
            final int previewEnd = nextNewline(text, nextNewline + 80);

            if (previewStart < nextNewline) {
                sb.append(text, previewStart, nextNewline + 1);
            }
            for (int i = 0; i < (offset - lastNewlineBeforeHere - 1); i++) {
                sb.append(" ");
            }
            sb.append("^-------[ ").append(label).append(" ]\n");
            if (nextNewline < previewEnd) {
                sb.append(text, nextNewline + 1, previewEnd);
            }
        }
        if (sb.charAt(sb.length() - 1) != '\n') {
            sb.append("\n");
        }
        sb.append("--\n");
        return sb.toString();
    }

    private static int nextNewline(String str, int afterPosition) {
        if (afterPosition >= str.length() || afterPosition < 0) {
            return str.length();
        }
        final int found = str.substring(afterPosition).indexOf("\n");
        return found < 0 ? str.length() : afterPosition + found;
    }

    private static int lastNewline(String str, int beforePosition) {
        if (beforePosition >= str.length() || beforePosition < 0) {
            return 0;
        }
        return Math.max(0, str.substring(0, beforePosition).lastIndexOf("\n"));
    }
}
