package org.openrewrite.python.marker;

import lombok.Value;
import lombok.With;
import org.openrewrite.marker.Marker;

import java.util.UUID;

/**
 * In some contexts, the Python `None` literal is optional and can be inferred from empty expressions.
 */
@Value
@With
public class ImplicitNone implements Marker {
    UUID id;
}
