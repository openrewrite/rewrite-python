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


import org.intellij.lang.annotations.Language;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.JavaVisitor;
import org.openrewrite.java.tree.Space;
import org.openrewrite.python.PythonParser;
import org.openrewrite.test.SourceSpec;
import org.openrewrite.test.SourceSpecs;

import java.util.function.Consumer;

import static org.assertj.core.api.Assertions.assertThat;
import static org.openrewrite.python.PythonParser.LanguageLevel.PYTHON_312;

public final class ParserAssertions {
    private ParserAssertions() {
    }
    public static SourceSpecs python(@Language("py") @Nullable String before) {
        return python(before, s -> {
        }, PYTHON_312);
    }

    public static SourceSpecs python(@Language("py") @Nullable String before, Consumer<SourceSpec<Py.CompilationUnit>> spec) {
        return python(before, spec, PYTHON_312);
    }

    public static SourceSpecs python(@Language("py") @Nullable String before, @Language("py") String after) {
        return python(before, after, s -> {
        }, PYTHON_312);
    }

    public static SourceSpecs python(@Language("py") @Nullable String before, @Language("py") String after,
                                     Consumer<SourceSpec<Py.CompilationUnit>> spec) {
        return python(before, after, spec, PYTHON_312);
    }

    public static SourceSpecs python(@Language("py") @Nullable String before, PythonParser.LanguageLevel languageLevel) {
        return python(before, s -> {
        }, languageLevel);
    }

    public static SourceSpecs python(@Language("py") @Nullable String before, Consumer<SourceSpec<Py.CompilationUnit>> spec, PythonParser.LanguageLevel languageLevel) {
        SourceSpec<Py.CompilationUnit> python = new SourceSpec<>(Py.CompilationUnit.class, null, PythonParser.builder().languageLevel(languageLevel), before, null);
        acceptSpec(spec, python);
        return python;
    }

    public static SourceSpecs python(@Language("py") @Nullable String before, @Language("py") String after, PythonParser.LanguageLevel languageLevel) {
        return python(before, after, s -> {
        }, languageLevel);
    }

    public static SourceSpecs python(@Language("py") @Nullable String before, @Language("py") String after,
                                     Consumer<SourceSpec<Py.CompilationUnit>> spec, PythonParser.LanguageLevel languageLevel) {
        SourceSpec<Py.CompilationUnit> python = new SourceSpec<>(Py.CompilationUnit.class, null, PythonParser.builder().languageLevel(languageLevel), before, s -> after);
        acceptSpec(spec, python);
        return python;
    }

    private static void acceptSpec(Consumer<SourceSpec<Py.CompilationUnit>> spec, SourceSpec<Py.CompilationUnit> python) {
        Consumer<Py.CompilationUnit> userSuppliedAfterRecipe = python.getAfterRecipe();
        python.afterRecipe(userSuppliedAfterRecipe::accept);
        spec.andThen(isFullyParsed()).accept(python);
    }

    public static Consumer<SourceSpec<Py.CompilationUnit>> isFullyParsed() {
        return spec -> spec.afterRecipe(cu -> new JavaVisitor<Integer>() {
            @Override
            public Space visitSpace(Space space, Space.Location loc, Integer integer) {
                assertThat(space.getWhitespace().trim()).isEmpty();
                return super.visitSpace(space, loc, integer);
            }
        }.visit(cu, 0));
    }
}
