/*
 * Copyright 2021 the original author or authors.
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
package org.openrewrite.python.internal;

import com.intellij.psi.PsiElement;
import com.jetbrains.python.psi.PyFile;
import org.openrewrite.ExecutionContext;
import org.openrewrite.InMemoryExecutionContext;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * See `python-plugin/README.md`.
 */
public class CollectIntelliJDependencies {
    public static void main(String[] args) {
        new CollectIntelliJDependencies().processDirectory(new File("example-data"));
    }

    private final ExecutionContext executionContext = new InMemoryExecutionContext();

    private void processDirectory(File dir) {
        for (File child : dir.listFiles()) {
            if (child.isDirectory()) {
                processDirectory(child);
            } else {
                processFile(child);
            }
        }
    }

    private void processFile(File file) {
        if (!file.getName().endsWith(".py")) {
            return;
        }

        byte[] data;
        try {
            data = Files.readAllBytes(file.toPath());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        final PyFile parsed = IntelliJUtils.parsePythonSource(
            new String(data)
        );

        processNode(parsed);
    }

    // expected errors
    private static final List<String> ERROR_BLACKLIST = Arrays.asList(
            "Not a stub type",
            "Missing extension point: Pythonid.knownDecoratorProvider",
            "ResolveScopeManager.getInstance must not return null",
            "ProjectFileIndex.getInstance must not return null",
            "ProjectFileIndex.getInstance must not return null",
            "Cannot invoke \"com.jetbrains.python.psi.PyElementGenerator.createExpressionFromText(com.jetbrains.python.psi.LanguageLevel, String)\" because \"elementGenerator\" is null",
            "the return value of \"com.intellij.openapi.project.Project.getService(java.lang.Class)\" is null"
    );

    // running methods that fail constantly takes a lot of time; don't re-run methods that fail due to configuration
    private final Set<Method> blacklistedMethods = new HashSet<>();

    private void processNode(PsiElement element) {
        for (Method method : element.getClass().getMethods()) {
            runNodeMethod(element, method);
        }
        for (PsiElement child : element.getChildren()) {
            processNode(child);
        }
    }

    private void runNodeMethod(PsiElement element, Method method) {
        if (blacklistedMethods.contains(method)) {
            return;
        }

        if (!method.getName().startsWith("get") || method.getParameterCount() != 0) {
            return;
        }

        try {
            method.invoke(element);
        } catch (InvocationTargetException original) {
            boolean hadMessage = false;
            for (Throwable e = original.getTargetException(); e != null; e = e.getCause()) {
                final String message = e.getMessage();
                if (message != null) {
                    hadMessage = true;
                    for (String pattern : ERROR_BLACKLIST) {
                        if (message.contains(pattern)) {
                            System.err.println(
                                    "BLACKLISTING METHOD:\n\t" + method.getDeclaringClass().getSimpleName() + "." + method.getName() +
                                            "\n\t" + e + "\n"
                            );
                            blacklistedMethods.add(method);
                            return;
                        }
                    }
                }
            }
            if (hadMessage) {
                original.getTargetException().printStackTrace();
            } else {
                System.err.println("METHOD " + method + " FAILED WITHOUT CONTEXT DUE TO: " + original.getTargetException());
                original.getTargetException().printStackTrace();
            }
        } catch (Throwable t) {
            t.printStackTrace();
        }
    }
}
