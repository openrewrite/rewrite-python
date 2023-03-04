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
