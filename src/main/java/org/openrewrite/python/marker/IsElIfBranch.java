package org.openrewrite.python.marker;

import lombok.Value;
import lombok.With;
import org.openrewrite.marker.Marker;

import java.util.UUID;

/**
 * Marks a `J.If.Else` block as being part of a Python `elif`.
 * This allows `PythonPrinter` to print `elif` instead of `else if`.
 */
@Value
@With
public class IsElIfBranch implements Marker {
    UUID id;
}
