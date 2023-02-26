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

import org.openrewrite.SourceFile;
import org.openrewrite.internal.ListUtils;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.JavaVisitor;
import org.openrewrite.java.tree.*;
import org.openrewrite.java.tree.J.CompilationUnit;
import org.openrewrite.python.tree.*;

/**
 * Visit K types.
 */
public class PythonVisitor<P> extends JavaVisitor<P> {

    @Override
    public boolean isAcceptable(SourceFile sourceFile, P p) {
        return sourceFile instanceof Py.CompilationUnit;
    }

    @Override
    public String getLanguage() {
        return "python";
    }

    @Override
    public J visitJavaSourceFile(JavaSourceFile cu, P p) {
        return cu instanceof Py.CompilationUnit ? visitCompilationUnit((Py.CompilationUnit) cu, p) : cu;
    }

    public J visitCompilationUnit(Py.CompilationUnit cu, P p) {
        Py.CompilationUnit c = cu;
        c = c.withPrefix(visitSpace(c.getPrefix(), Space.Location.COMPILATION_UNIT_PREFIX, p));
        c = c.withMarkers(visitMarkers(c.getMarkers(), p));
        c = c.getPadding().withImports(ListUtils.map(c.getPadding().getImports(), t -> visitRightPadded(t, JRightPadded.Location.IMPORT, p)));
        c = c.withStatements(ListUtils.map(c.getStatements(), e -> visitAndCast(e, p)));
        c = c.withEof(visitSpace(c.getEof(), Space.Location.COMPILATION_UNIT_EOF, p));
        return c;
    }

    @Override
    public J visitCompilationUnit(CompilationUnit cu, P p) {
        throw new UnsupportedOperationException("Python has a different structure for its compilation unit. See P.CompilationUnit.");
    }

    public J visitPassStatement(Py.PassStatement ogPass, P p) {
        Py.PassStatement pass = ogPass;
        pass = pass.withPrefix(visitSpace(pass.getPrefix(), PSpace.Location.PASS_PREFIX, p));
        pass = pass.withMarkers(visitMarkers(pass.getMarkers(), p));
        return visitStatement(pass, p);
    }

    public <T> JRightPadded<T> visitRightPadded(@Nullable JRightPadded<T> right, PRightPadded.Location loc, P p) {
        return super.visitRightPadded(right, JRightPadded.Location.LANGUAGE_EXTENSION, p);
    }

    public <T> JLeftPadded<T> visitLeftPadded(JLeftPadded<T> left, PLeftPadded.Location loc, P p) {
        return super.visitLeftPadded(left, JLeftPadded.Location.LANGUAGE_EXTENSION, p);
    }

    public Space visitSpace(Space space, PSpace.Location loc, P p) {
        return visitSpace(space, Space.Location.LANGUAGE_EXTENSION, p);
    }

    public <J2 extends J> JContainer<J2> visitContainer(JContainer<J2> container, PContainer.Location loc, P p) {
        return super.visitContainer(container, JContainer.Location.LANGUAGE_EXTENSION, p);
    }
}
