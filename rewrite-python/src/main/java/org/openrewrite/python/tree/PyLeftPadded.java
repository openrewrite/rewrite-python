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
package org.openrewrite.python.tree;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

public class PyLeftPadded {
    @Getter
    @RequiredArgsConstructor
    public enum Location {
        BINARY_OPERATOR(PySpace.Location.BINARY_OPERATOR),
        ERROR_FROM(PySpace.Location.ERROR_FROM_SOURCE),
        FOR_LOOP_ITERABLE(PySpace.Location.FOR_LOOP_ITERABLE),
        MATCH_CASE_GUARD(PySpace.Location.MATCH_CASE_GUARD),
        NAMED_ARGUMENT(PySpace.Location.NAMED_ARGUMENT),
        TYPE_ALIAS_VALUE(PySpace.Location.TYPE_ALIAS_VALUE),
        ;

        private final PySpace.Location beforeLocation;
    }
}
