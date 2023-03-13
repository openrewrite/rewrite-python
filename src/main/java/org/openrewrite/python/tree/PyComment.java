package org.openrewrite.python.tree;

import lombok.Value;
import lombok.With;
import org.openrewrite.Cursor;
import org.openrewrite.PrintOutputCapture;
import org.openrewrite.java.tree.Comment;
import org.openrewrite.marker.Markers;

@Value
public class PyComment implements Comment {
    String text;

    @With
    String suffix;

    @With
    boolean alignedToIndent;

    @With
    Markers markers;

    @Override
    public boolean isMultiline() {
        // Python comments can *never* span multiple lines.
        return false;
    }

    @Override
    public <P> void printComment(Cursor cursor, PrintOutputCapture<P> p) {
        p.append("#").append(text);
    }
}
