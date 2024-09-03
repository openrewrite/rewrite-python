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
import org.openrewrite.*;
import org.openrewrite.internal.EncodingDetectingInputStream;
import org.openrewrite.java.internal.JavaTypeCache;
import org.openrewrite.python.tree.Py;
import org.openrewrite.remote.ReceiverContext;
import org.openrewrite.remote.RemotingContext;
import org.openrewrite.remote.RemotingExecutionContextView;
import org.openrewrite.remote.java.RemotingClient;
import org.openrewrite.style.NamedStyles;
import org.openrewrite.text.PlainTextParser;
import org.openrewrite.tree.ParseError;
import org.openrewrite.tree.ParsingEventListener;
import org.openrewrite.tree.ParsingExecutionContextView;

import java.io.*;
import java.net.InetAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static java.util.Collections.singletonList;
import static java.util.Objects.requireNonNull;

@SuppressWarnings("unused")
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
public class PythonParser implements Parser {
    private final Collection<NamedStyles> styles;
    private final boolean logCompilationWarningsAndErrors;
    private final JavaTypeCache typeCache;
    private final List<Path> pythonPath;

    private @Nullable Process pythonProcess;
    private @Nullable RemotingContext remotingContext;
    private @Nullable RemotingClient client;

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
        if (!ensureServerRunning(ctx)) {
            return PlainTextParser.builder().build().parseInputs(inputs, relativeTo, ctx);
        }

        ParsingExecutionContextView pctx = ParsingExecutionContextView.view(ctx);
        ParsingEventListener parsingListener = pctx.getParsingListener();

        return acceptedInputs(inputs).map(input -> {
            Path path = input.getRelativePath(relativeTo);
            parsingListener.startedParsing(input);

            try (EncodingDetectingInputStream is = input.getSource(ctx)) {
                SourceFile parsed = client.runUsingSocket((socket, messenger) -> requireNonNull(messenger.sendRequest(generator -> {
                            if (input.isSynthetic() || !Files.isRegularFile(input.getPath())) {
                                generator.writeString("parse-python-source");
                                generator.writeString(is.readFully());
                            } else {
                                generator.writeString("parse-python-file");
                                generator.writeString(input.getPath().toString());
                            }
                        }, parser -> {
                            Tree tree = new ReceiverContext(remotingContext.newReceiver(parser), remotingContext).receiveTree(null);
                            return (SourceFile) tree;
                        }, socket)))
                        .withSourcePath(path)
                        .withFileAttributes(FileAttributes.fromPath(input.getPath()))
                        .withCharset(getCharset(ctx));

                if (parsed instanceof ParseError) {
                    ctx.getOnError().accept(new AssertionError(parsed));
                    return parsed;
                }

                Py.CompilationUnit py = (Py.CompilationUnit) parsed;
                parsingListener.parsed(input, py);
                return requirePrintEqualsInput(py, input, relativeTo, ctx);
            } catch (Throwable t) {
                ctx.getOnError().accept(t);
                return ParseError.build(this, input, relativeTo, ctx, t);
            }
        });
    }

    private boolean ensureServerRunning(ExecutionContext ctx) {
        if (client == null || !isAlive()) {
            try {
                initializeRemoting(ctx);
            } catch (IOException e) {
                return false;
            }
        } else {
            requireNonNull(remotingContext).reset();
        }
        return client != null && isAlive();
    }

    private boolean isAlive() {
        try {
            return requireNonNull(client).runUsingSocket((socket, messenger) -> {
                messenger.sendReset(socket);
                return true;
            });
        } catch (Exception e) {
            return false;
        }
    }

    private void initializeRemoting(ExecutionContext ctx) throws IOException {
        RemotingExecutionContextView view = RemotingExecutionContextView.view(ctx);
        remotingContext = view.getRemotingContext();
        if (remotingContext == null) {
            remotingContext = new RemotingContext(PythonParser.class.getClassLoader(), false);
            view.setRemotingContext(remotingContext);
        } else {
            remotingContext.reset();
        }

        int port = 54322;
        if (!isServerRunning(port)) {
            ProcessBuilder processBuilder = new ProcessBuilder("python3", "-m", "rewrite.remote.server", Integer.toString(port));
            if (!pythonPath.isEmpty()) {
                Map<String, String> environment = processBuilder.environment();
                environment.compute("PYTHONPATH", (k, current) ->
                        (current != null ? current + File.pathSeparator : "") + pythonPath.stream().map(Path::toString).collect(Collectors.joining(File.pathSeparator)));
            }
            if (System.getProperty("os.name").startsWith("Windows")) {
                processBuilder.redirectOutput(new File("NUL"));
                processBuilder.redirectError(new File("NUL"));
            } else {
                processBuilder.redirectOutput(new File("/dev/null"));
                processBuilder.redirectError(new File("/dev/null"));
            }
            pythonProcess = processBuilder.start();
            for (int i = 0; i < 5 && pythonProcess.isAlive(); i++) {
                if (isServerRunning(port)) {
                    break;
                }
                try {
                    Thread.sleep(50);
                } catch (InterruptedException ignore) {
                }
            }

            if (pythonProcess == null || !pythonProcess.isAlive()) {
                remotingContext = null;
                return;
            }
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                if (pythonProcess != null && pythonProcess.isAlive()) {
                    pythonProcess.destroy();
                }
            }));
        }

        client = RemotingClient.create(ctx, PythonParser.class, () -> {
            try {
                return new Socket(InetAddress.getLoopbackAddress(), port);
            } catch (IOException e) {
                throw new UncheckedIOException(e);
            }
        });
    }

    public static boolean isServerRunning(int port) {
        try (Socket socket = new Socket(InetAddress.getLoopbackAddress(), port)) {
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    @Override
    public boolean accept(Path path) {
        return path.toString().endsWith(".py");
    }

    @Override
    public PythonParser reset() {
        typeCache.clear();
        if (remotingContext != null) {
            remotingContext.reset();
            remotingContext = null;
        }
        if (pythonProcess != null) {
            pythonProcess.destroy();
            pythonProcess = null;
        }
        client = null;
        return this;
    }

    @Override
    public Path sourcePathFromSourceText(Path prefix, String sourceCode) {
        return prefix.resolve("file.py");
    }

    public static Builder builder() {
        return new Builder();
    }

    public static Builder usingRemotingInstallation(Path dir) {
        try {
            return verifyRemotingInstallation(dir);
        } catch (IOException | InterruptedException ignore) {
        }
        return builder();
    }

    private static Builder verifyRemotingInstallation(Path dir) throws IOException, InterruptedException {
        if (!Files.isDirectory(dir)) {
            Files.createDirectories(dir);
        }

        try (InputStream inputStream = requireNonNull(PythonParser.class.getClassLoader().getResourceAsStream("META-INF/python-requirements.txt"))) {
            List<String> packages = new BufferedReader(new InputStreamReader(inputStream)).lines().filter(l -> !l.isEmpty()).collect(Collectors.toList());

            List<String> command = new ArrayList<>(Arrays.asList("python3", "-m", "pip", "install", "--target", dir.toString()));
            command.addAll(packages);

            ProcessBuilder processBuilder = new ProcessBuilder(command);
            Process process = processBuilder.start();

            int exitCode = process.waitFor();
            return new Builder().pythonPath(singletonList(dir));
        }
    }

    @SuppressWarnings("unused")
    public static class Builder extends Parser.Builder {
        private JavaTypeCache typeCache = new JavaTypeCache();
        private boolean logCompilationWarningsAndErrors;
        private final Collection<NamedStyles> styles = new ArrayList<>();
        private List<Path> pythonPath = new ArrayList<>();

        private Builder() {
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

        public Builder pythonPath(List<Path> path) {
            this.pythonPath = new ArrayList<>(path);
            return this;
        }

        @Override
        public PythonParser build() {
            return new PythonParser(styles, logCompilationWarningsAndErrors, typeCache, pythonPath);
        }

        @Override
        public String getDslName() {
            return "python";
        }
    }
}
