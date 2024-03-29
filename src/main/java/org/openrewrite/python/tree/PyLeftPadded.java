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

public class PyLeftPadded {
    public enum Location {
        ERROR_FROM(PySpace.Location.ERROR_FROM_SOURCE),
        MATCH_CASE_GUARD(PySpace.Location.MATCH_CASE_GUARD),
        NAMED_ARGUMENT(PySpace.Location.NAMED_ARGUMENT),
        YIELD_FROM(PySpace.Location.YIELD_FROM_PREFIX);

        private final PySpace.Location beforeLocation;

        Location(PySpace.Location beforeLocation) {
            this.beforeLocation = beforeLocation;
        }

        public PySpace.Location getBeforeLocation() {
            return beforeLocation;
        }
    }
}
