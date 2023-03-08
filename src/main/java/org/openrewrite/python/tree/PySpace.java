/*
 * Copyright 2023 the original author or authors.
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
package org.openrewrite.python.tree;

public class PySpace {
    public enum Location {
        ASSERT_PREFIX,
        ASSERT_ELEMENT_SUFFIX,
        AWAIT_PREFIX,
        COMPREHENSION_CLAUSE_PREFIX,
        COMPREHENSION_CONDITION_PREFIX,
        COMPREHENSION_IN,
        COMPREHENSION_PREFIX,
        COMPREHENSION_SUFFIX,
        DEL_ELEMENT_SUFFIX,
        DEL_PREFIX,
        DICT_ENTRY,
        DICT_ENTRY_KEY_SUFFIX,
        DICT_LITERAL_ELEMENT_SUFFIX,
        DICT_LITERAL_PREFIX,
        EXCEPTION_TYPE_PREFIX,
        ERROR_FROM_PREFIX,
        ERROR_FROM_SOURCE,
        KEY_VALUE_PREFIX,
        KEY_VALUE_SUFFIX,
        MATCH_CASE_GUARD,
        MATCH_CASE_PREFIX,
        MATCH_PATTERN_PREFIX,
        MATCH_PATTERN_ELEMENT_PREFIX,
        MATCH_PATTERN_ELEMENT_SUFFIX,
        PASS_PREFIX,
        SPECIAL_PARAM_PREFIX,
        TOP_LEVEL_STATEMENT,
        VARIABLE_SCOPE_NAME_SUFFIX,
        VARIABLE_SCOPE_PREFIX,
        YIELD_FROM_PREFIX,
        YIELD_PREFIX,
        YIELD_ELEMENT_SUFFIX,
    }
}
