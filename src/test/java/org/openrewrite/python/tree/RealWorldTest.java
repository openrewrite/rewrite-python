package org.openrewrite.python.tree;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.openrewrite.test.RewriteTest;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;

import static org.openrewrite.python.Assertions.python;

public class RealWorldTest implements RewriteTest {

    @ParameterizedTest
    @ValueSource(strings = {
      "example-data/airflow/airflow/datasets/manager.py"
    })
    public void test(String filename) throws IOException {
        File file = new File(filename);
        String source = Files.readString(file.toPath());
        rewriteRun(python(source));
    }

}
