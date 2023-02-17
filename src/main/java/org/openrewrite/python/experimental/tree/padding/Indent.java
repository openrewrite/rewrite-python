package org.openrewrite.python.experimental.tree.padding;


import lombok.Value;

import java.util.regex.Pattern;

@Value
public class Indent {
    private static Pattern VALID_PATTERN = Pattern.compile("^[ \t]*$");

    String text;

    public boolean isValid() {
        return VALID_PATTERN.matcher(text).matches();
    }
}
