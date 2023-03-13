/*
 * Copyright 2023 the original author or authors.
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
package org.openrewrite.python.tree;

import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.Comment;
import org.openrewrite.java.tree.Space;
import org.openrewrite.marker.Markers;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

public final class PySpace {

    public static final class SpaceBuilder {
        private @Nullable String initialWhitespace;
        private @Nullable List<Comment> comments;

        private @Nullable StringBuilder whitespaceBuilder;
        private @Nullable String nextComment;

        private String finishWhitespace() {
            if (whitespaceBuilder == null) {
                return "";
            } else {
                String ws = whitespaceBuilder.toString();
                whitespaceBuilder.setLength(0);
                return ws;
            }
        }

        private void finishComment() {
            String whitespace = finishWhitespace();
            if (nextComment != null) {
                if (comments == null) {
                    comments = new ArrayList<>();
                }
                comments.add(new PyComment(nextComment, whitespace, false, Markers.EMPTY));
            } else if (!whitespace.isEmpty()) {
                if (this.initialWhitespace != null) {
                    throw new IllegalStateException("unexpected");
                }
                this.initialWhitespace = whitespace;
            }
        }

        @SuppressWarnings("UnusedReturnValue")
        public SpaceBuilder addWhitespace(String whitespace) {
            if (whitespaceBuilder == null) {
                whitespaceBuilder = new StringBuilder();
            }
            whitespaceBuilder.append(whitespace);
            return this;
        }

        @SuppressWarnings("UnusedReturnValue")
        public SpaceBuilder addComment(String commentWithHash) {
            finishComment();
            nextComment = commentWithHash;
            return this;
        }

        public Space build() {
            finishComment();
            Space space = Space.build(
                    initialWhitespace == null ? "" : initialWhitespace,
                    comments == null ? Collections.emptyList() : comments
            );
            reset();
            return space;
        }

        public SpaceBuilder reset() {
            this.initialWhitespace = null;
            this.whitespaceBuilder.setLength(0);
            this.comments = null;
            return this;
        }
    }

    public static Space appendWhitespace(Space space, String whitespace) {
        if (!space.getComments().isEmpty()) {
            return space.withComments(
                    ListUtils.mapLast(
                            space.getComments(),
                            comment -> comment.withSuffix(comment.getSuffix() + whitespace)
                    )
            );
        } else {
            return space.withWhitespace(
                    space.getWhitespace() + whitespace
            );
        }
    }

    public static Space appendComment(Space space, String commentWithHash) {
        final String commentText = validateComment(commentWithHash);
        return space.withComments(ListUtils.concat(
                space.getComments(),
                new PyComment(commentText, "", false, Markers.EMPTY)
        ));
    }

    private static String validateComment(String commentWithHash) {
        if (!commentWithHash.startsWith("#")) {
            throw new IllegalArgumentException("comment should start with a hash");
        }
        if (commentWithHash.contains("\n")) {
            throw new IllegalArgumentException("comment cannot contain newlines");
        }
        return commentWithHash.substring(1);
    }

    public static Space reindent(Space space, String indentWithoutNewline) {
        if (space.getComments().isEmpty()) {
            return space.withWhitespace(space.getWhitespace() + indentWithoutNewline);
        }

        List<Comment> comments = new ArrayList<>(space.getComments());
        boolean isAligned = true;
        for (int i = space.getComments().size() - 1; i >= 0; i--) {
            Comment comment = comments.get(i);
            if (isAligned) {
                comment = comment.withSuffix(comment.getSuffix() + indentWithoutNewline);
            }
            comments.set(i, comment);
            isAligned = ((PyComment)comment).isAlignedToIndent();
        }
        space = space.withComments(comments);
        if (isAligned) {
            space = space.withWhitespace(space.getWhitespace() + indentWithoutNewline);
        }
        return space;
    }

    public static Space deindent(Space space, String indentWithoutNewline) {
        System.err.println("deindenting with: " + Space.build(indentWithoutNewline, Collections.emptyList()));
        System.err.println("  before: " + space);

        AtomicBoolean isAligned = new AtomicBoolean();
        String indentWithNewline = "\n" + indentWithoutNewline;

        isAligned.set(
                space.getWhitespace().endsWith(indentWithNewline)
                        || space.getWhitespace().equals(indentWithoutNewline)
        );
        if (isAligned.get()) {
            space = space.withWhitespace(
                    space.getWhitespace().substring(0, space.getWhitespace().length() - indentWithoutNewline.length())
            );
        }
        space = space.withComments(ListUtils.map(
                space.getComments(),
                comment -> {
                    if (isAligned.get()) {
                        comment = ((PyComment) comment).withAlignedToIndent(true);
                    }
                    isAligned.set(comment.getSuffix().endsWith(indentWithNewline));
                    if (isAligned.get()) {
                        comment = comment.withSuffix(
                                comment.getSuffix().substring(0, comment.getSuffix().length() - indentWithNewline.length() + 1)
                        );
                    }
                    return comment;
                }
        ));
        System.err.println("  after: " + space);
        if (!isAligned.get()) {
            throw new IllegalStateException("expected statement prefix to end with block indent");
        }
        return space;
    }

    public static Space stripIndent(Space space, String expectedIndent) {
        if (space.getComments().isEmpty()) {
            final String ws = space.getWhitespace();
            if (!ws.endsWith(expectedIndent)) {
                throw new IllegalStateException("expected statement prefix to end with block indent");
            }
            space = space.withWhitespace(
                    ws.substring(0, ws.length() - expectedIndent.length())
            );
        } else {
            space = space.withComments(
                    ListUtils.mapLast(
                            space.getComments(),
                            lastComment -> {
                                final String suffix = lastComment.getSuffix();
                                if (!suffix.endsWith(expectedIndent)) {
                                    throw new IllegalStateException("expected statement prefix to end with block indent");
                                }
                                return lastComment.withSuffix(
                                        suffix.substring(0, suffix.length() - expectedIndent.length())
                                );
                            }
                    )
            );
        }

        return space;
    }


    public enum Location {
        ASSERT_PREFIX,
        ASSERT_ELEMENT_SUFFIX,
        AWAIT_PREFIX,
        COMPREHENSION_CLAUSE_PREFIX,
        COMPREHENSION_CONDITION_PREFIX,
        COMPREHENSION_IN,
        COMPREHENSION_PREFIX,
        COMPREHENSION_SUFFIX,
        DEL_ELEMENT_SUFFIX,
        DEL_PREFIX,
        DICT_ENTRY,
        DICT_ENTRY_KEY_SUFFIX,
        DICT_LITERAL_ELEMENT_SUFFIX,
        DICT_LITERAL_PREFIX,
        EXCEPTION_TYPE_PREFIX,
        ERROR_FROM_PREFIX,
        ERROR_FROM_SOURCE,
        KEY_VALUE_PREFIX,
        KEY_VALUE_SUFFIX,
        MATCH_CASE_GUARD,
        MATCH_CASE_PREFIX,
        MATCH_PATTERN_PREFIX,
        MATCH_PATTERN_ELEMENT_PREFIX,
        MATCH_PATTERN_ELEMENT_SUFFIX,
        PASS_PREFIX,
        SPECIAL_PARAM_PREFIX,
        TOP_LEVEL_STATEMENT,
        TYPE_HINT_PREFIX,
        TYPE_HINTED_EXPRESSION_PREFIX,
        VARIABLE_SCOPE_NAME_SUFFIX,
        VARIABLE_SCOPE_PREFIX,
        YIELD_FROM_PREFIX,
        YIELD_PREFIX,
        YIELD_ELEMENT_SUFFIX,
    }

    private PySpace() {
    }
}
