/*
 * Copyright 2024 the original author or authors.
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * https://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.openrewrite.python.cleanup;

import org.junit.jupiter.api.Test;
import org.openrewrite.DocumentExample;
import org.openrewrite.test.RecipeSpec;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.python.Assertions.python;

@SuppressWarnings({"PyInterpreter", "PyUnresolvedReferences"})
class StartsWithEndsWithTest implements RewriteTest {
    @Override
    public void defaults(RecipeSpec spec) {
        spec.recipe(new StartsWithEndsWith());
    }

    @Test
    @DocumentExample
    void startswithAndEndswith() {
        rewriteRun(
          python(
            """
              a_string = "ababab"
                                      
              if a_string.startswith("ab") or a_string.startswith("aba"):
                  print("Starts with ab")
                  
              if a_string.startswith("ab") or a_string.startswith("aba") or a_string.startswith("abab"):
                  print("Starts with ab")
                  
              if a_string.endswith("ab") or a_string.endswith("bab"):
                  print("Ends with ab")
              """,
            """
              a_string = "ababab"
                              
              if a_string.startswith(("ab", "aba")):
                  print("Starts with ab")
                  
              if a_string.startswith(("ab", "aba", "abab")):
                  print("Starts with ab")
                            
              if a_string.endswith(("ab", "bab")):
                  print("Ends with ab")
              """
          )
        );
    }

    @Test
    void morePositiveCases() {
        rewriteRun(
          python(
            """
              a_string = "ababab"
                            
              a_string.startswith("ab") or a_string.startswith("aba") or a_string.startswith("abab") or a_string.startswith("ababa")
              a_string.startswith("ab") or a_string.startswith(("aba", "abab"))
              a_string.startswith(("ab", "aba")) or a_string.startswith(("abab", "ababa"))
              """,
            """
              a_string = "ababab"
                              
              a_string.startswith(("ab", "aba", "abab", "ababa"))
              a_string.startswith(("ab", "aba", "abab"))
              a_string.startswith(("ab", "aba", "abab", "ababa"))
              """
          )
        );
    }

    @Test
    void negativeCases() {
        rewriteRun(
          python(
            """
              a_string = "ababab"
              b_string = "babab"
                                      
              a_string.startswith("ab")
              a_string.startswith(("ab", "aba"))
              a_string.startswith("aba") and a_string.startswith("ab")
              a_string.startswith("aba") and a_string.startswith("ab") or True
              a_string.startswith("aba") or b_string.startswith("ba")
              a_string.startswith("aba") or a_string.endswith("bab")
              """
          )
        );
    }
}
