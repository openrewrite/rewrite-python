package org.openrewrite.python.experimental.tree.padding;

import lombok.Value;

@Value
public class Comment implements PaddingElement {
    String text;
}
