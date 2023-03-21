package org.openrewrite.python.internal;

import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Value;
import lombok.experimental.FieldDefaults;
import org.openrewrite.PrintOutputCapture;
import org.openrewrite.internal.lang.Nullable;
import org.openrewrite.java.tree.J;
import org.openrewrite.java.tree.Space;

import java.util.function.Function;

@FieldDefaults(makeFinal = true, level = AccessLevel.PUBLIC)
@AllArgsConstructor
public class PythonPrinterAdapter<
        TTree extends J,
        TLoc,
        TLeftLoc,
        TRtLoc,
        TContLoc,
        P> {

    SpaceVisitor<TLoc, P> spaceVisitor;
    Function<TLeftLoc, TLoc> getBeforeLocation;
    Function<TRtLoc, TLoc> getAfterLocation;
    Function<TContLoc, TLoc> getContainerBeforeLocation;
    Function<TContLoc, TRtLoc> getElementLocation;

    interface SpaceVisitor<TLoc, P> {
        void visitSpace(Space prefix, @Nullable TLoc loc, PrintOutputCapture<P> p);
    }
}
