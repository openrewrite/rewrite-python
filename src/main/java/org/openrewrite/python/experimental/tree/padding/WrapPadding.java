package org.openrewrite.python.experimental.tree.padding;

import lombok.Value;

@Value
public class WrapPadding {
    Padding left;
    Padding right;

    @Override
    public String toString() {
        return "{" + left + ", " + right + "}";
    }
}
