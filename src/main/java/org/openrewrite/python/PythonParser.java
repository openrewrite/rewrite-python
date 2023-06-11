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

import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import org.openrewrite.*;
import org.openrewrite.internal.EncodingDetectingInputStream;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.internal.JavaTypeCache;
import org.openrewrite.python.internal.PsiPythonMapper;
import org.openrewrite.python.tree.Py;
import org.openrewrite.style.NamedStyles;
import org.openrewrite.tree.ParsingEventListener;
import org.openrewrite.tree.ParsingExecutionContextView;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

@SuppressWarnings("unused")
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
public class PythonParser implements Parser {
    private final LanguageLevel languageLevel;
    private final List<NamedStyles> styles;
    private final boolean logCompilationWarningsAndErrors;
    private final JavaTypeCache typeCache;

    @Override
    public Stream<SourceFile> parse(String... sources) {
        List<Input> inputs = new ArrayList<>(sources.length);
        for (int i = 0; i < sources.length; i++) {
            Path path = Paths.get("p" + i + ".py");
            int j = i;
            inputs.add(new Input(
                    path, null,
                    () -> new ByteArrayInputStream(sources[j].getBytes(StandardCharsets.UTF_8)),
                    true
            ));
        }

        return parseInputs(
                inputs,
                null,
                new InMemoryExecutionContext()
        );
    }

    @Override
    public Stream<SourceFile> parseInputs(Iterable<Input> inputs, @Nullable Path relativeTo, ExecutionContext ctx) {
        ParsingExecutionContextView pctx = ParsingExecutionContextView.view(ctx);
        ParsingEventListener parsingListener = pctx.getParsingListener();

        return acceptedInputs(inputs).map(sourceFile -> {
            Path path = sourceFile.getRelativePath(relativeTo);
            try (EncodingDetectingInputStream is = sourceFile.getSource(ctx)) {
                Py.CompilationUnit py = new PsiPythonMapper(path, is.getCharset(), is.isCharsetBomMarked(), mapLanguageLevel(languageLevel))
                        .mapSource(is.readFully());
                parsingListener.parsed(sourceFile, py);
                return py;
            } catch (Throwable t) {
                ctx.getOnError().accept(t);
                return ParseError.build(this, sourceFile, relativeTo, ctx, t);
            }
        });
    }

    public enum LanguageLevel {
        PYTHON_24,
        PYTHON_25,
        PYTHON_26,
        PYTHON_27,
        PYTHON_30,
        PYTHON_31,
        PYTHON_32,
        PYTHON_33,
        PYTHON_34,
        PYTHON_35,
        PYTHON_36,
        PYTHON_37,
        PYTHON_38,
        PYTHON_39,
        PYTHON_310,
        PYTHON_311,
        PYTHON_312
    }

    private static com.jetbrains.python.psi.LanguageLevel mapLanguageLevel(LanguageLevel languageLevel) {
        com.jetbrains.python.psi.LanguageLevel level;
        switch (languageLevel) {
            case PYTHON_24:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON24;
                break;
            case PYTHON_25:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON25;
                break;
            case PYTHON_26:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON26;
                break;
            case PYTHON_27:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON27;
                break;
            case PYTHON_30:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON30;
                break;
            case PYTHON_31:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON31;
                break;
            case PYTHON_32:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON32;
                break;
            case PYTHON_33:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON33;
                break;
            case PYTHON_34:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON34;
                break;
            case PYTHON_35:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON35;
                break;
            case PYTHON_36:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON36;
                break;
            case PYTHON_37:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON37;
                break;
            case PYTHON_38:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON38;
                break;
            case PYTHON_39:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON39;
                break;
            case PYTHON_310:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON310;
                break;
            case PYTHON_311:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON311;
                break;
            case PYTHON_312:
                level = com.jetbrains.python.psi.LanguageLevel.PYTHON312;
                break;
            default:
                level = com.jetbrains.python.psi.LanguageLevel.getLatest();
                break;
        }

        return level;
    }

    @Override
    public boolean accept(Path path) {
        return path.toString().endsWith(".py");
    }

    @Override
    public PythonParser reset() {
        typeCache.clear();
        return this;
    }

    @Override
    public Path sourcePathFromSourceText(Path prefix, String sourceCode) {
        return prefix.resolve("file.py");
    }

    public static Builder builder() {
        return new Builder();
    }

    @SuppressWarnings("unused")
    public static class Builder extends Parser.Builder {
        private LanguageLevel languageLevel = LanguageLevel.PYTHON_312;
        private JavaTypeCache typeCache = new JavaTypeCache();
        private boolean logCompilationWarningsAndErrors;
        private final List<NamedStyles> styles = new ArrayList<>();

        public Builder() {
            super(Py.CompilationUnit.class);
        }

        public Builder logCompilationWarningsAndErrors(boolean logCompilationWarningsAndErrors) {
            this.logCompilationWarningsAndErrors = logCompilationWarningsAndErrors;
            return this;
        }

        public Builder typeCache(JavaTypeCache typeCache) {
            this.typeCache = typeCache;
            return this;
        }

        public Builder styles(Iterable<? extends NamedStyles> styles) {
            for (NamedStyles style : styles) {
                this.styles.add(style);
            }
            return this;
        }

        public Builder languageLevel(LanguageLevel languageLevel) {
            this.languageLevel = languageLevel;
            return this;
        }

        public PythonParser build() {
            return new PythonParser(languageLevel, styles, logCompilationWarningsAndErrors, typeCache);
        }

        @Override
        public String getDslName() {
            return "python";
        }
    }
}
