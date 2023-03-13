package org.openrewrite.python.internal;

import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiComment;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiWhiteSpace;
import com.intellij.psi.impl.source.tree.LeafElement;
import lombok.Value;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.Space;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.tree.PyComment;

import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Function;

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

            State consumeUntilNewline(AtomicReference<Space> acc);
        }

        /**
         * Marker interface; declares that discarding thie state will not discard unused whitespace.
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
            public State consumeUntilNewline(AtomicReference<Space> acc) {
                final String text = element.getText();
                final int index = text.indexOf("\n", startIndex);
                if (index < 0) {
                    return consume(acc);
                } else {
                    final String upToNewline = text.substring(startIndex, index + 1);
                    acc.updateAndGet(space -> appendWhitespace(space, upToNewline));

                    return new FoundNewline(element, index);
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
            public State consumeUntilNewline(AtomicReference<Space> acc) {
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
        class FoundNewline implements State.Consumable {
            PsiWhiteSpace whitespace;
            int newlineIndex;

            private WhitespaceNext nextState() {
                return new WhitespaceNext(whitespace, newlineIndex + 1);
            }

            @Override
            public State consume(AtomicReference<Space> acc) {
                return nextState().consume(acc);
            }

            @Override
            public State consumeUntilNewline(AtomicReference<Space> acc) {
                return nextState().consumeUntilNewline(acc);
            }

            @Override
            public Integer getSourceOffset() {
                return actualNodeOffset(whitespace) + newlineIndex;
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

    public PsiPaddingCursor() {
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

    public Space consumeRemaining() {
        AtomicReference<Space> acc = new AtomicReference<>(Space.EMPTY);
        while (state instanceof State.Consumable) {
            state = ((State.Consumable) state).consume(acc);
        }
        return acc.get();
    }

    public Space consumeRemainingAndExpect(PsiElement expectedNext) {
        System.err.println("expecting: " + expectedNext.getText());
        final Space space = consumeRemaining();

        final @Nullable Integer currentOffset = state.getSourceOffset();
        final int expectedOffset = actualNodeOffset(expectedNext);
        if (currentOffset == null || currentOffset != expectedOffset) {
            throw new IllegalStateException(String.format(
                    "did not stop (%d) where expected (%d)",
                    currentOffset == null ? -1 : currentOffset,
                    expectedOffset
            ));
        }
        return space;
    }

    public Space consumeRemainingAndExpectEOF() {
        final Space space = consumeRemaining();
        if (!(state instanceof State.StoppedAtEOF)) {
            throw new IllegalStateException("did not stop where expected (at eof)");
        }
        return space;
    }

    public WithStatus<Space> consumeUntilNewlineWithStatus() {
        final AtomicReference<Space> acc = new AtomicReference<>(Space.EMPTY);
        while (state instanceof State.Consumable) {
            state = ((State.Consumable) state).consumeUntilNewline(acc);
            if (state instanceof State.FoundNewline) {
                break;
            }
        }
        final boolean success = state instanceof State.FoundNewline;
        return new WithStatus<>(acc.get(), success);
    }

    public Space consumeUntilNewline() {
        return consumeUntilNewlineWithStatus().value;
    }

    public <T> @Nullable T consumeUntilNewlineOrReset(Function<Space, T> fn) {
        final State initialState = state;
        WithStatus<Space> result = consumeUntilNewlineWithStatus();
        if (result.succeeded) {
            return fn.apply(result.value);
        } else {
            state = initialState;
            return null;
        }
    }

    public Space consumeUntilExpectedNewline() {
        WithStatus<Space> withStatus = consumeUntilNewlineWithStatus();
        if (!withStatus.succeeded) {
            throw new IllegalStateException("did not find a newline as expected");
        }
        return withStatus.value;
    }

    private void assertDiscardable() {
        if (!(this.state instanceof State.Discardable)) {
            throw new IllegalStateException("resetting would discard an active whitespace position");
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
}
