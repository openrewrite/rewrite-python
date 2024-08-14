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
package org.openrewrite.python.internal;

import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.jspecify.annotations.Nullable;
import org.openrewrite.PrintOutputCapture;
import org.openrewrite.java.tree.J;
import org.openrewrite.java.tree.Space;

import java.util.function.Function;

@FieldDefaults(makeFinal = true, level = AccessLevel.PUBLIC)
@AllArgsConstructor
public class PythonPrinterAdapter<
        TTree extends J,
        TLoc,
        TLeftLoc,
        TRtLoc,
        TContLoc,
        P> {

    SpaceVisitor<TLoc, P> spaceVisitor;
    Function<TLeftLoc, TLoc> getBeforeLocation;
    Function<TRtLoc, TLoc> getAfterLocation;
    Function<TContLoc, TLoc> getContainerBeforeLocation;
    Function<TContLoc, TRtLoc> getElementLocation;

    interface SpaceVisitor<TLoc, P> {
        void visitSpace(Space prefix, @Nullable TLoc loc, PrintOutputCapture<P> p);
    }
}
