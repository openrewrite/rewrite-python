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
import org.jspecify.annotations.Nullable;
import org.openrewrite.ExecutionContext;
import org.openrewrite.InMemoryExecutionContext;
import org.openrewrite.Parser;
import org.openrewrite.SourceFile;
import org.openrewrite.java.internal.JavaTypeCache;
import org.openrewrite.python.tree.Py;
//import org.openrewrite.remote.java.RemotingClient;
import org.openrewrite.style.NamedStyles;
import org.openrewrite.tree.ParsingEventListener;
import org.openrewrite.tree.ParsingExecutionContextView;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.net.InetAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Stream;

@SuppressWarnings("unused")
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
public class PythonParser implements Parser {
    private final Collection<NamedStyles> styles;
    private final boolean logCompilationWarningsAndErrors;
    private final JavaTypeCache typeCache;
//    private @Nullable RemotingClient client;

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

//        if (client == null) {
//            client = RemotingClient.create(ctx, PythonParser.class, () -> {
//                try {
//                    return new Socket(InetAddress.getLoopbackAddress(), 54321);
//                } catch (IOException e) {
//                    throw new RuntimeException(e);
//                }
//            });
//        }

        return acceptedInputs(inputs).map(input -> {
            Path path = input.getRelativePath(relativeTo);
            parsingListener.startedParsing(input);

            // TODO temporarily commented out to avoid compilation errors in the first publish
            //  after the introduction of RemotingContext API.
//            try (EncodingDetectingInputStream is = input.getSource(ctx)) {
//                SourceFile parsed = client.runUsingSocket((socket, messenger) -> messenger.sendRequest(generator -> {
//                    generator.writeString("parse-python");
//                    generator.writeString(is.readFully());
//                }, parser -> {
//                    Tree tree = new ReceiverContext(client.getContext().newReceiver(parser), client.getContext()).receiveTree(null);
//                    return (SourceFile) tree;
//                }, socket));
//
//                Py.CompilationUnit py = (Py.CompilationUnit) parsed;
//                parsingListener.parsed(input, py);
//                return requirePrintEqualsInput(py, input, relativeTo, ctx);
//            } catch (Throwable t) {
//                ctx.getOnError().accept(t);
//                return ParseError.build(this, input, relativeTo, ctx, t);
//            }
            return null;
        });
    }

    @Override
    public boolean accept(Path path) {
        return path.toString().endsWith(".py");
    }

    @Override
    public PythonParser reset() {
        typeCache.clear();
//        if (client != null) {
//            client.getContext().reset();
//        }
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
        private JavaTypeCache typeCache = new JavaTypeCache();
        private boolean logCompilationWarningsAndErrors;
        private final Collection<NamedStyles> styles = new ArrayList<>();

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

        @Override
        public PythonParser build() {
            return new PythonParser(styles, logCompilationWarningsAndErrors, typeCache);
        }

        @Override
        public String getDslName() {
            return "python";
        }
    }
}
