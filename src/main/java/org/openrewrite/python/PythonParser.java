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

import com.intellij.lang.ASTNode;
import com.intellij.lang.ParserDefinition;
import com.intellij.lang.PsiBuilder;
import com.intellij.lang.impl.PsiBuilderImpl;
import com.intellij.mock.MockApplication;
import com.intellij.mock.MockProject;
import com.intellij.openapi.Disposable;
import com.intellij.openapi.application.Application;
import com.intellij.openapi.application.ApplicationManager;
import com.intellij.openapi.extensions.DefaultPluginDescriptor;
import com.intellij.openapi.extensions.PluginDescriptor;
import com.intellij.openapi.extensions.impl.ExtensionPointImpl;
import com.intellij.openapi.extensions.impl.ExtensionsAreaImpl;
import com.intellij.openapi.project.Project;
import com.jetbrains.python.PythonDialectsTokenSetContributor;
import com.jetbrains.python.PythonParserDefinition;
import com.jetbrains.python.PythonTokenSetContributor;
import com.jetbrains.python.documentation.doctest.PyDocstringTokenSetContributor;
import com.jetbrains.python.parsing.PyParser;
import com.jetbrains.python.psi.PyFile;
import com.jetbrains.python.psi.PyFileElementType;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import org.openrewrite.ExecutionContext;
import org.openrewrite.FileAttributes;
import org.openrewrite.InMemoryExecutionContext;
import org.openrewrite.Parser;
import org.openrewrite.internal.EncodingDetectingInputStream;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.internal.JavaTypeCache;
import org.openrewrite.java.tree.Space;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.tree.P;
import org.openrewrite.style.NamedStyles;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.openrewrite.Tree.randomId;

@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
public class PythonParser implements Parser<P.CompilationUnit> {
    private final List<NamedStyles> styles;
    private final boolean logCompilationWarningsAndErrors;
    private final JavaTypeCache typeCache;

    @Override
    public List<P.CompilationUnit> parse(String... sources) {
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
    public List<P.CompilationUnit> parseInputs(Iterable<Input> sources, @Nullable Path relativeTo, ExecutionContext ctx) {
        Disposable mockDisposable = () -> {
        };

        Application app = new MockApplication(mockDisposable);
        ApplicationManager.setApplication(app, mockDisposable);

        PluginDescriptor pluginDescriptor = new DefaultPluginDescriptor("io.moderne.test");

        ExtensionsAreaImpl extensionsArea = (ExtensionsAreaImpl) app.getExtensionArea();
        ExtensionPointImpl<PythonDialectsTokenSetContributor> extensionPoint = extensionsArea.registerPoint(
                PythonDialectsTokenSetContributor.EP_NAME.getName(),
                PythonDialectsTokenSetContributor.class, pluginDescriptor,
                false
        );
        extensionPoint.registerExtension(new PythonTokenSetContributor());
        extensionPoint.registerExtension(new PyDocstringTokenSetContributor());

        PyParser parser = new PyParser();
        ParserDefinition parserDefinition = new PythonParserDefinition();
        Project project = new MockProject(null, mockDisposable);

        return acceptedInputs(sources).stream().map(sourceFile -> {
            EncodingDetectingInputStream is = sourceFile.getSource(ctx);

            PyFile file = null;
            PsiBuilder psiBuilder = new PsiBuilderImpl(
                    project,
                    file,
                    parserDefinition,
                    parserDefinition.createLexer(project),
                    null,
                    is.readFully(),
                    null,
                    null
            );

            ASTNode ast = parser.parse(PyFileElementType.INSTANCE, psiBuilder);

            // FIXME Make PythonParserVisitor implement whatever visitor pattern exists in PSI,
            // and have it return a P.CompilationUnit. Replace the return statement below with the
            // call to that visitor.

            return new P.CompilationUnit(
                    randomId(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    sourceFile.getPath(),
                    FileAttributes.fromPath(sourceFile.getPath()),
                    is.getCharset().toString(),
                    is.isCharsetBomMarked(),
                    null,
                    Collections.emptyList(),
                    Collections.emptyList(),
                    Space.EMPTY
            );
        }).collect(toList());
    }

    @Override
    public boolean accept(Path path) {
        return path.toString().endsWith(".kt");
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

    public static class Builder extends Parser.Builder {
        private JavaTypeCache typeCache = new JavaTypeCache();
        private boolean logCompilationWarningsAndErrors = false;
        private final List<NamedStyles> styles = new ArrayList<>();

        public Builder() {
            super(P.CompilationUnit.class);
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

        public PythonParser build() {
            return new PythonParser(styles, logCompilationWarningsAndErrors, typeCache);
        }

        @Override
        public String getDslName() {
            return "python";
        }
    }
}
