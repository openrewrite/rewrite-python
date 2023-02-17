package org.openrewrite.python.experimental.tree.padding;

import lombok.Value;

import java.util.regex.Pattern;

@Value
public class WhiteSpace implements PaddingElement {
    private static Pattern VALID_PATTERN = Pattern.compile("^([ \t\f\n]|(\\[\n]))+$");
    private static Pattern VALID_TOPLEVEL_PATTERN = Pattern.compile("^([ \t\f]|(\\[\n]))+$");

    String text;

    public boolean isValid() {
        return VALID_PATTERN.matcher(text).matches();
    }

    public boolean isValidTopLevelPattern() {
        return VALID_TOPLEVEL_PATTERN.matcher(text).matches();
    }

    @Override
    public String toString() {
        final String escaped = text.replaceAll("\n", "\\\\n").replaceAll("\t", "\\\\t");
        return "WS(" + escaped + ")";
    }
}
