/*
 * Copyright 2021 the original author or authors.
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
package org.openrewrite.python.marker;

import lombok.Value;
import lombok.With;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.JRightPadded;
import org.openrewrite.java.tree.Statement;
import org.openrewrite.marker.Marker;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Value
@With
public class GroupedStatement implements Marker {
    UUID id;
    UUID groupId;

    @Value
    public static class StatementGroup<T extends Statement> {
        int firstIndex;
        int lastIndex;
        List<T> statements;

        public boolean containsIndex(int index) {
            return index >= firstIndex && index <= lastIndex;
        }
    }

    public static <T extends Statement> @Nullable StatementGroup<T> findCurrentStatementGroup(List<JRightPadded<T>> statements, int firstIndex) {
        @Nullable UUID firstId = getGroupId(statements.get(firstIndex));
        if (firstId == null) {
            return null;
        }
        int lastIndex;
        for (lastIndex = firstIndex; lastIndex < statements.size() - 1; lastIndex++) {
            @Nullable UUID nextId = getGroupId(statements.get(lastIndex + 1));
            if (nextId == null || !nextId.equals(firstId)) {
                break;
            }
        }
        return new StatementGroup<>(
                firstIndex,
                lastIndex,
                JRightPadded.getElements(statements).subList(firstIndex, lastIndex + 1)
        );
    }

    public static <T extends Statement> @Nullable UUID getGroupId(JRightPadded<T> padded) {
        return getGroupId(padded.getElement());
    }

    public static @Nullable UUID getGroupId(Statement statement) {
        Optional<GroupedStatement> marker = statement.getMarkers().findFirst(GroupedStatement.class);
        if (marker.isPresent()) {
            return marker.get().getGroupId();
        }
        return null;
    }
}
