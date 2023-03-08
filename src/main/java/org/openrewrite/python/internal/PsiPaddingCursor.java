package org.openrewrite.python.internal;

import com.intellij.psi.PsiComment;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiWhiteSpace;
import lombok.Value;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.Space;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.tree.PyComment;

import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Function;

public class PsiPaddingCursor {

    private static Space appendWhitespace(Space space, String ws) {
        if (ws.isEmpty()) {
            return space;
        } else if (space.getComments().isEmpty()) {
            return space.withWhitespace(space.getWhitespace() + ws);
        } else {
            return space.withComments(ListUtils.mapLast(
                    space.getComments(),
                    lastComment -> lastComment.withSuffix(
                            lastComment.getSuffix() + ws
                    )
            ));
        }
    }

    private static Space appendComment(Space space, String comment) {
        if (!comment.startsWith("#")) {
            throw new IllegalArgumentException("comment should start with a hash");
        }
        if (comment.contains("\n")) {
            throw new IllegalArgumentException("comment cannot contain newlines");
        }
        return space.withComments(ListUtils.concat(
                space.getComments(),
                new PyComment(comment.substring(1), "", Markers.EMPTY)
        ));
    }

    @Value
    public static class WithStatus<T> {
        T value;
        boolean succeeded;
    }

    private static State attachAfter(PsiElement element) {
        System.err.println(">> attaching after " + previewElement(element));
        // in-order traversal, limited to not increase depth
        while (element.getNextSibling() == null) {
            if (element.getParent() == null) {
                return new State.StoppedAtEOF(element.getContainingFile());
            }
            element = element.getParent();
        }

        element = element.getNextSibling();
        final State state = attachAt(element);
        System.err.println(">>> ended at " + state.getSourceOffset() + " with a " + state.getClass().getSimpleName());
        return state;
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
        System.err.println(">> attaching to trailing space within " + previewElement(element));
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

        System.err.println(">>> ended at " + state.getSourceOffset() + " with a " + state.getClass().getSimpleName());

        return state;
    }

    private static String previewElement(PsiElement element) {
        String preview;
        String fullText = element.getText();
        if (fullText.length() == 0) {
            preview = "<empty>";
        } else if (fullText.length() < 15) {
            preview = "\"" + fullText + "\"";
        } else {
            preview = "\"" + fullText.substring(0, 6) + "…" + fullText.substring(fullText.length() - 6) + "\"";
        }
        preview = preview.replace("\n", "⏎");

        return String.format(
                "{%s, %d, %s}",
                element.getNode().getElementType(),
                actualNodeOffset(element),
                preview
        );
    }

    private static State attachAt(PsiElement element) {
        System.err.println(">> attaching at " + previewElement(element));
        if (element instanceof PsiWhiteSpace) {
            System.err.println(">>> it's whitespace; attaching as WhitespaceNext");
            return new State.WhitespaceNext((PsiWhiteSpace) element, 0);
        } else if (element instanceof PsiComment) {
            System.err.println(">>> it's a comment; attaching as CommentNext");
            return new State.CommentNext((PsiComment) element);
        } else {
            System.err.println(">>> it's non-padding; attaching as StoppedAtElement");
            return new State.StoppedAtElement(element);
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
        System.err.println();
        System.err.println("> consumeRemaining @ " + state.getSourceOffset());
        AtomicReference<Space> acc = new AtomicReference<>(Space.EMPTY);
        while (state instanceof State.Consumable) {
            System.err.println("> temp result: " + acc.get());
            state = ((State.Consumable) state).consume(acc);
        }
        System.err.println("> result: " + acc.get());
        System.err.println("> new state: " + this.state.getClass().getSimpleName() + " @ " + this.state.getSourceOffset());
        System.err.println();
        return acc.get();
    }

    public Space consumeRemainingAndExpect(PsiElement expectedNext) {
        System.err.println("> (below will expect a " + expectedNext.getNode().getElementType() + ")");
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
        System.err.println();
        System.err.println("> consumeUntilNewline @ " + state.getSourceOffset());

        final AtomicReference<Space> acc = new AtomicReference<>(Space.EMPTY);
        while (state instanceof State.Consumable) {
            state = ((State.Consumable) state).consumeUntilNewline(acc);
            if (state instanceof State.FoundNewline) {
                break;
            }
        }
        final boolean success = state instanceof State.FoundNewline;
        System.err.println("> result: " + acc.get() + ", " + success);
        System.err.println("> new state: " + this.state.getClass().getSimpleName() + " @ " + this.state.getSourceOffset());
        System.err.println();
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
        System.err.println();
        System.err.println("> resetTo " + previewElement(next));
        assertDiscardable();
        this.state = attachAt(next);
        System.err.println("> new state: " + this.state.getClass().getSimpleName() + " @ " + this.state.getSourceOffset());
        System.err.println();
    }

    public void resetToSpaceBefore(PsiElement elementAfterSpace) {
        System.err.println();
        System.err.println("> resetToSpaceBefore " + previewElement(elementAfterSpace));
        assertDiscardable();
        this.state = attachToSpaceBefore(elementAfterSpace);
        System.err.println("> new state: " + this.state.getClass().getSimpleName() + " @ " + this.state.getSourceOffset());
        System.err.println();
    }

    public void resetToSpaceAfter(PsiElement next) {
        System.err.println();
        System.err.println("> resetToSpaceAfter " + previewElement(next));
        assertDiscardable();
        this.state = attachAfter(next);
        System.err.println("> new state: " + this.state.getClass().getSimpleName() + " @ " + this.state.getSourceOffset());
        System.err.println();
    }

    public void resetToTrailingSpaceWithin(PsiElement within) {
        System.err.println();
        System.err.println("> resetToTrailingSpaceWithin " + previewElement(within));
        assertDiscardable();
        this.state = attachAtTrailingSpaceWithin(within);
        System.err.println("> new state: " + this.state.getClass().getSimpleName() + " @ " + this.state.getSourceOffset());
        System.err.println();
    }
}
