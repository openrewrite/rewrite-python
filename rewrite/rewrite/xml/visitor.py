from typing import cast, TypeVar

from rewrite.core import TreeVisitor
from rewrite.xml.tree.tree import *

P = TypeVar('P')

# noinspection DuplicatedCode
class XmlVisitor(TreeVisitor[Xml, P]):
    def is_acceptable(self, source_file: SourceFile, p: P) -> bool:
        return isinstance(source_file, Xml)

    def visit_document(self, document: Document, p: P) -> Xml:
        document = document.with_markers(self.visit_markers(document.markers, p))
        document = document.with_prolog(self.visit_and_cast(document.prolog, Prolog, p))
        document = document.with_root(self.visit_and_cast(document.root, Tag, p))
        return document

    def visit_prolog(self, prolog: Prolog, p: P) -> Xml:
        prolog = prolog.with_markers(self.visit_markers(prolog.markers, p))
        prolog = prolog.with_xml_decl(self.visit_and_cast(prolog.xml_decl, XmlDecl, p))
        prolog = prolog.with_misc([self.visit_and_cast(v, Misc, p) for v in prolog.misc])
        prolog = prolog.with_jsp_directives([self.visit_and_cast(v, JspDirective, p) for v in prolog.jsp_directives])
        return prolog

    def visit_xml_decl(self, xml_decl: XmlDecl, p: P) -> Xml:
        xml_decl = xml_decl.with_markers(self.visit_markers(xml_decl.markers, p))
        xml_decl = xml_decl.with_attributes([self.visit_and_cast(v, Attribute, p) for v in xml_decl.attributes])
        return xml_decl

    def visit_processing_instruction(self, processing_instruction: ProcessingInstruction, p: P) -> Xml:
        processing_instruction = processing_instruction.with_markers(self.visit_markers(processing_instruction.markers, p))
        processing_instruction = processing_instruction.with_processing_instructions(self.visit_and_cast(processing_instruction.processing_instructions, CharData, p))
        return processing_instruction

    def visit_tag(self, tag: Tag, p: P) -> Xml:
        tag = tag.with_markers(self.visit_markers(tag.markers, p))
        tag = tag.with_attributes([self.visit_and_cast(v, Attribute, p) for v in tag.attributes])
        tag = tag.with_content([self.visit_and_cast(v, Content, p) for v in tag.content])
        tag = tag.with_closing(self.visit_and_cast(tag.closing, Tag.Closing, p))
        return tag

    def visit_tag_closing(self, closing: Tag.Closing, p: P) -> Xml:
        closing = closing.with_markers(self.visit_markers(closing.markers, p))
        return closing

    def visit_attribute(self, attribute: Attribute, p: P) -> Xml:
        attribute = attribute.with_markers(self.visit_markers(attribute.markers, p))
        attribute = attribute.with_key(self.visit_and_cast(attribute.key, Ident, p))
        attribute = attribute.with_value(self.visit_and_cast(attribute.value, Attribute.Value, p))
        return attribute

    def visit_attribute_value(self, value: Attribute.Value, p: P) -> Xml:
        value = value.with_markers(self.visit_markers(value.markers, p))
        return value

    def visit_char_data(self, char_data: CharData, p: P) -> Xml:
        char_data = char_data.with_markers(self.visit_markers(char_data.markers, p))
        return char_data

    def visit_comment(self, comment: Comment, p: P) -> Xml:
        comment = comment.with_markers(self.visit_markers(comment.markers, p))
        return comment

    def visit_doc_type_decl(self, doc_type_decl: DocTypeDecl, p: P) -> Xml:
        doc_type_decl = doc_type_decl.with_markers(self.visit_markers(doc_type_decl.markers, p))
        doc_type_decl = doc_type_decl.with_name(self.visit_and_cast(doc_type_decl.name, Ident, p))
        doc_type_decl = doc_type_decl.with_external_id(self.visit_and_cast(doc_type_decl.external_id, Ident, p))
        doc_type_decl = doc_type_decl.with_internal_subset([self.visit_and_cast(v, Ident, p) for v in doc_type_decl.internal_subset])
        doc_type_decl = doc_type_decl.with_external_subsets(self.visit_and_cast(doc_type_decl.external_subsets, DocTypeDecl.ExternalSubsets, p))
        return doc_type_decl

    def visit_doc_type_decl_external_subsets(self, external_subsets: DocTypeDecl.ExternalSubsets, p: P) -> Xml:
        external_subsets = external_subsets.with_markers(self.visit_markers(external_subsets.markers, p))
        external_subsets = external_subsets.with_elements([self.visit_and_cast(v, Element, p) for v in external_subsets.elements])
        return external_subsets

    def visit_element(self, element: Element, p: P) -> Xml:
        element = element.with_markers(self.visit_markers(element.markers, p))
        element = element.with_subset([self.visit_and_cast(v, Ident, p) for v in element.subset])
        return element

    def visit_ident(self, ident: Ident, p: P) -> Xml:
        ident = ident.with_markers(self.visit_markers(ident.markers, p))
        return ident

    def visit_jsp_directive(self, jsp_directive: JspDirective, p: P) -> Xml:
        jsp_directive = jsp_directive.with_markers(self.visit_markers(jsp_directive.markers, p))
        jsp_directive = jsp_directive.with_attributes([self.visit_and_cast(v, Attribute, p) for v in jsp_directive.attributes])
        return jsp_directive
