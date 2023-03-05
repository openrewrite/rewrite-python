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

import lombok.*;
import lombok.experimental.FieldDefaults;
import lombok.experimental.NonFinal;
import org.openrewrite.*;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.internal.TypesInUse;
import org.openrewrite.java.tree.*;
import org.openrewrite.marker.Markers;
import org.openrewrite.python.PythonVisitor;
import org.openrewrite.python.internal.PythonPrinter;

import java.beans.Transient;
import java.lang.ref.SoftReference;
import java.lang.ref.WeakReference;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

public interface Py extends J {

    @SuppressWarnings("unchecked")
    @Override
    default <R extends Tree, P> R accept(TreeVisitor<R, P> v, P p) {
        return (R) acceptPython(v.adapt(PythonVisitor.class), p);
    }

    @Override
    default <P> boolean isAcceptable(TreeVisitor<?, P> v, P p) {
        return v.isAdaptableTo(PythonVisitor.class);
    }

    @Nullable
    default <P> J acceptPython(PythonVisitor<P> v, P p) {
        return v.defaultValue(this, p);
    }

    Space getPrefix();

    default List<Comment> getComments() {
        return getPrefix().getComments();
    }

    @ToString
    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @RequiredArgsConstructor
    @AllArgsConstructor(access = AccessLevel.PRIVATE)
    final class CompilationUnit implements Py, JavaSourceFile, SourceFile {
        @Nullable
        @NonFinal
        transient SoftReference<TypesInUse> typesInUse;

        @Nullable
        @NonFinal
        transient WeakReference<Padding> padding;

        @EqualsAndHashCode.Include
        @With
        @Getter
        UUID id;

        @With
        @Getter
        Space prefix;

        @With
        @Getter
        Markers markers;

        @With
        @Getter
        Path sourcePath;

        @With
        @Getter
        @Nullable
        FileAttributes fileAttributes;

        @Nullable // for backwards compatibility
        @With(AccessLevel.PRIVATE)
        String charsetName;

        @With
        @Getter
        boolean charsetBomMarked;

        @With
        @Getter
        @Nullable
        Checksum checksum;

        @Override
        public Charset getCharset() {
            return charsetName == null ? StandardCharsets.UTF_8 : Charset.forName(charsetName);
        }

        @SuppressWarnings("unchecked")
        @Override
        public SourceFile withCharset(Charset charset) {
            return withCharsetName(charset.name());
        }

        List<JRightPadded<Import>> imports;

        public List<Import> getImports() {
            return JRightPadded.getElements(imports);
        }

        public Py.CompilationUnit withImports(List<Import> imports) {
            return getPadding().withImports(JRightPadded.withElements(this.imports, imports));
        }

        List<JRightPadded<Statement>> statements;

        public List<Statement> getStatements() {
            return JRightPadded.getElements(statements);
        }

        public Py.CompilationUnit withStatements(List<Statement> statements) {
            return getPadding().withStatements(JRightPadded.withElements(this.statements, statements));
        }

        @With
        @Getter
        Space eof;

        @Transient
        public List<ClassDeclaration> getClasses() {
            return statements.stream()
                    .map(JRightPadded::getElement)
                    .filter(J.ClassDeclaration.class::isInstance)
                    .map(J.ClassDeclaration.class::cast)
                    .collect(Collectors.toList());
        }

        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            return v.visitJavaSourceFile(this, p);
        }

        @Override
        public <P> TreeVisitor<?, PrintOutputCapture<P>> printer(Cursor cursor) {
            return new PythonPrinter<>();
        }

        @Transient
        public TypesInUse getTypesInUse() {
            TypesInUse cache;
            if (this.typesInUse == null) {
                cache = TypesInUse.build(this);
                this.typesInUse = new SoftReference<>(cache);
            } else {
                cache = this.typesInUse.get();
                if (cache == null || cache.getCu() != this) {
                    cache = TypesInUse.build(this);
                    this.typesInUse = new SoftReference<>(cache);
                }
            }
            return cache;
        }

        @Override
        public @Nullable Package getPackageDeclaration() {
            return null;
        }

        @Override
        public JavaSourceFile withPackageDeclaration(Package pkg) {
            throw new IllegalStateException("Python does not support package declarations");
        }

        public Padding getPadding() {
            Padding p;
            if (this.padding == null) {
                p = new Padding(this);
                this.padding = new WeakReference<>(p);
            } else {
                p = this.padding.get();
                if (p == null || p.t != this) {
                    p = new Padding(this);
                    this.padding = new WeakReference<>(p);
                }
            }
            return p;
        }

        @RequiredArgsConstructor
        public static class Padding implements JavaSourceFile.Padding {
            private final Py.CompilationUnit t;

            @Override
            public List<JRightPadded<Import>> getImports() {
                return t.imports;
            }

            @Override
            public Py.CompilationUnit withImports(List<JRightPadded<Import>> imports) {
                return t.imports == imports ? t : new Py.CompilationUnit(t.id, t.prefix, t.markers, t.sourcePath, t.fileAttributes, t.charsetName, t.charsetBomMarked, null,
                        imports, t.statements, t.eof);
            }

            public List<JRightPadded<Statement>> getStatements() {
                return t.statements;
            }

            public Py.CompilationUnit withStatements(List<JRightPadded<Statement>> statements) {
                return t.statements == statements ? t : new Py.CompilationUnit(t.id, t.prefix, t.markers, t.sourcePath,
                        t.fileAttributes, t.charsetName, t.charsetBomMarked, t.checksum, t.imports, statements, t.eof);
            }
        }
    }

    @ToString
    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @AllArgsConstructor
    final class ExpressionStatement implements Py, Expression, Statement {
        @With
        @Getter
        UUID id;

        @With
        @Getter
        Expression expression;

        // For backwards compatibility with older ASTs before there was an id field
        @SuppressWarnings("unused")
        public ExpressionStatement(Expression expression) {
            this.id = Tree.randomId();
            this.expression = expression;
        }

        @Override
        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            J j = v.visit(getExpression(), p);
            if (j instanceof ExpressionStatement) {
                return j;
            } else if (j instanceof Expression) {
                return withExpression((Expression) j);
            }
            return j;
        }

        @Override
        public <P2 extends J> P2 withPrefix(Space space) {
            return (P2) withExpression(expression.withPrefix(space));
        }

        @Override
        public Space getPrefix() {
            return expression.getPrefix();
        }

        @Override
        public <P2 extends Tree> P2 withMarkers(Markers markers) {
            return (P2) withExpression(expression.withMarkers(markers));
        }

        @Override
        public Markers getMarkers() {
            return expression.getMarkers();
        }

        @Override
        public @Nullable JavaType getType() {
            return expression.getType();
        }

        @Override
        public <T extends J> T withType(@Nullable JavaType type) {
            //noinspection unchecked
            return (T) withExpression(expression.withType(type));
        }

        @Transient
        @Override
        public CoordinateBuilder.Statement getCoordinates() {
            return new CoordinateBuilder.Statement(this);
        }
    }

    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @RequiredArgsConstructor
    @AllArgsConstructor(access = AccessLevel.PRIVATE)
    final class KeyValue implements Py, Expression, TypedTree {
        @Nullable
        @NonFinal
        transient WeakReference<Padding> padding;

        @Getter
        @With
        @EqualsAndHashCode.Include
        UUID id;

        @Getter
        @With
        Space prefix;

        @Getter
        @With
        Markers markers;

        JRightPadded<Expression> key;

        public Expression getKey() {
            return key.getElement();
        }

        public KeyValue withKey(@Nullable Expression key) {
            return getPadding().withKey(JRightPadded.withElement(this.key, key));
        }

        @Getter
        @With
        Expression value;

        @Getter
        @With
        @Nullable
        JavaType type;

        @Override
        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            return v.visitKeyValue(this, p);
        }

        @Transient
        @Override
        public CoordinateBuilder.Expression getCoordinates() {
            return new CoordinateBuilder.Expression(this);
        }

        public Padding getPadding() {
            Padding p;
            if (this.padding == null) {
                p = new Padding(this);
                this.padding = new WeakReference<>(p);
            } else {
                p = this.padding.get();
                if (p == null || p.t != this) {
                    p = new Padding(this);
                    this.padding = new WeakReference<>(p);
                }
            }
            return p;
        }

        @RequiredArgsConstructor
        public static class Padding {
            private final KeyValue t;

            @Nullable
            public JRightPadded<Expression> getKey() {
                return t.key;
            }

            public KeyValue withKey(@Nullable JRightPadded<Expression> key) {
                return t.key == key ? t : new KeyValue(t.id, t.prefix, t.markers, key, t.value, t.type);
            }
        }
    }

    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @RequiredArgsConstructor
    @AllArgsConstructor(access = AccessLevel.PRIVATE)
    final class DictLiteral implements Py, Expression, TypedTree {
        @Nullable
        @NonFinal
        transient WeakReference<Padding> padding;

        @Getter
        @With
        @EqualsAndHashCode.Include
        UUID id;

        @Getter
        @With
        Space prefix;

        @Getter
        @With
        Markers markers;

        JContainer<KeyValue> elements;

        public List<KeyValue> getElements() {
            return elements.getElements();
        }

        public DictLiteral withElements(List<KeyValue> elements) {
            return getPadding().withElements(JContainer.withElements(this.elements, elements));
        }

        @Getter
        @With
        @Nullable
        JavaType type;

        @Override
        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            return v.visitDictLiteral(this, p);
        }

        @Override
        @Transient
        public CoordinateBuilder.Expression getCoordinates() {
            return new CoordinateBuilder.Expression(this);
        }

        public Padding getPadding() {
            Padding p;
            if (this.padding == null) {
                p = new Padding(this);
                this.padding = new WeakReference<>(p);
            } else {
                p = this.padding.get();
                if (p == null || p.t != this) {
                    p = new Padding(this);
                    this.padding = new WeakReference<>(p);
                }
            }
            return p;
        }

        @RequiredArgsConstructor
        public static class Padding {
            private final DictLiteral t;

            public JContainer<KeyValue> getElements() {
                return t.elements;
            }

            public DictLiteral withElements(JContainer<KeyValue> elements) {
                return t.elements == elements ? t : new DictLiteral(t.id, t.prefix, t.markers, elements, t.type);
            }
        }
    }

    @ToString
    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @AllArgsConstructor
    final class PassStatement implements Py, Statement {
        @With
        @Getter
        UUID id;

        @With
        @Getter
        Space prefix;

        @With
        @Getter
        Markers markers;

        @Override
        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            return v.visitPassStatement(this, p);
        }

        @Transient
        @Override
        public CoordinateBuilder.Statement getCoordinates() {
            return new CoordinateBuilder.Statement(this);
        }
    }

    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @RequiredArgsConstructor
    final class ComprehensionExpression implements Py, Expression {

        public enum Kind {
            LIST, SET, DICT, GENERATOR
        }

        @With
        @Getter
        @EqualsAndHashCode.Include
        UUID id;

        @With
        @Getter
        Space prefix;

        @With
        @Getter
        Markers markers;

        @With
        @Getter
        Kind kind;

        @With
        @Getter
        Expression result;

        @Getter
        @With
        List<Clause> clauses;

        @With
        @Getter
        Space suffix;

        @Getter
        @With
        @Nullable
        JavaType type;

        @Override
        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            return v.visitComprehensionExpression(this, p);
        }

        @Transient
        @Override
        public CoordinateBuilder.Expression getCoordinates() {
            return new CoordinateBuilder.Expression(this);
        }

        @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
        @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
        @RequiredArgsConstructor
        public static final class Condition implements Py {
            @With
            @Getter
            @EqualsAndHashCode.Include
            UUID id;

            @With
            @Getter
            Space prefix;

            @With
            @Getter
            Markers markers;

            @With
            @Getter
            Expression expression;

            @Override
            public <P> J acceptPython(PythonVisitor<P> v, P p) {
                return v.visitComprehensionCondition(this, p);
            }

        }

        @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
        @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
        @RequiredArgsConstructor
        @AllArgsConstructor(access = AccessLevel.PRIVATE)
        public static final class Clause implements Py {
            @Nullable
            @NonFinal
            transient WeakReference<Padding> padding;

            @With
            @Getter
            @EqualsAndHashCode.Include
            UUID id;

            @With
            @Getter
            Space prefix;

            @With
            @Getter
            Markers markers;

            @With
            @Getter
            Expression iteratorVariable;

            JLeftPadded<Expression> iteratedList;

            @With
            @Getter
            @Nullable
            List<Condition> conditions;

            public Expression getIteratedList() {
                return this.iteratedList.getElement();
            }

            public Clause withIteratedList(Expression expression) {
                return this.getPadding().withIteratedList(this.iteratedList.withElement(expression));
            }

            @Override
            public <P> J acceptPython(PythonVisitor<P> v, P p) {
                return v.visitComprehensionClause(this, p);
            }

            public Padding getPadding() {
                Padding p;
                if (this.padding == null) {
                    p = new Padding(this);
                    this.padding = new WeakReference<>(p);
                } else {
                    p = this.padding.get();
                    if (p == null || p.t != this) {
                        p = new Padding(this);
                        this.padding = new WeakReference<>(p);
                    }
                }
                return p;
            }

            @RequiredArgsConstructor
            public static class Padding {
                private final Clause t;

                public JLeftPadded<Expression> getIteratedList() {
                    return t.iteratedList;
                }

                public Clause withIteratedList(JLeftPadded<Expression> iteratedList) {
                    return t.iteratedList == iteratedList ? t : new Clause(t.id, t.prefix, t.markers, t.iteratorVariable, iteratedList, t.conditions);
                }
            }
        }
    }

    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @RequiredArgsConstructor
    final class AwaitExpression implements Py, Expression {
        @With
        @Getter
        @EqualsAndHashCode.Include
        UUID id;

        @With
        @Getter
        Space prefix;

        @With
        @Getter
        Markers markers;

        @With
        @Getter
        Expression expression;

        @With
        @Getter
        JavaType type;

        @Override
        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            return v.visitAwaitExpression(this, p);
        }

        public CoordinateBuilder.Expression getCoordinates() {
            return new CoordinateBuilder.Expression(this);
        }

    }

    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @RequiredArgsConstructor
    @AllArgsConstructor(access = AccessLevel.PRIVATE)
    final class YieldExpression implements Py, Expression {
        @Nullable
        @NonFinal
        transient WeakReference<Padding> padding;

        @With
        @Getter
        @EqualsAndHashCode.Include
        UUID id;

        @With
        @Getter
        Space prefix;

        @With
        @Getter
        Markers markers;

        JLeftPadded<Boolean> from;

        List<JRightPadded<Expression>> expressions;

        @With
        @Getter
        JavaType type;

        public boolean isFrom() {
            return this.from.getElement();
        }

        public YieldExpression withFrom(boolean from) {
            return this.getPadding().withFrom(JLeftPadded.withElement(this.from, from));
        }

        public List<Expression> getExpressions() {
            return JRightPadded.getElements(expressions);
        }

        public YieldExpression withExpressions(List<Expression> expressions) {
            return this.getPadding().withExpressions(JRightPadded.withElements(this.expressions, expressions));
        }


        @Override
        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            return v.visitYieldExpression(this, p);
        }

        public CoordinateBuilder.Expression getCoordinates() {
            return new CoordinateBuilder.Expression(this);
        }

        public Padding getPadding() {
            Padding p;
            if (this.padding == null) {
                p = new Padding(this);
                this.padding = new WeakReference<>(p);
            } else {
                p = this.padding.get();
                if (p == null || p.t != this) {
                    p = new Padding(this);
                    this.padding = new WeakReference<>(p);
                }
            }
            return p;
        }

        @RequiredArgsConstructor
        public static class Padding {
            private final YieldExpression t;

            public JLeftPadded<Boolean> getFrom() {
                return t.from;
            }

            public YieldExpression withFrom(JLeftPadded<Boolean> from) {
                return from == t.from ? t : new YieldExpression(t.id, t.prefix, t.markers, from, t.expressions, t.type);
            }


            public List<JRightPadded<Expression>> getExpressions() {
                return t.expressions;
            }

            public YieldExpression withExpressions(List<JRightPadded<Expression>> expressions) {
                return expressions == t.expressions
                        ? t
                        : new YieldExpression(t.id, t.prefix, t.markers, t.from, expressions, t.type);
            }
        }

    }

    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @RequiredArgsConstructor
    @AllArgsConstructor(access = AccessLevel.PRIVATE)
    final class AssertStatement implements Py, Statement {
        @Nullable
        @NonFinal
        transient WeakReference<Padding> padding;

        @With
        @Getter
        @EqualsAndHashCode.Include
        UUID id;

        @With
        @Getter
        Space prefix;

        @With
        @Getter
        Markers markers;

        List<JRightPadded<Expression>> expressions;

        public List<Expression> getExpressions() {
            return JRightPadded.getElements(expressions);
        }

        public AssertStatement withExpressions(List<Expression> expressions) {
            return this.getPadding().withExpressions(JRightPadded.withElements(this.expressions, expressions));
        }

        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            return v.visitAssertStatement(this, p);
        }

        public CoordinateBuilder.Statement getCoordinates() {
            return new CoordinateBuilder.Statement(this);
        }

        public Padding getPadding() {
            Padding p;
            if (this.padding == null) {
                p = new Padding(this);
                this.padding = new WeakReference<>(p);
            } else {
                p = this.padding.get();
                if (p == null || p.t != this) {
                    p = new Padding(this);
                    this.padding = new WeakReference<>(p);
                }
            }
            return p;
        }

        @RequiredArgsConstructor
        public static class Padding {
            private final AssertStatement t;

            public List<JRightPadded<Expression>> getExpressions() {
                return t.expressions;
            }

            public AssertStatement withExpressions(List<JRightPadded<Expression>> expressions) {
                return expressions == t.expressions
                        ? t
                        : new AssertStatement(t.id, t.prefix, t.markers, expressions);
            }
        }
    }

    @FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
    @EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
    @RequiredArgsConstructor
    @AllArgsConstructor(access = AccessLevel.PRIVATE)
    final class DelStatement implements Py, Statement {
        @Nullable
        @NonFinal
        transient WeakReference<Padding> padding;

        @With
        @Getter
        @EqualsAndHashCode.Include
        UUID id;

        @With
        @Getter
        Space prefix;

        @With
        @Getter
        Markers markers;

        List<JRightPadded<Expression>> targets;

        public List<Expression> getTargets() {
            return JRightPadded.getElements(targets);
        }

        public DelStatement withTargets(List<Expression> expressions) {
            return this.getPadding().withTargets(JRightPadded.withElements(this.targets, expressions));
        }

        public <P> J acceptPython(PythonVisitor<P> v, P p) {
            return v.visitDelStatement(this, p);
        }

        public CoordinateBuilder.Statement getCoordinates() {
            return new CoordinateBuilder.Statement(this);
        }

        public Padding getPadding() {
            Padding p;
            if (this.padding == null) {
                p = new Padding(this);
                this.padding = new WeakReference<>(p);
            } else {
                p = this.padding.get();
                if (p == null || p.t != this) {
                    p = new Padding(this);
                    this.padding = new WeakReference<>(p);
                }
            }
            return p;
        }

        @RequiredArgsConstructor
        public static class Padding {
            private final DelStatement t;

            public List<JRightPadded<Expression>> getTargets() {
                return t.targets;
            }

            public DelStatement withTargets(List<JRightPadded<Expression>> expressions) {
                return expressions == t.targets
                        ? t
                        : new DelStatement(t.id, t.prefix, t.markers, expressions);
            }
        }
    }

}
