from parsing.node_classes.function_definition_node import FunctionDefNode
from clang.cindex import CursorKind, AccessSpecifier
from parsing.enums.operator_type import OperatorType

class CxxMethodDefNode(FunctionDefNode):
    def __init__(self, node):
        if (node.kind != CursorKind.CXX_METHOD and
            node.kind != CursorKind.FUNCTION_TEMPLATE and
            node.kind != CursorKind.CONSTRUCTOR and
            node.kind != CursorKind.DESTRUCTOR and
            node.kind != CursorKind.CONVERSION_FUNCTION and
            node.semantic_parent.kind != CursorKind.CLASS_TEMPLATE and
            node.semantic_parent.kind != CursorKind.CLASS_DECL):
            raise Exception("Node is not a method definition.\nIt's a " + str(node.kind))
        super().__init__(node)
        self.class_name = node.semantic_parent.spelling
        # Setting operator type
        self.operator = OperatorType.NONE
        if self.name.startswith("operator") and len(self.name) < 12:
            self.operator = OperatorType(self.name)

    def is_method(self):
        return True

    def is_function_template(self):
        if self.node.kind == CursorKind.FUNCTION_TEMPLATE:
            return True
        else:
            return False

    def is_const_qualified(self):
        return self.node.is_const_method()

    def get_required_templates(self):
        if not self.is_function_template():
            return 0
        templates_names = []
        for child in self.node.get_children():
            if child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER:
                required = True
                for nephew in child.get_children():
                    if nephew.kind == CursorKind.TEMPLATE_REF:
                        required = False
                        break
                if required:
                    templates_names.append(child.spelling)
        return templates_names

    def get_function_name(self):
        return self.node.spelling

    def get_class_name(self, namespace=False):
        if namespace:
            from parsing.node_classes.class_definition_node import ClassDefNode
            class_def = ClassDefNode(self.node.semantic_parent)
            class_namespace = class_def.get_namespace()
            if class_namespace:
                return class_namespace + "::" + self.class_name
            else:
                return self.class_name
        else:
            return self.class_name