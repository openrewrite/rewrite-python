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

public class PyRightPadded {
    public enum Location {
        ASSERT_ELEMENT(PySpace.Location.ASSERT_ELEMENT_SUFFIX),
        DEL_ELEMENT(PySpace.Location.DEL_ELEMENT_SUFFIX),
        DICT_LITERAL_ELEMENT(PySpace.Location.DICT_LITERAL_ELEMENT_SUFFIX),
        DICT_ENTRY_KEY(PySpace.Location.DICT_ENTRY_KEY_SUFFIX),
        KEY_VALUE_KEY_SUFFIX(PySpace.Location.KEY_VALUE_SUFFIX),
        MATCH_PATTERN_ELEMENT(PySpace.Location.MATCH_PATTERN_ELEMENT_SUFFIX),
        TOP_LEVEL_STATEMENT_SUFFIX(PySpace.Location.TOP_LEVEL_STATEMENT),
        VARIABLE_SCOPE_ELEMENT(PySpace.Location.VARIABLE_SCOPE_NAME_SUFFIX),
        YIELD_ELEMENT(PySpace.Location.YIELD_ELEMENT_SUFFIX);

        private final PySpace.Location afterLocation;

        Location(PySpace.Location afterLocation) {
            this.afterLocation = afterLocation;
        }

        public PySpace.Location getAfterLocation() {
            return afterLocation;
        }
    }
}
