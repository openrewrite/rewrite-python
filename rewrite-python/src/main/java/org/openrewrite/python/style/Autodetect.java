package org.openrewrite.python.style;

import org.openrewrite.SourceFile;
import org.openrewrite.Tree;
import org.openrewrite.java.tree.J;
import org.openrewrite.java.tree.Statement;
import org.openrewrite.python.PythonIsoVisitor;
import org.openrewrite.python.tree.Py;
import org.openrewrite.style.NamedStyles;
import org.openrewrite.style.Style;

import java.util.*;

public class Autodetect extends NamedStyles implements PythonStyle {
    public Autodetect(UUID id, Collection<Style> styles) {
        super(id,
                "org.openrewrite.python.Autodetect",
                "Auto-detected",
                "Automatically detect styles from a repository's existing code.",
                Collections.emptySet(),
                styles);
    }

    public static Detector detector() {
        return new Detector();
    }

    public static class Detector {
        private final IndentStatistics indentStatistics = new IndentStatistics();
        private final FindIndentVisitor indentVisitor = new FindIndentVisitor();

        public void sample(SourceFile python) {
            if (python instanceof Py.CompilationUnit) {
                indentVisitor.visitNonNull(python, indentStatistics);
            }
        }

        public Autodetect build() {
            return new Autodetect(
                    Tree.randomId(),
                    Collections.singletonList(indentStatistics.getTabsAndIndentsStyle())
            );
        }
    }

    private static class IndentStatistics {
        private final Map<Integer, Integer> countsByIndentSize = new HashMap<>();

        private<T> T keyWithHighestCount(Map<T, Integer> counts) {
            int max = Collections.max(counts.values());
            return counts.entrySet()
                    .stream()
                    .filter(entry -> entry.getValue() == max)
                    .findFirst().get().getKey();
        }

        public TabsAndIndentsStyle getTabsAndIndentsStyle() {
            int mostPopularIndent = keyWithHighestCount(countsByIndentSize);
            return new TabsAndIndentsStyle(false, 2, mostPopularIndent, 4, false);
        }
    }

    private static class FindIndentVisitor extends PythonIsoVisitor<IndentStatistics> {
        private int currentBlockIndent = 0;

        private int countSpaces(String s) {
            int withoutSpaces = s.replaceAll(" ", "").length();
            return s.length() - withoutSpaces;
        }

        @Override
        public J.Block visitBlock(J.Block block, IndentStatistics indentStatistics) {
            int blockIndentBeforeThisBlock = currentBlockIndent;
            int currentBlockIndentSize = 0;

            if (!block.getStatements().isEmpty()) {
                this.currentBlockIndent = countSpaces(block.getStatements().get(0).getPrefix().getWhitespace());
                currentBlockIndentSize = this.currentBlockIndent - blockIndentBeforeThisBlock;
            }

            for (Statement s : block.getStatements()) {
                int spaceCount = countSpaces(s.getPrefix().getWhitespace());
                int relativeIndentSize = spaceCount - this.currentBlockIndent;
                int classifyAsIndentSize = relativeIndentSize + currentBlockIndentSize;
                indentStatistics.countsByIndentSize.put(classifyAsIndentSize, indentStatistics.countsByIndentSize.getOrDefault(classifyAsIndentSize, 0) + 1);
            }
            J.Block ret = super.visitBlock(block, indentStatistics);
            this.currentBlockIndent = blockIndentBeforeThisBlock;
            return ret;
        }
    }
}
