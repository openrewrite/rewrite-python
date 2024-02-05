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

import lombok.Value;
import lombok.With;
import org.openrewrite.marker.Marker;

import java.util.UUID;

/**
 * In Python, many operators are actually syntax sugar for method calls.
 * For example, <pre>a == b</pre> is syntax sugar for <pre>a.__eq__(b)</pre>.
 * This marker is for binary operators that were de-sugared to call expressions to fit into the Java language model.
 */
@Value
@With
public class MagicMethodDesugar implements Marker {
    UUID id;
}
