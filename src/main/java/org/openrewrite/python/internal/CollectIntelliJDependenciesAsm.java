package org.openrewrite.python.internal;

import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.signature.SignatureReader;
import org.objectweb.asm.signature.SignatureVisitor;

import java.io.IOException;
import java.net.URL;
import java.util.HashSet;
import java.util.Set;

import static org.objectweb.asm.Opcodes.ASM9;

public final class CollectIntelliJDependenciesAsm {

    public static void main(String[] args) {
        new CollectIntelliJDependenciesAsm().run();
    }

    private final Set<String> visited = new HashSet<>();

    void run() {
        processClass("org/openrewrite/python/PythonParser", Kind.ROOT);
    }

    // for debugging
    enum Kind {
        ROOT,
        CLASS,
        SIGNATURE,
        INTERFACE,
        BASE, INSTRUCTION,
    }

    void processClass(String className, Kind kind) {
        if (className == null) return;

        if (className.startsWith("[")) {
            while (className.startsWith("[")) {
                className = className.substring(1);
            }
            className = className.substring(1);
        }
        while (className.endsWith(";")) {
            className = className.substring(0, className.length() - 1);
        }

        if (className.isEmpty()) {
            return;
        }

        if (!visited.add(className)) return;

        ClassReader reader;
        try {
            reader = new ClassReader(className);
        } catch (IOException e) {
//            System.err.println("CLASS: " + className + " (" + kind + ")");
//            System.err.println("\t*** NOT FOUND");
            return;
        }

        URL classfileUrl = getClass().getClassLoader().getResource(className + ".class");
        if (classfileUrl != null && classfileUrl.getProtocol().equals("jar")) {
            String jarfile = classfileUrl.getPath().substring(0, classfileUrl.getPath().indexOf("!"));
            System.out.println("class\t" + className + "\t" + jarfile);
        }

//        try {
//            Class<?> clazz = Class.forName(className.replace("/", "."));
//        } catch (Throwable e) {
//            System.err.println("\t*** NOT FOUND: " + e);
//        }

        final int ASM_VERSION = ASM9;

        SignatureVisitor signatureVisitor = new SignatureVisitor(ASM_VERSION) {
            @Override
            public void visitClassType(String name) {
                processClass(name, Kind.SIGNATURE);
                super.visitClassType(name);
            }
        };

        MethodVisitor methodVisitor = new MethodVisitor(ASM_VERSION) {
            @Override
            public void visitTypeInsn(int opcode, String type) {
                processClass(type, Kind.INSTRUCTION);
                super.visitTypeInsn(opcode, type);
            }
        };
        ClassVisitor visitor = new ClassVisitor(ASM_VERSION) {
            @Override
            public void visit(int version, int access, String name, String signature, String superName, String[] interfaces) {
                if (signature != null) {
                    new SignatureReader(signature).accept(signatureVisitor);
                }
                processClass(superName, Kind.BASE);
                for (String iface : interfaces) {
                    processClass(iface, Kind.INTERFACE);
                }
                super.visit(version, access, name, signature, superName, interfaces);
            }

            @Override
            public MethodVisitor visitMethod(int access, String name, String descriptor, String signature, String[] exceptions) {
                if (signature != null) {
                    new SignatureReader(signature).accept(signatureVisitor);
                }
                return methodVisitor;
            }
        };
        reader.accept(visitor, 0);
    }

}
