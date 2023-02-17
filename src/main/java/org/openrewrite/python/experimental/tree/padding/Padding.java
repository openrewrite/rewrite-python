package org.openrewrite.python.experimental.tree.padding;

import lombok.Value;
import org.openrewrite.python.experimental.tree.common.ItemList;

import java.util.Collections;

@Value
public class Padding {
    public static Padding EMPTY = new Padding(ItemList.from(Collections.emptyList()));

    ItemList<PaddingElement> elements;

    @Override
    public String toString() {
        return "Padding" + elements;
    }
}
