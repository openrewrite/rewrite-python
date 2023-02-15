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
import org.openrewrite.python.tree.P.Binary;

/**
 * Visit K types.
 */
public class PythonVisitor<Param> extends JavaVisitor<Param> {

    @Override
    public boolean isAcceptable(SourceFile sourceFile, Param param) {
        return sourceFile instanceof P.CompilationUnit;
    }

    @Override
    public String getLanguage() {
        return "python";
    }

    @Override
    public J visitJavaSourceFile(JavaSourceFile cu, Param param) {
        return cu instanceof P.CompilationUnit ? visitCompilationUnit((P.CompilationUnit) cu, param) : cu;
    }

    public J visitCompilationUnit(P.CompilationUnit cu, Param param) {
        P.CompilationUnit c = cu;
        c = c.withPrefix(visitSpace(c.getPrefix(), Space.Location.COMPILATION_UNIT_PREFIX, param));
        c = c.withMarkers(visitMarkers(c.getMarkers(), param));
        c = c.getPadding().withImports(ListUtils.map(c.getPadding().getImports(), t -> visitRightPadded(t, JRightPadded.Location.IMPORT, param)));
        c = c.withStatements(ListUtils.map(c.getStatements(), e -> visitAndCast(e, param)));
        c = c.withEof(visitSpace(c.getEof(), Space.Location.COMPILATION_UNIT_EOF, param));
        return c;
    }

    @Override
    public J visitCompilationUnit(CompilationUnit cu, Param param) {
        throw new UnsupportedOperationException("Python has a different structure for its compilation unit. See P.CompilationUnit.");
    }

    public J visitPassStatement(P.PassStatement ogPass, Param param) {
        P.PassStatement pass = ogPass;
        pass = pass.withPrefix(visitSpace(pass.getPrefix(), PSpace.Location.PASS_PREFIX, param));
        pass = pass.withMarkers(visitMarkers(pass.getMarkers(), param));
        return visitStatement(pass, param);
    }

    public J visitBinary(Binary binary, Param param) {
        Binary b = binary;
        b = b.withPrefix(visitSpace(b.getPrefix(), PSpace.Location.BINARY_PREFIX, param));
        b = b.withMarkers(visitMarkers(b.getMarkers(), param));
        Expression temp = (Expression) visitExpression(b, param);
        if (!(temp instanceof Binary)) {
            return temp;
        } else {
            b = (Binary) temp;
        }
        b = b.withLeft(visitAndCast(b.getLeft(), param));
        b = b.getPadding().withOperator(visitLeftPadded(b.getPadding().getOperator(), PLeftPadded.Location.BINARY_OPERATOR, param));
        b = b.withRight(visitAndCast(b.getRight(), param));
        b = b.withType(visitType(b.getType(), param));
        return b;
    }

    public <T> JRightPadded<T> visitRightPadded(@Nullable JRightPadded<T> right, PRightPadded.Location loc, Param p) {
        return super.visitRightPadded(right, JRightPadded.Location.LANGUAGE_EXTENSION, p);
    }

    public <T> JLeftPadded<T> visitLeftPadded(JLeftPadded<T> left, PLeftPadded.Location loc, Param p) {
        return super.visitLeftPadded(left, JLeftPadded.Location.LANGUAGE_EXTENSION, p);
    }

    public Space visitSpace(Space space, PSpace.Location loc, Param p) {
        return visitSpace(space, Space.Location.LANGUAGE_EXTENSION, p);
    }

    public <J2 extends J> JContainer<J2> visitContainer(JContainer<J2> container, PContainer.Location loc, Param p) {
        return super.visitContainer(container, JContainer.Location.LANGUAGE_EXTENSION, p);
    }
}
