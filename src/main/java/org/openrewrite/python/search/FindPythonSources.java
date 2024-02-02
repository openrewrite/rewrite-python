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
import org.openrewrite.*;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.marker.SearchResult;
import org.openrewrite.python.marker.PythonVersion;
import org.openrewrite.python.table.PythonSourceFile;
import org.openrewrite.python.tree.Py;
import org.openrewrite.quark.Quark;
import org.openrewrite.text.PlainText;

@Value
@EqualsAndHashCode(callSuper = false)
public class FindPythonSources extends Recipe {
    transient PythonSourceFile pythonSourceFile = new PythonSourceFile(this);

    @Override
    public String getDisplayName() {
        return "Find Python sources and collect metrics on them";
    }

    @Override
    public String getDescription() {
        return "Creates a data table which contains detailed information about all `.py` files such as where those files are and what version of Python is being used.";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new TreeVisitor<Tree, ExecutionContext>() {
            @Override
            public @Nullable Tree visit(@Nullable Tree tree, ExecutionContext ctx) {
                if (!(tree instanceof SourceFile)) {
                    return tree;
                }
                SourceFile sourceFile = (SourceFile) tree;
                if (sourceFile.getSourcePath().toString().endsWith(".py")) {
                    PythonSourceFile.SourceFileType sourceFileType = null;
                    String languageLevel = "";
                    if (sourceFile instanceof Py.CompilationUnit) {
                        PythonVersion level = sourceFile.getMarkers().findFirst(PythonVersion.class).orElse(null);
                        languageLevel = level == null ? "Not found" : level.getLanguageLevel().name();
                        sourceFileType = PythonSourceFile.SourceFileType.Python;
                    } else if (sourceFile instanceof Quark) {
                        sourceFileType = PythonSourceFile.SourceFileType.Quark;
                    } else if (sourceFile instanceof PlainText) {
                        sourceFileType = PythonSourceFile.SourceFileType.PlainText;
                    }
                    pythonSourceFile.insertRow(ctx, new PythonSourceFile.Row(sourceFile.getSourcePath().toString(), sourceFileType, languageLevel));
                    return SearchResult.found(sourceFile);
                }
                return sourceFile;
            }
        };
    }
}
