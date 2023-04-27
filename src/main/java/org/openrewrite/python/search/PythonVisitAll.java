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
package org.openrewrite.python.search;

import lombok.EqualsAndHashCode;
import lombok.Value;
import org.openrewrite.ExecutionContext;
import org.openrewrite.Recipe;
import org.openrewrite.TreeVisitor;
import org.openrewrite.java.tree.J;
import org.openrewrite.python.PythonIsoVisitor;

@Value
@EqualsAndHashCode(callSuper = true)
public class PythonVisitAll extends Recipe {

    @Override
    public String getDisplayName() {
        return "Python recipe to confirm LST matches source code.";
    }

    @Override
    public String getDescription() {
        return "A temporary recipe to identify parsing/printing issues.";
    }

    @Override
    protected TreeVisitor<?, ExecutionContext> getVisitor() {
        return new PythonIsoVisitor<ExecutionContext>() {
            @Override
            public J.CompilationUnit visitCompilationUnit(J.CompilationUnit cu, ExecutionContext executionContext) {
                return super.visitCompilationUnit(cu, executionContext);
            }
        };
    }
}
