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
package org.openrewrite.python.style;

import lombok.Value;
import lombok.With;
import org.openrewrite.style.Style;
import org.openrewrite.style.StyleHelper;

import java.util.UUID;

@Value
@With
public class TabsAndIndentsStyle implements PythonStyle {
    UUID id;
    boolean useTabCharacter;
    int tabSize;
    int indentSize;
    int continuationIndent;
    boolean keepIndentsOnEmptyLines;

    @Override
    public Style applyDefaults() {
        return StyleHelper.merge(IntelliJ.tabsAndIndents(), this);
    }
}
