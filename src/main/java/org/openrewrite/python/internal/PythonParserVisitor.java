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
package org.openrewrite.python.internal;

import org.openrewrite.ExecutionContext;
import org.openrewrite.FileAttributes;
import org.openrewrite.internal.EncodingDetectingInputStream;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.internal.JavaTypeCache;
import org.openrewrite.java.tree.JLeftPadded;
import org.openrewrite.java.tree.JRightPadded;
import org.openrewrite.java.tree.Space;
import org.openrewrite.marker.Markers;

import java.nio.charset.Charset;
import java.nio.file.Path;
import java.util.regex.Pattern;

import static org.openrewrite.internal.StringUtils.indexOfNextNonWhitespace;
import static org.openrewrite.java.tree.Space.EMPTY;
import static org.openrewrite.java.tree.Space.format;

public class PythonParserVisitor {
    private final Path sourcePath;

    @Nullable
    private final FileAttributes fileAttributes;

    private final String source;
    private final Charset charset;
    private final boolean charsetBomMarked;
    private final ExecutionContext ctx;
    private int cursor;

    private static final Pattern whitespaceSuffixPattern = Pattern.compile("\\s*[^\\s]+(\\s*)");

    public PythonParserVisitor(Path sourcePath, @Nullable FileAttributes fileAttributes, EncodingDetectingInputStream source,
                               JavaTypeCache typeCache, ExecutionContext ctx) {
        this.sourcePath = sourcePath;
        this.fileAttributes = fileAttributes;
        this.source = source.readFully();
        this.charset = source.getCharset();
        this.charsetBomMarked = source.isCharsetBomMarked();
        this.ctx = ctx;
    }

    private <T> JLeftPadded<T> padLeft(Space left, T tree) {
        return new JLeftPadded<>(left, tree, Markers.EMPTY);
    }

    @SuppressWarnings("SameParameterValue")
    private <T> JRightPadded<T> padRight(T tree, @Nullable Space right) {
        return new JRightPadded<>(tree, right == null ? EMPTY : right, Markers.EMPTY);
    }

    private int positionOfNext(String untilDelim) {
        return positionOfNext(untilDelim, null);
    }

    private int positionOfNext(String untilDelim, @Nullable Character stop) {
        boolean inMultiLineComment = false;
        boolean inSingleLineComment = false;

        int delimIndex = cursor;
        for (; delimIndex < source.length() - untilDelim.length() + 1; delimIndex++) {
            if (inSingleLineComment) {
                if (source.charAt(delimIndex) == '\n') {
                    inSingleLineComment = false;
                }
            } else {
                if (source.length() - untilDelim.length() > delimIndex + 1) {
                    char c1 = source.charAt(delimIndex);
                    char c2 = source.charAt(delimIndex + 1);
                    if (c1 == '/') {
                        if (c2 == '/') {
                            inSingleLineComment = true;
                            delimIndex++;
                        } else if (c2 == '*') {
                            inMultiLineComment = true;
                            delimIndex++;
                        }
                    } else if (c1 == '*') {
                        if (c2 == '/') {
                            inMultiLineComment = false;
                            delimIndex += 2;
                        }
                    }
                }

                if (!inMultiLineComment && !inSingleLineComment) {
                    if (stop != null && source.charAt(delimIndex) == stop) {
                        return -1;
                    } // reached stop word before finding the delimiter

                    if (source.startsWith(untilDelim, delimIndex)) {
                        break; // found it!
                    }
                }
            }
        }

        return delimIndex > source.length() - untilDelim.length() ? -1 : delimIndex;
    }

    private Space sourceBefore(String untilDelim) {
        int delimIndex = positionOfNext(untilDelim);
        if (delimIndex < 0) {
            return EMPTY; // unable to find this delimiter
        }

        String prefix = source.substring(cursor, delimIndex);
        cursor += prefix.length() + untilDelim.length(); // advance past the delimiter
        return Space.format(prefix);
    }

    /**
     * @return Source from <code>cursor</code> to next occurrence of <code>untilDelim</code>,
     * and if not found in the remaining source, the empty String. If <code>stop</code> is reached before
     * <code>untilDelim</code> return the empty String.
     */
    @SuppressWarnings("SameParameterValue")
    private Space sourceBefore(String untilDelim, @Nullable Character stop) {
        int delimIndex = positionOfNext(untilDelim, stop);
        if (delimIndex < 0) {
            return EMPTY; // unable to find this delimiter
        }

        if (delimIndex == cursor) {
            cursor += untilDelim.length();
            return EMPTY;
        }
        String prefix = source.substring(cursor, delimIndex);
        cursor += prefix.length() + untilDelim.length(); // advance past the delimiter
        return Space.format(prefix);
    }

    private Space whitespace() {
        String prefix = source.substring(cursor, indexOfNextNonWhitespace(cursor, source));
        cursor += prefix.length();
        return format(prefix);
    }
}
