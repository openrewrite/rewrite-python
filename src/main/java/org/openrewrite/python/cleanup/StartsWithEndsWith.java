/*
 * Copyright 2024 the original author or authors.
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
package org.openrewrite.python.cleanup;

import org.openrewrite.ExecutionContext;
import org.openrewrite.Recipe;
import org.openrewrite.Repeat;
import org.openrewrite.TreeVisitor;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.*;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.PythonVisitor;
import org.openrewrite.python.marker.BuiltinDesugar;

import java.util.Arrays;
import java.util.List;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static java.util.stream.Collectors.toList;
import static org.openrewrite.Tree.randomId;
import static org.openrewrite.marker.Markers.EMPTY;

public class StartsWithEndsWith extends Recipe {
    @Override
    public String getDisplayName() {
        return "Combine startswith and endswith";
    }

    @Override
    public String getDescription() {
        return "`startswith` and `endswith` methods of the `str` object accept a tuple of strings to match against." +
               "When multiple calls to `startswith` or `endswith` are made on the same string, they can be combined into a single call with a tuple of strings.";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return Repeat.repeatUntilStable(new StartsWithEndsWithVisitor<>());
    }

    private static class StartsWithEndsWithVisitor<P> extends PythonVisitor<P> {
        @Override
        public J visitBinary(J.Binary binary, P p) {
            if (binary.getOperator() == J.Binary.Type.Or) {
                Expression left = binary.getLeft();
                Expression right = binary.getRight();
                if (left instanceof J.MethodInvocation && right instanceof J.MethodInvocation) {
                    J.MethodInvocation leftMethod = (J.MethodInvocation) left;
                    J.MethodInvocation rightMethod = (J.MethodInvocation) right;
                    boolean bothStartsWith = leftMethod.getSimpleName().equals("startswith") && rightMethod.getSimpleName().equals("startswith");
                    boolean bothEndsWith = leftMethod.getSimpleName().equals("endswith") && rightMethod.getSimpleName().equals("endswith");
                    if ((bothStartsWith || bothEndsWith) &&
                        leftMethod.getSelect() != null &&
                        rightMethod.getSelect() != null &&
                        leftMethod.getArguments().size() == 1 &&
                        rightMethod.getArguments().size() == 1 &&
                        leftMethod.getSelect().printTrimmed(getCursor()).equals(rightMethod.getSelect().printTrimmed(getCursor()))
                    ) {
                        final List<Expression> rightExpressionFinal = ListUtils.map(
                                getSimplestRightExpressions(rightMethod),
                                e -> e.withPrefix(Space.SINGLE_SPACE)
                        );
                        if (leftMethod.getArguments().get(0) instanceof J.MethodInvocation &&
                            "tuple".equals(((J.MethodInvocation) leftMethod.getArguments().get(0)).getSimpleName())) {
                            J.MethodInvocation tuple = (J.MethodInvocation) leftMethod.getArguments().get(0);

                            tuple = tuple.withArguments(ListUtils.mapFirst(tuple.getArguments(), arg -> {
                                assert arg instanceof J.NewArray;
                                J.NewArray newArray = (J.NewArray) arg;
                                newArray = newArray.withInitializer(ListUtils.concatAll(
                                        newArray.getInitializer(),
                                        rightExpressionFinal
                                ));
                                return newArray;
                            }));
                            return leftMethod.withArguments(singletonList(tuple)).withPrefix(binary.getPrefix());
                        }
                        return leftMethod.withArguments(singletonList(
                                createTuple(
                                        leftMethod.getArguments().get(0),
                                        rightExpressionFinal
                                )
                        )).withPrefix(binary.getPrefix());
                    }
                }
            }
            return super.visitBinary(binary, p);
        }

        @Nullable
        private static List<Expression> getSimplestRightExpressions(J.MethodInvocation rightMethod) {
            // The `rightMethod` is already a call to `startsWith` or `endsWith`
            // If the right side is already a tuple, then unpack the elements
            if (rightMethod.getArguments().get(0) instanceof J.MethodInvocation &&
                "tuple".equals(((J.MethodInvocation) rightMethod.getArguments().get(0)).getSimpleName())) {
                J.NewArray newArray = (J.NewArray) ((J.MethodInvocation) rightMethod.getArguments().get(0)).getArguments().get(0);
                return newArray.getInitializer();
            } else {
                // Otherwise, the right side is a single element
                return rightMethod.getArguments();
            }
        }

        private J.MethodInvocation createTuple(Expression first, List<Expression> right) {
            Markers markers = Markers.build(singletonList(new BuiltinDesugar(randomId())));
            J.Identifier builtins = makeBuiltinsIdentifier();

            List<JRightPadded<Expression>> paddedRight =
                    right
                            .stream()
                            .map(JRightPadded::build)
                            .collect(toList());
            JContainer<Expression> args = JContainer.build(singletonList(
                    JRightPadded.build(
                            new J.NewArray(
                                    randomId(),
                                    Space.EMPTY,
                                    markers,
                                    null,
                                    emptyList(),
                                    JContainer.build(
                                            ListUtils.concat(
                                                    JRightPadded.build(first),
                                                    paddedRight
                                            )
                                    ),
                                    null
                            )
                    )
            ));
            return new J.MethodInvocation(
                    randomId(),
                    Space.EMPTY,
                    markers,
                    JRightPadded.build(builtins),
                    null,
                    new J.Identifier(randomId(), Space.EMPTY, EMPTY, "tuple", null, null),
                    args,
                    null
            );
        }

        private J.Identifier makeBuiltinsIdentifier() {
            return new J.Identifier(randomId(), Space.EMPTY, EMPTY, "__builtins__", null, null);
        }
    }
}
