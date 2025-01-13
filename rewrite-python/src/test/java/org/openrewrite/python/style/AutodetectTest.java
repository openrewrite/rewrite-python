/*
 * Copyright 2025 the original author or authors.
 * <p>
 * Licensed under the Moderne Source Available License (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * https://docs.moderne.io/licensing/moderne-source-available-license
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
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
