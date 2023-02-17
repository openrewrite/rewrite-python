package org.openrewrite.python.experimental;

import org.openrewrite.python.experimental.tree.CompilationUnit;

public abstract class PythonPrinter {

    public static String printToString(CompilationUnit node) {
        StringBuilder sb = new StringBuilder();
        PythonPrinter printer = new PythonPrinter() {
            @Override
            protected void append(String text) {
                sb.append(text);
            }
        };
        printer.print(node);
        return sb.toString();
    }

    protected abstract void append(String text);
    public void print(CompilationUnit node) {

    }
}
