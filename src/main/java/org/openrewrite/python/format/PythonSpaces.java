package org.openrewrite.python.format;

import lombok.EqualsAndHashCode;
import lombok.Value;
import org.openrewrite.ExecutionContext;
import org.openrewrite.Recipe;
import org.openrewrite.TreeVisitor;

@Value
@EqualsAndHashCode(callSuper = true)
public class PythonSpaces extends Recipe {
    @Override
    public String getDisplayName() {
        return "Formats spaces in Python code";
    }

    @Override
    public String getDescription() {
        return "Standardizes spaces in Python code. Currently limited to formatting method arguments.";
    }

    @Override
    protected TreeVisitor<?, ExecutionContext> getVisitor() {
        return new PythonSpacesVisitor<>();
    }
}
