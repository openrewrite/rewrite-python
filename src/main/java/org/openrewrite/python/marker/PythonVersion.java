package org.openrewrite.python.marker;

import lombok.EqualsAndHashCode;
import lombok.Value;
import lombok.With;
import org.openrewrite.marker.Marker;
import org.openrewrite.python.PythonParser;

import java.util.UUID;

@Value
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
@With
public class PythonVersion implements Marker {
    @EqualsAndHashCode.Include
    UUID id;

    PythonParser.LanguageLevel languageLevel;
}
