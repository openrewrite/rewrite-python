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

import lombok.Getter;
import lombok.RequiredArgsConstructor;

public class PyContainer {
    @Getter
    @RequiredArgsConstructor
    public enum Location {
        COLLECTION_LITERAL_ELEMENTS(PySpace.Location.COLLECTION_LITERAL_PREFIX, PyRightPadded.Location.COLLECTION_LITERAL_ELEMENT),
        DICT_LITERAL_ELEMENTS(PySpace.Location.DICT_LITERAL_PREFIX, PyRightPadded.Location.DICT_LITERAL_ELEMENT),
        MATCH_PATTERN_ELEMENTS(PySpace.Location.MATCH_PATTERN_ELEMENT_PREFIX, PyRightPadded.Location.MATCH_PATTERN_ELEMENT),
        MULTI_IMPORT_NAMES(PySpace.Location.MULTI_IMPORT_NAME_PREFIX, PyRightPadded.Location.MULTI_IMPORT_NAME);

        private final PySpace.Location beforeLocation;
        private final PyRightPadded.Location elementLocation;
    }
}
