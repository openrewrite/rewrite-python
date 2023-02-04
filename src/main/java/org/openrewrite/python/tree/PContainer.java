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

public class PContainer {
    public enum Location {
        LIST_LITERAL_ELEMENTS(PSpace.Location.LIST_LITERAL_ELEMENTS, PRightPadded.Location.LIST_LITERAL_ELEMENT_SUFFIX),
        WHEN_BRANCH_EXPRESSION(PSpace.Location.WHEN_BRANCH_EXPRESSION, PRightPadded.Location.WHEN_BRANCH_EXPRESSION);

        private final PSpace.Location beforeLocation;
        private final PRightPadded.Location elementLocation;

        Location(PSpace.Location beforeLocation, PRightPadded.Location elementLocation) {
            this.beforeLocation = beforeLocation;
            this.elementLocation = elementLocation;
        }

        public PSpace.Location getBeforeLocation() {
            return beforeLocation;
        }

        public PRightPadded.Location getElementLocation() {
            return elementLocation;
        }
    }
}
