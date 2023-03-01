package org.openrewrite.python.marker;

import lombok.*;
import org.openrewrite.marker.Marker;

import java.util.UUID;

/**
 * In Python, many operators are actually syntax sugar for method calls.
 * For example, <pre>a == b</pre> is syntax sugar for <pre>a.__eq__(b)</pre>.
 * This marker is for binary operators that were de-sugared to call expressions to fit into the Java language model.
 */
@Value
@With
public class MagicMethodDesugar implements Marker {
    UUID id;
}
