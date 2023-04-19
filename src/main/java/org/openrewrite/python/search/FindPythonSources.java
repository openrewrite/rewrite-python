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
import org.openrewrite.marker.SearchResult;
import org.openrewrite.python.table.PythonSourceFile;
import org.openrewrite.python.tree.Py;
import org.openrewrite.quark.Quark;
import org.openrewrite.text.PlainText;

@Value
@EqualsAndHashCode(callSuper = true)
public class FindPythonSources extends Recipe {
    transient PythonSourceFile pythonSourceFile = new PythonSourceFile(this);

    @Override
    public String getDisplayName() {
        return "Find Python sources and collect data metrics";
    }

    @Override
    public String getDescription() {
        return "Use data table to collect source files types and counts of files with extensions `.py`.";
    }

    @Override
    protected TreeVisitor<?, ExecutionContext> getVisitor() {
        return new TreeVisitor<Tree, ExecutionContext>() {
            @Override
            public Tree visitSourceFile(SourceFile sourceFile, ExecutionContext ctx) {
                if (sourceFile.getSourcePath().toString().endsWith(".py")) {
                    PythonSourceFile.SourceFileType sourceFileType = null;
                    if (sourceFile instanceof Py.CompilationUnit) {
                        sourceFileType = PythonSourceFile.SourceFileType.Python;
                    } else if (sourceFile instanceof Quark) {
                        sourceFileType = PythonSourceFile.SourceFileType.Quark;
                    } else if (sourceFile instanceof PlainText) {
                        sourceFileType = PythonSourceFile.SourceFileType.PlainText;
                    }
                    pythonSourceFile.insertRow(ctx, new PythonSourceFile.Row(sourceFile.getSourcePath().toString(), sourceFileType));
                    return SearchResult.found(sourceFile);
                }
                return sourceFile;
            }
        };
    }
}
