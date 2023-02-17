package org.openrewrite.python.experimental.tree.padding;

import lombok.Value;
import org.openrewrite.python.experimental.tree.common.ItemList;

import java.util.Collections;

@Value
public class BlankLines {
    public static BlankLines EMPTY = new BlankLines(ItemList.from(Collections.emptyList()));

    ItemList<PaddingElement> elements;

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("BlankLines(");
        for (int i = 0; i < elements.size(); i++) {
            sb.append(elements.get(i).toString());
            if (i != elements.size() - 1) {
                sb.append(", ");
            }
        }
        sb.append(")");
        return sb.toString();
    }
}
