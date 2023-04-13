from parsing.node_classes.node import Node
from clang.cindex import CursorKind, AccessSpecifier

class ClassDefNode(Node):
    def __init__(self, node):
        if ((node.kind != CursorKind.CLASS_TEMPLATE and
            node.kind != CursorKind.STRUCT_DECL and
            node.kind != CursorKind.CLASS_DECL) or
            not node.is_definition()):
            raise Exception("Node is not a class.")
        super().__init__(node)
        self.name_short = node.spelling
        self.name_long = node.displayname


    def get_methods_definitions(self, access_specifier=AccessSpecifier.PUBLIC):
        methods = []
        for child in self.node.get_children():
            if ((child.kind == CursorKind.FUNCTION_TEMPLATE or
                child.kind == CursorKind.CXX_METHOD) and
                child.access_specifier == access_specifier):
                # Checking if a method isn't actually a constructor
                if (child.spelling == self.name_short or
                    child.spelling == self.name_long):
                    continue
                # Check for definition
                if not child.is_definition():
                    child = child.get_definition()
                    # It may happen that there's no definition cause it is
                    # a default operator
                    if child is None:
                        continue
                from parsing.node_classes.method_definition_node import CxxMethodDefNode
                methods.append(CxxMethodDefNode(child))
        return methods


    def get_namespace(self):
        namespace = ""
        parent = self.node.semantic_parent
        while parent is not None:
            if parent.kind == CursorKind.NAMESPACE:
                namespace = parent.spelling + "::" + namespace
            parent = parent.semantic_parent
        if len(namespace) > 0:
            namespace = namespace[:-2]
        return namespace


    def get_templates(self, optional=False):
        templates_names = []
        for child in self.node.get_children():
            if child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER:
                optional_template = False
                for nephew in child.get_children():
                    if nephew.kind == CursorKind.TEMPLATE_REF:
                        optional_template = True
                        break
                if optional or not optional_template:
                    templates_names.append(child.spelling)
        return templates_names


    def get_name(self, namespace=True, templates=True):
        if templates:
            class_name = self.name_long
        else:
            class_name = self.name_short
        if namespace:
            class_name = self.get_namespace() + "::" + class_name
        return class_name