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
package org.openrewrite.python.remote;

import org.jspecify.annotations.Nullable;
import org.openrewrite.Tree;
import org.openrewrite.java.tree.*;
import org.openrewrite.python.tree.PyComment;
import org.openrewrite.remote.ReceiverContext;
import org.openrewrite.remote.SenderContext;

import java.util.List;
import java.util.function.Function;

// IMPORTANT: This duplicates all logic from the Java `Extensions` class in order to be able to send `PyComment` instead of `TextComment`
// We should find a better way to solve this
public final class Extensions {
    public static Space receiveSpace(@Nullable Space space, Class<?> type, ReceiverContext ctx) {
        if (space != null) {
            space = space.withComments(ctx.receiveNonNullNodes(space.getComments(), Extensions::receiveComment));
            space = space.withWhitespace(ctx.receiveNonNullValue(space.getWhitespace(), String.class));
        } else {
            List<Comment> comments = ctx.receiveNonNullNodes(null, Extensions::receiveComment);
            String whitespace = ctx.receiveValue(null, String.class);
            space = Space.build(
                    whitespace,
                    comments
            );
        }
        return space;
    }

    public static Comment receiveComment(@Nullable Comment comment, @Nullable Class<Comment> type, ReceiverContext ctx) {
        if (comment != null) {
            comment = ((PyComment) comment).withText(ctx.receiveNonNullValue(((PyComment) comment).getText(), String.class));
            comment = comment.withSuffix(ctx.receiveNonNullValue(comment.getSuffix(), String.class));
            comment = ((PyComment) comment).withAlignedToIndent(ctx.receiveNonNullValue(((PyComment) comment).isAlignedToIndent(), boolean.class));
            comment = comment.withMarkers(ctx.receiveNonNullNode(comment.getMarkers(), ctx::receiveMarkers));
        } else {
            comment = new PyComment(
                    ctx.receiveNonNullValue(null, String.class),
                    ctx.receiveNonNullValue(null, String.class),
                    ctx.receiveNonNullValue(null, boolean.class),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers)
            );
        }
        return comment;
    }

    public static void sendSpace(Space space, SenderContext ctx) {
        ctx.sendNodes(space, Space::getComments, Extensions::sendComment, Function.identity());
        ctx.sendValue(space, Space::getWhitespace);
    }

    public static void sendComment(Comment comment, SenderContext ctx) {
        if (!(comment instanceof PyComment)) {
            throw new UnsupportedOperationException("Unsupported comment type: " + comment.getClass().getName());
        }

        ctx.sendValue((PyComment) comment, PyComment::getText);
        ctx.sendValue(comment, Comment::getSuffix);
        ctx.sendValue((PyComment) comment, PyComment::isAlignedToIndent);
        ctx.sendNode(comment, Comment::getMarkers, ctx::sendMarkers);
    }

    public static <T extends J> void sendContainer(JContainer<T> container, SenderContext ctx) {
        ctx.sendNode(container, JContainer::getBefore, Extensions::sendSpace);
        ctx.sendNodes(container, c -> c.getPadding().getElements(), Extensions::sendRightPadded, e -> e.getElement().getId());
        ctx.sendNode(container, JContainer::getMarkers, ctx::sendMarkers);
    }

    public static <T> void sendLeftPadded(JLeftPadded<T> leftPadded, SenderContext ctx) {
        ctx.sendNode(leftPadded, JLeftPadded::getBefore, Extensions::sendSpace);
        if (leftPadded.getElement() instanceof Tree) {
            ctx.sendNode(leftPadded, e -> (Tree) e.getElement(), ctx::sendTree);
        } else if (leftPadded.getElement() instanceof Space) {
            ctx.sendNode(leftPadded, e -> (Space) e.getElement(), Extensions::sendSpace);
        } else {
            ctx.sendValue(leftPadded, JLeftPadded::getElement);
        }
        ctx.sendNode(leftPadded, JLeftPadded::getMarkers, ctx::sendMarkers);
    }

    public static <T> void sendRightPadded(JRightPadded<T> rightPadded, SenderContext ctx) {
        if (rightPadded.getElement() instanceof Tree) {
            ctx.sendNode(rightPadded, e -> (Tree) e.getElement(), ctx::sendTree);
        } else if (rightPadded.getElement() instanceof Space) {
            ctx.sendNode(rightPadded, e -> (Space) e.getElement(), Extensions::sendSpace);
        } else {
            ctx.sendValue(rightPadded, JRightPadded::getElement);
        }
        ctx.sendNode(rightPadded, JRightPadded::getAfter, Extensions::sendSpace);
        ctx.sendNode(rightPadded, JRightPadded::getMarkers, ctx::sendMarkers);
    }

    public static <T extends J> JContainer<T> receiveContainer(@Nullable JContainer<T> container, @Nullable Class<?> type, ReceiverContext ctx) {
        if (container != null) {
            container = container.withBefore(ctx.receiveNonNullNode(container.getBefore(), Extensions::receiveSpace));
            container = container.getPadding().withElements(ctx.receiveNonNullNodes(container.getPadding().getElements(), Extensions::receiveRightPaddedTree));
            container = container.withMarkers(ctx.receiveNonNullNode(container.getMarkers(), ctx::receiveMarkers));
        } else {
            container = JContainer.build(
                    ctx.receiveNonNullNode(null, Extensions::receiveSpace),
                    ctx.receiveNonNullNodes(null, Extensions::receiveRightPaddedTree),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers)
            );
        }
        return container;
    }

    private static final ClassValue<ReceiverContext.DetailsReceiver<JLeftPadded>> leftPaddedValueReceiverCache = new ClassValue<ReceiverContext.DetailsReceiver<JLeftPadded>>() {
        @Override
        protected ReceiverContext.DetailsReceiver<JLeftPadded> computeValue(Class<?> valueType) {
            return (leftPadded, type, ctx) -> {
                if (leftPadded != null) {
                    leftPadded = leftPadded.withBefore(ctx.receiveNonNullNode(leftPadded.getBefore(), Extensions::receiveSpace));
                    leftPadded = leftPadded.withElement(ctx.receiveNonNullValue(leftPadded.getElement(), valueType));
                    leftPadded = leftPadded.withMarkers(ctx.receiveNonNullNode(leftPadded.getMarkers(), ctx::receiveMarkers));
                } else {
                    leftPadded = new JLeftPadded<>(
                            ctx.receiveNonNullNode(null, Extensions::receiveSpace),
                            ctx.receiveNonNullValue(null, valueType),
                            ctx.receiveNonNullNode(null, ctx::receiveMarkers)
                    );
                }
                return leftPadded;
            };
        }
    };

    public static <T> ReceiverContext.DetailsReceiver<JLeftPadded<T>> leftPaddedValueReceiver(Class<T> valueType) {
        return (ReceiverContext.DetailsReceiver) leftPaddedValueReceiverCache.get(valueType);
    }

    private static final ClassValue<ReceiverContext.DetailsReceiver<JLeftPadded>> leftPaddedNodeReceiverCache = new ClassValue<ReceiverContext.DetailsReceiver<JLeftPadded>>() {
        @Override
        protected ReceiverContext.DetailsReceiver<JLeftPadded> computeValue(Class<?> nodeType) {
            if (nodeType == Space.class) {
                return (leftPadded, type, ctx) -> {
                    if (leftPadded != null) {
                        leftPadded = leftPadded.withBefore(ctx.receiveNonNullNode(leftPadded.getBefore(), Extensions::receiveSpace));
                        leftPadded = leftPadded.withElement(ctx.receiveNonNullNode((Space)leftPadded.getElement(), Extensions::receiveSpace));
                        leftPadded = leftPadded.withMarkers(ctx.receiveNonNullNode(leftPadded.getMarkers(), ctx::receiveMarkers));
                    } else {
                        leftPadded = new JLeftPadded<>(
                                ctx.receiveNonNullNode(null, Extensions::receiveSpace),
                                ctx.receiveNonNullNode(null, Extensions::receiveSpace),
                                ctx.receiveNonNullNode(null, ctx::receiveMarkers)
                        );
                    }
                    return leftPadded;
                };
            }
            throw new IllegalArgumentException("Unsupported type: " + nodeType);
        }
    };

    public static <T> ReceiverContext.DetailsReceiver<JLeftPadded<T>> leftPaddedNodeReceiver(Class<T> nodeType) {
        return (ReceiverContext.DetailsReceiver) leftPaddedNodeReceiverCache.get(nodeType);
    }

    public static <T extends J> JLeftPadded<T> receiveLeftPaddedTree(@Nullable JLeftPadded<T> leftPadded, @Nullable Class<?> type, ReceiverContext ctx) {
        if (leftPadded != null) {
            leftPadded = leftPadded.withBefore(ctx.receiveNonNullNode(leftPadded.getBefore(), Extensions::receiveSpace));
            leftPadded = leftPadded.withElement(ctx.receiveNonNullNode(leftPadded.getElement(), ctx::receiveTree));
            leftPadded = leftPadded.withMarkers(ctx.receiveNonNullNode(leftPadded.getMarkers(), ctx::receiveMarkers));
        } else {
            leftPadded = new JLeftPadded<>(
                    ctx.receiveNonNullNode(null, Extensions::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers)
            );
        }
        return leftPadded;
    }

    private static final ClassValue<ReceiverContext.DetailsReceiver<JRightPadded>> rightPaddedValueReceiverCache = new ClassValue<ReceiverContext.DetailsReceiver<JRightPadded>>() {
        @Override
        protected ReceiverContext.DetailsReceiver<JRightPadded> computeValue(Class<?> valueType) {
            return (rightPadded, type, ctx) -> {
                if (rightPadded != null) {
                    rightPadded = rightPadded.withElement(ctx.receiveNonNullValue(rightPadded.getElement(), valueType));
                    rightPadded = rightPadded.withAfter(ctx.receiveNonNullNode(rightPadded.getAfter(), Extensions::receiveSpace));
                    rightPadded = rightPadded.withMarkers(ctx.receiveNonNullNode(rightPadded.getMarkers(), ctx::receiveMarkers));
                } else {
                    rightPadded = new JRightPadded<>(
                            ctx.receiveNonNullValue(null, valueType),
                            ctx.receiveNonNullNode(null, Extensions::receiveSpace),
                            ctx.receiveNonNullNode(null, ctx::receiveMarkers)
                    );
                }
                return rightPadded;
            };
        }
    };

    public static <T> ReceiverContext.DetailsReceiver<JRightPadded<T>> rightPaddedValueReceiver(Class<T> valueType) {
        return (ReceiverContext.DetailsReceiver) rightPaddedValueReceiverCache.get(valueType);
    }

    private static final ClassValue<ReceiverContext.DetailsReceiver<JRightPadded>> rightPaddedNodeReceiverCache = new ClassValue<ReceiverContext.DetailsReceiver<JRightPadded>>() {
        @Override
        protected ReceiverContext.DetailsReceiver<JRightPadded> computeValue(Class<?> nodeType) {
            if (nodeType == Space.class) {
                return (rightPadded, type, ctx) -> {
                    if (rightPadded != null) {
                        rightPadded = rightPadded.withElement(ctx.receiveNonNullNode((Space)rightPadded.getElement(), Extensions::receiveSpace));
                        rightPadded = rightPadded.withAfter(ctx.receiveNonNullNode(rightPadded.getAfter(), Extensions::receiveSpace));
                        rightPadded = rightPadded.withMarkers(ctx.receiveNonNullNode(rightPadded.getMarkers(), ctx::receiveMarkers));
                    } else {
                        rightPadded = new JRightPadded<>(
                                ctx.receiveNonNullNode(null, Extensions::receiveSpace),
                                ctx.receiveNonNullNode(null, Extensions::receiveSpace),
                                ctx.receiveNonNullNode(null, ctx::receiveMarkers)
                        );
                    }
                    return rightPadded;
                };
            }
            throw new IllegalArgumentException("Unsupported type: " + nodeType);
        }
    };

    public static <T> ReceiverContext.DetailsReceiver<JRightPadded<T>> rightPaddedNodeReceiver(Class<T> nodeType) {
        return (ReceiverContext.DetailsReceiver) rightPaddedNodeReceiverCache.get(nodeType);
    }

    public static <T extends J> JRightPadded<T> receiveRightPaddedTree(@Nullable JRightPadded<T> rightPadded, @Nullable Class<?> type, ReceiverContext ctx) {
        if (rightPadded != null) {
            rightPadded = rightPadded.withElement(ctx.receiveNonNullNode(rightPadded.getElement(), ctx::receiveTree));
            rightPadded = rightPadded.withAfter(ctx.receiveNonNullNode(rightPadded.getAfter(), Extensions::receiveSpace));
            rightPadded = rightPadded.withMarkers(ctx.receiveNonNullNode(rightPadded.getMarkers(), ctx::receiveMarkers));
        } else {
            rightPadded = new JRightPadded<>(
                    ctx.receiveNonNullNode(null, ctx::receiveTree),
                    ctx.receiveNonNullNode(null, Extensions::receiveSpace),
                    ctx.receiveNonNullNode(null, ctx::receiveMarkers)
            );
        }
        return rightPadded;
    }
}
