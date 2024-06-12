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
package org.openrewrite.python.marker;

import lombok.EqualsAndHashCode;
import lombok.Value;
import lombok.With;
import org.openrewrite.Tree;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.Space;
import org.openrewrite.marker.Marker;

import java.util.UUID;

import static java.util.Collections.emptyList;

/**
 * For use as a last resort when Python elements semantically fit into the `J` scheme,
 * but lack the fields to store the necessary padding.
 */
@Value
@With
public class PythonExtraPadding implements Marker {
    @EqualsAndHashCode.Exclude
    UUID id;

    Location loc;

    @EqualsAndHashCode.Exclude
    Space space;

    public enum Location {
        /**
         * The method and class models don't support right-padding of decorators.
         * In Python, they're padded like statements and must be newline-terminated.
         * It's more natural to store trailing padding (which is unusual) with the decorator
         * rather than with the next sibling.
         *
         * <pre>
         *      \@foo⇒❘ # a comment❘⇐
         *      \@bar
         *      def method():
         *          pass
         * </pre>
         */
        AFTER_DECORATOR(Space.build("\n", emptyList())),

        /**
         * <pre>
         *      if someCondition⇒
         *          pass
         * </pre>
         */
        BEFORE_COMPOUND_BLOCK_COLON(Space.EMPTY),

        /**
         * Imports can optionally be wrapped in parens.
         *
         * <pre>
         *      from math import⇒
         *          sin,
         *          cos
         *      )
         * </pre>
         */
        IMPORT_PARENS_PREFIX(Space.build(" ", emptyList())),

        /**
         * Imports can optionally be wrapped in parens.
         *
         * <pre>
         *      from math import (
         *          sin,
         *          cos⇒
         *      )
         * </pre>
         */
        IMPORT_PARENS_SUFFIX(Space.build("\n", emptyList())),

        /**
         * Some Python operators have space within the operator itself.
         *
         * <pre>
         *      if x is⇒ not y:
         *          pass
         * </pre>
         */
        WITHIN_OPERATOR_NAME(Space.build(" ", emptyList())),

        /**
         * Some Python containers (like dict literals) can have space between the initialization delimiters
         * but lack the space for it in the model.
         *
         * <pre>
         *      xs = {⇒ }
         * </pre>
         */
        EMPTY_INITIALIZER(Space.EMPTY);

        final Space defaultSpace;

        Location(Space defaultSpace) {
            this.defaultSpace = defaultSpace;
        }
    }

    public static @Nullable Space get(Tree tree, Location loc) {
        for (PythonExtraPadding marker : tree.getMarkers().findAll(PythonExtraPadding.class)) {
            if (marker.loc == loc) {
                return marker.space;
            }
        }
        return null;
    }

    public static Space getOrDefault(Tree tree, Location loc) {
        @Nullable Space space = get(tree, loc);
        if (space == null) {
            return loc.defaultSpace;
        } else {
            return space;
        }
    }

    public static <T extends Tree> T set(T tree, Location loc, Space space) {
        if (space.equals(loc.defaultSpace)) return tree;

        PythonExtraPadding marker = new PythonExtraPadding(UUID.randomUUID(), loc, space);
        return tree.withMarkers(
                tree.getMarkers().compute(
                        marker,
                        (oldMarker, newMarker) ->
                                oldMarker == null
                                        ? newMarker
                                        : oldMarker.withSpace(space)
                )
        );
    }

}
