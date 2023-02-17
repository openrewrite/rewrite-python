package org.openrewrite.python.experimental.tree.padding;

import lombok.Value;

@Value
public class ColonPadding {
    Padding beforeColon;
    Padding afterColon;
    BlankLines blankLinesFollowing;
}
