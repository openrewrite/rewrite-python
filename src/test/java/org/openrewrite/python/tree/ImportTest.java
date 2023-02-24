package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class ImportTest implements RewriteTest {

    @Test
    void simpleImport() {
        rewriteRun(
          python("import math")
        );
    }

    @Test
    void localImport() {
        rewriteRun(
          python("from . import foo")
        );
    }

    @Test
    void qualifiedImport() {
        rewriteRun(
          python("from math import ceil")
        );
    }

    @Test
    void simpleImportAlias() {
        rewriteRun(
          python("import math as math2")
        );
    }

    @Test
    void localImportAlias() {
        rewriteRun(
          python("from . import foo as foo2")
        );
    }

    @Test
    void qualifiedImportAlias() {
        rewriteRun(
          python("from math import ceil as ceil2")
        );
    }
}
