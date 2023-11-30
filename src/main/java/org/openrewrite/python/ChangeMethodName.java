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
package org.openrewrite.python;

import lombok.EqualsAndHashCode;
import lombok.Value;
import org.openrewrite.*;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.J;

@Incubating(since = "0.3.1")
@Value
@EqualsAndHashCode(callSuper = true)
public class ChangeMethodName extends Recipe {

    @Option(displayName = "Old method name",
            description = "The method name that will replace the existing name.",
            example = "any")
    String oldMethodName;

    @Option(displayName = "New method name",
            description = "The method name that will replace the existing name.",
            example = "any")
    String newMethodName;

    @Option(displayName = "Ignore type definition",
            description = "When set to `true` the definition of the old type will be left untouched. " +
                    "This is useful when you're replacing usage of a class but don't want to rename it.",
            required = false)
    @Nullable
    Boolean ignoreDefinition;

    @Override
    public String getDisplayName() {
        return "Change method name";
    }

    @Override
    public String getDescription() {
        return "Renames a method.";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new PythonIsoVisitor<ExecutionContext>() {
            @Override
            public J.MethodDeclaration visitMethodDeclaration(J.MethodDeclaration method, ExecutionContext executionContext) {
                J.MethodDeclaration m = super.visitMethodDeclaration(method, executionContext);
                if (!Boolean.TRUE.equals(ignoreDefinition) && oldMethodName.equals(m.getName().getSimpleName())) {
                    m = m.withName(m.getName().withSimpleName(newMethodName));
                }
                return m;
            }

            @Override
            public J.MethodInvocation visitMethodInvocation(J.MethodInvocation method, ExecutionContext executionContext) {
                J.MethodInvocation m = super.visitMethodInvocation(method, executionContext);
                if (oldMethodName.equals(m.getName().getSimpleName())) {
                    m = m.withName(m.getName().withSimpleName(newMethodName));
                }
                return m;
            }

            @Override
            public J.MemberReference visitMemberReference(J.MemberReference memberRef, ExecutionContext executionContext) {
                J.MemberReference m = super.visitMemberReference(memberRef, executionContext);
                if (oldMethodName.equals(m.getReference().getSimpleName())) {
                    m = m.withReference(m.getReference().withSimpleName(newMethodName));
                }
                return m;
            }
        };
    }
}
