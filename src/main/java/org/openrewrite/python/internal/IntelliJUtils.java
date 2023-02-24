package org.openrewrite.python.internal;

import com.intellij.configurationStore.StreamProvider;
import com.intellij.ide.plugins.PluginUtil;
import com.intellij.ide.plugins.PluginUtilImpl;
import com.intellij.ide.startup.impl.StartupManagerImpl;
import com.intellij.lang.*;
import com.intellij.lang.impl.PsiBuilderFactoryImpl;
import com.intellij.mock.MockApplication;
import com.intellij.mock.MockFileDocumentManagerImpl;
import com.intellij.mock.MockProject;
import com.intellij.mock.MockPsiManager;
import com.intellij.openapi.Disposable;
import com.intellij.openapi.application.Application;
import com.intellij.openapi.application.ApplicationManager;
import com.intellij.openapi.application.ModalityState;
import com.intellij.openapi.components.RoamingType;
import com.intellij.openapi.components.SettingsCategory;
import com.intellij.openapi.editor.Document;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.editor.EditorFactory;
import com.intellij.openapi.editor.EditorKind;
import com.intellij.openapi.editor.event.*;
import com.intellij.openapi.editor.impl.DocumentImpl;
import com.intellij.openapi.extensions.*;
import com.intellij.openapi.extensions.impl.ExtensionPointImpl;
import com.intellij.openapi.extensions.impl.ExtensionsAreaImpl;
import com.intellij.openapi.fileEditor.FileDocumentManager;
import com.intellij.openapi.fileEditor.impl.FileDocumentManagerBase;
import com.intellij.openapi.fileTypes.*;
import com.intellij.openapi.fileTypes.ex.FileTypeManagerEx;
import com.intellij.openapi.options.*;
import com.intellij.openapi.progress.ProgressManager;
import com.intellij.openapi.progress.impl.ProgressManagerImpl;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.startup.StartupManager;
import com.intellij.openapi.util.Computable;
import com.intellij.openapi.util.KeyedExtensionCollector;
import com.intellij.openapi.util.registry.Registry;
import com.intellij.openapi.vfs.VirtualFile;
import com.intellij.pom.PomModel;
import com.intellij.pom.core.impl.PomModelImpl;
import com.intellij.pom.tree.TreeAspect;
import com.intellij.psi.*;
import com.intellij.psi.impl.PsiCachedValuesFactory;
import com.intellij.psi.impl.PsiFileFactoryImpl;
import com.intellij.psi.impl.source.resolve.reference.ReferenceProvidersRegistry;
import com.intellij.psi.impl.source.resolve.reference.ReferenceProvidersRegistryImpl;
import com.intellij.psi.impl.source.tree.LeafPsiElement;
import com.intellij.psi.util.CachedValuesManager;
import com.intellij.testFramework.LightVirtualFile;
import com.intellij.util.ArrayUtil;
import com.intellij.util.CachedValuesManagerImpl;
import com.intellij.util.IncorrectOperationException;
import com.intellij.util.KeyedLazyInstance;
import com.intellij.util.messages.MessageBus;
import com.intellij.util.text.CharArrayCharSequence;
import com.jetbrains.python.*;
import com.jetbrains.python.documentation.doctest.PyDocstringTokenSetContributor;
import com.jetbrains.python.parsing.PyParser;
import com.jetbrains.python.psi.PyFile;
import com.jetbrains.python.psi.PyPsiFacade;
import com.jetbrains.python.psi.impl.PyPsiFacadeImpl;
import com.jetbrains.python.psi.impl.PythonASTFactory;
import kotlin.jvm.functions.Function1;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.openrewrite.ExecutionContext;
import org.openrewrite.Parser;
import org.openrewrite.internal.EncodingDetectingInputStream;
import org.picocontainer.ComponentAdapter;
import org.picocontainer.MutablePicoContainer;

import javax.swing.*;
import java.nio.file.Path;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.stream.Stream;

public class IntelliJUtils {

    private static <T> void registerExtensionPoint(
            PluginDescriptor pluginDescriptor,
            Application app,
            @NotNull ExtensionPointName<T> extensionPointName,
            @NotNull Class<T> aClass
    ) {
        registerExtensionPoint(pluginDescriptor, (ExtensionsAreaImpl) app.getExtensionArea(), extensionPointName, aClass);
    }

    private static <T> ExtensionPointImpl<T> registerExtensionPoint(@NotNull PluginDescriptor pluginDescriptor,
                                                                    @NotNull ExtensionsAreaImpl extensionArea,
                                                                    @NotNull BaseExtensionPointName<T> extensionPointName,
                                                                    @NotNull Class<T> extensionClass) {
        String name = extensionPointName.getName();
        if (extensionArea.hasExtensionPoint(name)) {
            return extensionArea.getExtensionPoint(name);
        } else {
            return extensionArea.registerPoint(name, extensionClass, pluginDescriptor, false);
        }
    }

    private static <T> void registerExtension(
            @NotNull PluginDescriptor pluginDescriptor,
            @NotNull Application app,
            @NotNull ExtensionPointName<T> name,
            @NotNull T extension
    ) {
        registerExtensions(pluginDescriptor, app, name, (Class<T>) extension.getClass(), Collections.singletonList(extension));
    }

    private static <T> void registerExtensions(
            @NotNull PluginDescriptor pluginDescriptor,
            @NotNull Application app,
            @NotNull ExtensionPointName<T> name,
            @NotNull Class<T> extensionClass,
            @NotNull List<? extends T> extensions
    ) {
        ExtensionsAreaImpl area = (ExtensionsAreaImpl) app.getExtensionArea();
        ExtensionPoint<T> point = area.getExtensionPointIfRegistered(name.getName());
        if (point == null) {
            point = registerExtensionPoint(pluginDescriptor, area, name, extensionClass);
        }

        for (T extension : extensions) {
            // no need to specify disposable because ParsingTestCase in any case clean area for each test
            //noinspection deprecation
            point.registerExtension(extension);
        }
    }

    private static <T> void addExplicitExtension(
            @NotNull PluginDescriptor pluginDescriptor,
            @NotNull Application app,
            @NotNull LanguageExtension<T> collector,
            @NotNull Language language,
            @NotNull T object
    ) {
        ExtensionsAreaImpl area = (ExtensionsAreaImpl) app.getExtensionArea();
        if (!area.hasExtensionPoint(collector.getName())) {
            area.registerFakeBeanPoint(collector.getName(), pluginDescriptor);
        }
        LanguageExtensionPoint<T> extension = new LanguageExtensionPoint<>(language.getID(), object);
        extension.setPluginDescriptor(pluginDescriptor);
        addExtension(area, collector, extension);
    }

    // from src/com/intellij/testFramework/ExtensionTestUtil.kt
    private static <T, BEAN_TYPE extends KeyedLazyInstance<T>, KeyT> void addExtension(
            ExtensionsAreaImpl area,
            KeyedExtensionCollector<T, KeyT> collector,
            BEAN_TYPE bean
    ) {
        ExtensionPointImpl<BEAN_TYPE> point = area.getExtensionPoint(collector.getName());
        point.registerExtension(bean);
        collector.clearCache();
    }

    private static void registerParserDefinition(
            @NotNull ExtensionPointImpl<KeyedLazyInstance<ParserDefinition>> languageParserDefinition,
            @NotNull ParserDefinition definition
    ) {
        Language language = definition.getFileNodeType().getLanguage();
        languageParserDefinition.registerExtension(new KeyedLazyInstance() {
            @Override
            public String getKey() {
                return language.getID();
            }

            @NotNull
            @Override
            public ParserDefinition getInstance() {
                return definition;
            }
        });
        LanguageParserDefinitions.INSTANCE.clearCache(language);
//        disposeOnTearDown(() -> LanguageParserDefinitions.INSTANCE.clearCache(language));
    }

    static class MockSchemeManagerFactory extends SchemeManagerFactory {
        @NotNull
        @Override
        public <SCHEME extends Scheme, MUTABLE_SCHEME extends SCHEME> SchemeManager<SCHEME> create(@NotNull String s, @NotNull SchemeProcessor<SCHEME, ? super MUTABLE_SCHEME> schemeProcessor, @Nullable String s1, @NotNull RoamingType roamingType, @NotNull Function1<? super String, String> function1, @Nullable StreamProvider streamProvider, @Nullable Path path, boolean b, @NotNull SettingsCategory settingsCategory) {
            return (SchemeManager<SCHEME>) (Object) new EmptySchemesManager();
        }
    }


    public static PyFile parsePythonSource(Parser.Input sourceFile, ExecutionContext ctx) {
        Disposable mockDisposable = () -> {
        };

        MockApplication app = MockApplication.setUp(mockDisposable);
        ApplicationManager.setApplication(app, mockDisposable);

        Registry.markAsLoaded();

        PluginDescriptor pluginDescriptor = new DefaultPluginDescriptor("io.moderne.test");

        registerExtensionPoint(pluginDescriptor, app, PythonDialectsTokenSetContributor.EP_NAME, PythonDialectsTokenSetContributor.class);
        registerExtension(pluginDescriptor, app, PythonDialectsTokenSetContributor.EP_NAME, new PythonTokenSetContributor());
        registerExtension(pluginDescriptor, app, PythonDialectsTokenSetContributor.EP_NAME, new PyDocstringTokenSetContributor());
        addExplicitExtension(pluginDescriptor, app, LanguageASTFactory.INSTANCE, PythonLanguage.getInstance(), new PythonASTFactory());

        MockProject project = new MockProject(null, mockDisposable);
        project.registerService(PyPsiFacade.class, PyPsiFacadeImpl.class);
        MockPsiManager psiManager = new MockPsiManager(project);
        PsiFileFactoryImpl psiFileFactory = new PsiFileFactoryImpl(psiManager);

//        ProjectCoreUtil.updateInternalTheOnlyProjectFieldTemporarily(project);

        MutablePicoContainer appContainer = app.getPicoContainer();
        ComponentAdapter component = appContainer.getComponentAdapter(ProgressManager.class.getName());
        if (component == null) {
            appContainer.registerComponentInstance(ProgressManager.class.getName(), new ProgressManagerImpl());
        }
        appContainer.registerComponentInstance(MessageBus.class, app.getMessageBus());
        appContainer.registerComponentInstance(SchemeManagerFactory.class, new MockSchemeManagerFactory());
        MockEditorFactory editorFactory = new MockEditorFactory();
        appContainer.registerComponentInstance(EditorFactory.class, editorFactory);
        app.registerService(FileDocumentManager.class, new MockFileDocumentManagerImpl(FileDocumentManagerBase.HARD_REF_TO_DOCUMENT_KEY,
                editorFactory::createDocument));
        app.registerService(PluginUtil.class, new PluginUtilImpl());
        app.registerService(PsiBuilderFactory.class, new PsiBuilderFactoryImpl());
        app.registerService(DefaultASTFactory.class, new DefaultASTFactoryImpl());
        app.registerService(ReferenceProvidersRegistry.class, new ReferenceProvidersRegistryImpl());
        project.registerService(PsiDocumentManager.class, new MockPsiDocumentManager());
        project.registerService(PsiManager.class, psiManager);
        project.registerService(TreeAspect.class, new TreeAspect());
        project.registerService(CachedValuesManager.class, new CachedValuesManagerImpl(project, new PsiCachedValuesFactory(project)));
        project.registerService(StartupManager.class, new StartupManagerImpl(project));
        registerExtensionPoint(pluginDescriptor, app.getExtensionArea(), FileTypeFactory.FILE_TYPE_FACTORY_EP, FileTypeFactory.class);
        registerExtensionPoint(pluginDescriptor, app.getExtensionArea(), MetaLanguage.EP_NAME, MetaLanguage.class);

        ExtensionPointImpl<KeyedLazyInstance<ParserDefinition>> langParserDefinition = app.getExtensionArea().registerFakeBeanPoint(LanguageParserDefinitions.INSTANCE.getName(), pluginDescriptor);
        ParserDefinition[] parserDefinitions = {
                new PythonParserDefinition()
        };

        {
            String fileExt = "py";
            @NotNull Language language = parserDefinitions[0].getFileNodeType().getLanguage();
            registerParserDefinition(langParserDefinition, parserDefinitions[0]);
            app.registerService(FileTypeManager.class, new MockFileTypeManager(new MockLanguageFileType(language, fileExt)));

            for (int i = 1, length = parserDefinitions.length; i < length; i++) {
                registerParserDefinition(langParserDefinition, parserDefinitions[i]);
            }
        }

        // That's for reparse routines
        project.registerService(PomModel.class, new PomModelImpl(project));

        Registry.markAsLoaded();


        PyParser parser = new PyParser();
        EncodingDetectingInputStream is = sourceFile.getSource(ctx);
        String sourceText = is.readFully();

        final FileViewProvider fileViewProvider = new SingleRootFileViewProvider(
                psiManager,
                new LightVirtualFile("test.py", PythonFileType.INSTANCE, sourceText)
        );

        return (PyFile) fileViewProvider.getPsi(PythonLanguage.INSTANCE);
    }

    static class MockPsiDocumentManager extends PsiDocumentManager {
        @Override
        @Nullable
        public PsiFile getPsiFile(@NotNull Document document) {
            throw new UnsupportedOperationException("Method getPsiFile is not yet implemented in " + getClass().getName());
        }

        @Override
        @Nullable
        public PsiFile getCachedPsiFile(@NotNull Document document) {
            throw new UnsupportedOperationException("Method getCachedPsiFile is not yet implemented in " + getClass().getName());
        }

        @Override
        @Nullable
        public Document getDocument(@NotNull PsiFile file) {
            return null;
        }

        @Override
        @Nullable
        public Document getCachedDocument(@NotNull PsiFile file) {
            VirtualFile vFile = file.getViewProvider().getVirtualFile();
            return FileDocumentManager.getInstance().getCachedDocument(vFile);
        }

        @Override
        public void commitAllDocuments() {
        }

        @Override
        public boolean commitAllDocumentsUnderProgress() {
            return true;
        }

        @Override
        public void performForCommittedDocument(@NotNull final Document document, @NotNull final Runnable action) {
            action.run();
        }

        @Override
        public void commitDocument(@NotNull Document document) {
        }

        @NotNull
        @Override
        public CharSequence getLastCommittedText(@NotNull Document document) {
            return document.getImmutableCharSequence();
        }

        @Override
        public long getLastCommittedStamp(@NotNull Document document) {
            return document.getModificationStamp();
        }

        @Nullable
        @Override
        public Document getLastCommittedDocument(@NotNull PsiFile file) {
            return null;
        }

        @Override
        public Document @NotNull [] getUncommittedDocuments() {
            throw new UnsupportedOperationException("Method getUncommittedDocuments is not yet implemented in " + getClass().getName());
        }

        @Override
        public boolean isUncommited(@NotNull Document document) {
            throw new UnsupportedOperationException("Method isUncommited is not yet implemented in " + getClass().getName());
        }

        @Override
        public boolean isCommitted(@NotNull Document document) {
            throw new UnsupportedOperationException();
        }

        @Override
        public boolean hasUncommitedDocuments() {
            throw new UnsupportedOperationException("Method hasUncommitedDocuments is not yet implemented in " + getClass().getName());
        }

        @Override
        public void commitAndRunReadAction(@NotNull Runnable runnable) {
            throw new UnsupportedOperationException("Method commitAndRunReadAction is not yet implemented in " + getClass().getName());
        }

        @Override
        public <T> T commitAndRunReadAction(@NotNull Computable<T> computation) {
            throw new UnsupportedOperationException("Method commitAndRunReadAction is not yet implemented in " + getClass().getName());
        }

        @SuppressWarnings("UnstableApiUsage")
        @Override
        public void addListener(@NotNull Listener listener) {
            throw new UnsupportedOperationException("Method addListener is not yet implemented in " + getClass().getName());
        }

        @Override
        public boolean isDocumentBlockedByPsi(@NotNull Document doc) {
            throw new UnsupportedOperationException("Method isDocumentBlockedByPsi is not yet implemented in " + getClass().getName());
        }

        @Override
        public void doPostponedOperationsAndUnblockDocument(@NotNull Document doc) {
            throw new UnsupportedOperationException(
                    "Method doPostponedOperationsAndUnblockDocument is not yet implemented in " + getClass().getName());
        }

        @Override
        public boolean performWhenAllCommitted(@NotNull Runnable action) {
            throw new UnsupportedOperationException();
        }

        @Override
        public void reparseFiles(@NotNull Collection<? extends VirtualFile> files, boolean includeOpenFiles) {
            throw new UnsupportedOperationException();
        }

        @Override
        public void performLaterWhenAllCommitted(@NotNull final Runnable runnable) {
            throw new UnsupportedOperationException();
        }

        @Override
        public void performLaterWhenAllCommitted(@NotNull ModalityState modalityState,
                                                 @NotNull Runnable runnable) {
            throw new UnsupportedOperationException();
        }
    }

    static class MockLanguageFileType extends LanguageFileType {

        private final String myExtension;

        public MockLanguageFileType(@NotNull Language language, String extension) {
            super(language);
            myExtension = extension;
        }

        @NotNull
        @Override
        public String getName() {
            return getLanguage().getID();
        }

        @NotNull
        @Override
        public String getDescription() {
            return "";
        }

        @NotNull
        @Override
        public String getDefaultExtension() {
            return myExtension;
        }

        @Override
        public Icon getIcon() {
            return null;
        }

        @Override
        public boolean equals(Object obj) {
            if (!(obj instanceof LanguageFileType)) return false;
            return getLanguage().equals(((LanguageFileType) obj).getLanguage());
        }
    }

    static class MockFileTypeManager extends FileTypeManagerEx {
        private final FileType fileType;

        public MockFileTypeManager(FileType fileType) {
            this.fileType = fileType;
        }

        @Override
        public void freezeFileTypeTemporarilyIn(@NotNull VirtualFile file, @NotNull Runnable runnable) {
        }

        @Override
        public @NotNull String getIgnoredFilesList() {
            throw new IncorrectOperationException();
        }

        @Override
        public void setIgnoredFilesList(@NotNull String list) {
        }

        @Override
        public boolean isIgnoredFilesListEqualToCurrent(@NotNull String list) {
            return false;
        }

        public void save() {
        }

        @Override
        public @NotNull String getExtension(@NotNull String fileName) {
            return "";
        }

        @Override
        @SuppressWarnings("removal")
        public void registerFileType(@NotNull FileType type, String @Nullable ... defaultAssociatedExtensions) {
        }

        @Override
        public void fireFileTypesChanged() {
        }

        @Override
        public @NotNull FileType getFileTypeByFileName(@NotNull String fileName) {
            return fileType;
        }

        @Override
        public @NotNull FileType getFileTypeByFile(@NotNull VirtualFile file) {
            return fileType;
        }

        @Override
        public @NotNull FileType getFileTypeByExtension(@NotNull String extension) {
            return fileType;
        }

        @Override
        public FileType @NotNull [] getRegisteredFileTypes() {
            return FileType.EMPTY_ARRAY;
        }

        @Override
        public boolean isFileIgnored(@NotNull String name) {
            return false;
        }

        @Override
        public boolean isFileIgnored(@NotNull VirtualFile file) {
            return false;
        }

        @Override
        @SuppressWarnings("removal")
        public String @NotNull [] getAssociatedExtensions(@NotNull FileType type) {
            return ArrayUtil.EMPTY_STRING_ARRAY;
        }

        @Override
        public void fireBeforeFileTypesChanged() {
        }

        @Override
        public void makeFileTypesChange(@NotNull String message, @NotNull Runnable command) {
            command.run();
        }

        @Override
        public FileType getKnownFileTypeOrAssociate(@NotNull VirtualFile file, @NotNull Project project) {
            return file.getFileType();
        }

        @Override
        public @NotNull List<FileNameMatcher> getAssociations(@NotNull FileType type) {
            return Collections.emptyList();
        }

        @Override
        public void associate(@NotNull FileType type, @NotNull FileNameMatcher matcher) {
        }

        @Override
        public void removeAssociation(@NotNull FileType type, @NotNull FileNameMatcher matcher) {
        }

        @Override
        public @NotNull FileType getStdFileType(@NotNull String fileTypeName) {
            if ("ARCHIVE".equals(fileTypeName)) return UnknownFileType.INSTANCE;
            if ("PLAIN_TEXT".equals(fileTypeName)) return PlainTextFileType.INSTANCE;
            if ("CLASS".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.ide.highlighter.JavaClassFileType", fileTypeName);
            if ("JAVA".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.ide.highlighter.JavaFileType", fileTypeName);
            if ("XML".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.ide.highlighter.XmlFileType", fileTypeName);
            if ("DTD".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.ide.highlighter.DTDFileType", fileTypeName);
            if ("JSP".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.ide.highlighter.NewJspFileType", fileTypeName);
            if ("JSPX".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.ide.highlighter.JspxFileType", fileTypeName);
            if ("HTML".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.ide.highlighter.HtmlFileType", fileTypeName);
            if ("XHTML".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.ide.highlighter.XHtmlFileType", fileTypeName);
            if ("JavaScript".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.lang.javascript.JavaScriptFileType", fileTypeName);
            if ("Properties".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.lang.properties.PropertiesFileType", fileTypeName);
            if ("GUI_DESIGNER_FORM".equals(fileTypeName))
                return loadFileTypeSafe("com.intellij.uiDesigner.GuiFormFileType", fileTypeName);
            return new MockLanguageFileType(PlainTextLanguage.INSTANCE, fileTypeName.toLowerCase(Locale.ENGLISH));
        }

        private static FileType loadFileTypeSafe(String className, String fileTypeName) {
            try {
                return (FileType) Class.forName(className).getField("INSTANCE").get(null);
            } catch (Exception ignored) {
                return new MockLanguageFileType(PlainTextLanguage.INSTANCE, fileTypeName.toLowerCase(Locale.ENGLISH));
            }
        }

        @Override
        public @Nullable FileType findFileTypeByName(@NotNull String fileTypeName) {
            return null;
        }
    }

    @SuppressWarnings("removal")
    static class MockEditorFactory extends EditorFactory {
        public Document createDocument(String text) {
            return new DocumentImpl(text);
        }

        @Override
        public Editor createEditor(@NotNull Document document) {
            return null;
        }

        @Override
        public Editor createViewer(@NotNull Document document) {
            return null;
        }

        @Override
        public Editor createEditor(@NotNull Document document, Project project) {
            return null;
        }

        @Override
        public Editor createEditor(@NotNull Document document, @Nullable Project project, @Nullable EditorKind kind) {
            return null;
        }

        @Override
        public Editor createEditor(@NotNull Document document, Project project, @NotNull VirtualFile file, boolean isViewer) {
            return null;
        }

        @Override
        public Editor createEditor(@NotNull Document document,
                                   Project project,
                                   @NotNull VirtualFile file,
                                   boolean isViewer,
                                   @NotNull EditorKind kind) {
            return null;
        }

        @Override
        public Editor createEditor(@NotNull final Document document, final Project project, @NotNull final FileType fileType, final boolean isViewer) {
            return null;
        }

        @Override
        public Editor createViewer(@NotNull Document document, Project project) {
            return null;
        }

        @Override
        public Editor createViewer(@NotNull Document document, @Nullable Project project, @Nullable EditorKind kind) {
            return null;
        }

        @Override
        public void releaseEditor(@NotNull Editor editor) {
        }

        @Override
        public @NotNull Stream<Editor> editors(@NotNull Document document, @Nullable Project project) {
            return Stream.empty();
        }

        @Override
        public Editor @NotNull [] getAllEditors() {
            return Editor.EMPTY_ARRAY;
        }

        @Override
        public void addEditorFactoryListener(@NotNull EditorFactoryListener listener) {
        }

        @Override
        public void addEditorFactoryListener(@NotNull EditorFactoryListener listener, @NotNull Disposable parentDisposable) {
        }

        @Override
        public void removeEditorFactoryListener(@NotNull EditorFactoryListener listener) {
        }

        @Override
        @NotNull
        public EditorEventMulticaster getEventMulticaster() {
            return new MockEditorEventMulticaster();
        }

        @Override
        @NotNull
        public Document createDocument(@NotNull CharSequence text) {
            return new DocumentImpl(text);
        }

        @Override
        @NotNull
        public Document createDocument(char @NotNull [] text) {
            return createDocument(new CharArrayCharSequence(text));
        }

        @Override
        public void refreshAllEditors() {
        }

    }

    @SuppressWarnings("removal")
    static class MockEditorEventMulticaster implements EditorEventMulticaster {
        public MockEditorEventMulticaster() {
        }

        @Override
        public void addDocumentListener(@NotNull DocumentListener listener) {
        }

        @Override
        public void addDocumentListener(@NotNull DocumentListener listener, @NotNull Disposable parentDisposable) {
        }

        @Override
        public void removeDocumentListener(@NotNull DocumentListener listener) {
        }

        @Override
        public void addEditorMouseListener(@NotNull EditorMouseListener listener) {
        }

        @Override
        public void addEditorMouseListener(@NotNull final EditorMouseListener listener, @NotNull final Disposable parentDisposable) {
        }

        @Override
        public void removeEditorMouseListener(@NotNull EditorMouseListener listener) {
        }

        @Override
        public void addEditorMouseMotionListener(@NotNull EditorMouseMotionListener listener) {
        }

        @Override
        public void addEditorMouseMotionListener(@NotNull EditorMouseMotionListener listener, @NotNull Disposable parentDisposable) {
        }

        @Override
        public void removeEditorMouseMotionListener(@NotNull EditorMouseMotionListener listener) {
        }

        @Override
        public void addCaretListener(@NotNull CaretListener listener) {
        }

        @Override
        public void addCaretListener(@NotNull CaretListener listener, @NotNull Disposable parentDisposable) {
        }

        @Override
        public void removeCaretListener(@NotNull CaretListener listener) {
        }

        @Override
        public void addSelectionListener(@NotNull SelectionListener listener) {
        }

        @Override
        public void addSelectionListener(@NotNull SelectionListener listener, @NotNull Disposable parentDisposable) {
        }

        @Override
        public void removeSelectionListener(@NotNull SelectionListener listener) {
        }

        @Override
        public void addVisibleAreaListener(@NotNull VisibleAreaListener listener) {
        }

        @Override
        public void addVisibleAreaListener(@NotNull VisibleAreaListener listener, @NotNull Disposable parent) {

        }

        @Override
        public void removeVisibleAreaListener(@NotNull VisibleAreaListener listener) {
        }

    }

    public static class PsiPrinter {
        private int depth = 0;

        private String indent() {
            StringBuilder indent = new StringBuilder();
            for (int i = 0; i < depth; i++) {
                indent.append("  ");
            }
            return indent.toString();
        }

        public void print(ASTNode node) {
            StringBuilder output = new StringBuilder();
            output.append(indent())
                    .append(node)
                    .append(" [psi=")
                    .append(node.getPsi().getClass().getSimpleName());
            if (node instanceof LeafPsiElement && !(node instanceof PsiWhiteSpace)) {
                output.append(", text=`" + node.getText() + "`");
            }
            output.append("]");

            System.out.println(output);

            depth++;
            for (ASTNode child : node.getChildren(null)) {
                print(child);
            }
            depth--;
        }
    }

}
