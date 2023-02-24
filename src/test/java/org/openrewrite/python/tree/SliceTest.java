package org.openrewrite.python.tree;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

public class SliceTest implements RewriteTest {

    @Test
    void sliceOperator() {
        rewriteRun(
          python("x[3:5]")
        );
    }
}
