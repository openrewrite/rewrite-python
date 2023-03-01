package org.openrewrite.python.internal;

import org.openrewrite.internal.lang.Nullable;

public abstract class PythonOperatorLookup {
    private PythonOperatorLookup() {}

    public static @Nullable String operatorForMagicMethod(String method) {
        switch (method) {
            case "__eq__":
                return "==";
            case "__ne__":
                return "!=";
            case "__contains__":
                return "in";
            default:
                return null;
        }
    }

    public static boolean doesMagicMethodReverseOperands(String method) {
        return method.equals("__contains__");
    }
}
