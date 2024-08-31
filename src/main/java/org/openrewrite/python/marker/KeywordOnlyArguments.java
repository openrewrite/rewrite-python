package org.openrewrite.python.marker;

import lombok.Value;
import lombok.With;
import org.openrewrite.marker.Marker;

import java.util.UUID;

@Value
@With
public class KeywordOnlyArguments implements Marker {
    UUID id;
}
