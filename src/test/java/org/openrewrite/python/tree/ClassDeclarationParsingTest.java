package org.openrewrite.python.tree;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ClassDeclarationParsingTest implements RewriteTest {

    /*
        Unsupported spacing tests are due to lack of padding locations.

        —gary olsen, 2023-02-15
     */

    @Test
    void classDeclaration() {
        rewriteRun(
          python("""
            class Foo:
                pass
            """)
        );
    }

    @Test
    void classDeclarationSpaceAfter_FAILS() {
        Assertions.assertThrows(Throwable.class, () ->
          rewriteRun(
            python("""
              class Foo :
                  pass
              """)
          )
        );
    }


    @Test
    void classDeclarationWithBase() {
        rewriteRun(
          python("""
            class Foo(Bar):
                pass
            """)
        );
    }

    @Test
    void classDeclarationWithBaseSpaceBefore_FAILS() {
        Assertions.assertThrows(Throwable.class, () ->
          rewriteRun(
            python("""
              class Foo (Bar):
                  pass
              """)
          )
        );
    }

    @Test
    void classDeclarationWithBaseSpaceAfter_FAILS() {
        Assertions.assertThrows(Throwable.class, () ->
          rewriteRun(
            python("""
              class Foo(Bar) :
                  pass
              """)
          )
        );
    }

    @Test
    void classDeclarationWithBaseSpaceInsideLeft() {
        rewriteRun(
          python("""
            class Foo( Bar):
                pass
            """)
        );
    }

    @Test
    void classDeclarationWithBaseSpaceInsideRight_FAILS() {
        Assertions.assertThrows(Throwable.class, () ->
          rewriteRun(
            python("""
              class Foo(Bar ):
                  pass
              """)
          )
        );
    }

    @Test
    void classDeclarationWithEmptyBase() {
        rewriteRun(
          python("""
            class Foo():
                pass
            """)
        );
    }

    @Test
    void classDeclarationWithEmptyBaseSpaceBefore_FAILS() {
        Assertions.assertThrows(Throwable.class, () ->
          rewriteRun(
            python("""
              class Foo ():
                  pass
              """)
          )
        );
    }

    @Test
    void classDeclarationWithEmptyBaseSpaceAfter() {
        Assertions.assertThrows(Throwable.class, () ->
          rewriteRun(
            python("""
              class Foo() :
                  pass
              """)
          )
        );
    }

    @Test
    void classDeclarationWithEmptyBaseSpaceInside() {
        rewriteRun(
          python("""
            class Foo( ):
                pass
            """)
        );
    }

    @Test
    void classDeclarationWithMultipleBases_FAILS() {
        Assertions.assertThrows(Throwable.class, () ->
          rewriteRun(
            python("""
              class Foo(Bar1, Bar2):
                  pass
              """)
          )
        );
    }

}
