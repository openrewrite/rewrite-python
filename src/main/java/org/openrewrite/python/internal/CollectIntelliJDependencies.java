package org.openrewrite.python.internal;

import com.intellij.psi.PsiElement;
import com.jetbrains.python.psi.PyFile;
import org.openrewrite.ExecutionContext;
import org.openrewrite.InMemoryExecutionContext;
import org.openrewrite.Parser;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
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

        final Parser.Input input = new Parser.Input(file.toPath(), () -> {
            try {
                return new BufferedInputStream(new FileInputStream(file));
            } catch (FileNotFoundException e) {
                throw new RuntimeException(e);
            }
        });

        final PyFile parsed = IntelliJUtils.parsePythonSource(
                input,
                executionContext
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
