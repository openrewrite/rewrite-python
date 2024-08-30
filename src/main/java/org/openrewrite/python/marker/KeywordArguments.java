package org.openrewrite.python.marker;

import lombok.Value;
import lombok.With;
import org.openrewrite.marker.Marker;

import java.util.UUID;

/**
 * Marks a method argument like <code>**kwargs</code>
 * as a holder of a dictionary of arguments.
 */
@Value
@With
public class KeywordArguments implements Marker {
    UUID id;
}
