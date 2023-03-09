package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

class DelTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
            "del x",
            "del  x",
            "del x, y",
            "del  x, y",
            "del x , y",
            "del x,  y",
    })
    void del(String arg) {
        rewriteRun(python(arg));
    }

}
