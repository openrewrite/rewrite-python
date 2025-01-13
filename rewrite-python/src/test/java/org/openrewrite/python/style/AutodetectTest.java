package org.openrewrite.python.style;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RecipeSpec;
import org.openrewrite.test.RewriteTest;

import java.util.function.Consumer;

import static org.assertj.core.api.Assertions.assertThat;
import static org.openrewrite.python.Assertions.python;

public class AutodetectTest implements RewriteTest {

    @Test
    void autodetectSpaces2() {
        rewriteRun(
          hasIndentation(2),
          python("""
          if 1 > 0:
           print("This one-space indent will be effectively ignored")

          for i in range(1, 24):
            print(i)
            for j in range(1, i):
              x = j * j
              print(i, j)
          """)
        );
    }

    @Test
    void autodetectSpaces4() {
        rewriteRun(
          hasIndentation(4),
          python("""
          if 1 > 0:
           print("This one-space indent will be effectively ignored")

          for i in range(1, 24):
              print(i)
              for j in range(1, i):
                  x = j * j
                  print(i, j)
          """)
        );
    }

    private static Consumer<RecipeSpec> hasIndentation(int indentSize) {
        return spec -> spec.beforeRecipe(sources -> {
            Autodetect.Detector detector = Autodetect.detector();
            sources.forEach(detector::sample);

            TabsAndIndentsStyle tabsAndIndents = (TabsAndIndentsStyle) detector.build().getStyles().stream()
              .filter(TabsAndIndentsStyle.class::isInstance)
              .findAny().orElseThrow();
            assertThat(tabsAndIndents.getIndentSize()).isEqualTo(indentSize);
        });
    }
}
