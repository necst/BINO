from parsing.node_classes.node import Node
from clang.cindex import CursorKind, AccessSpecifier
from parsing.utils.helper import create_function_def_node
from parsing.utils.helper import is_function

class CallExprNode(Node):
    def __init__(self, node):
        if node.kind != CursorKind.CALL_EXPR:
            raise Exception("Node is not a function call.")
        super().__init__(node)

    ##### Public methods #####

    def object_type(self):
        object_type = None
        if self.node.get_definition():
            if(self.node.get_definition().lexical_parent.kind == CursorKind.CLASS_DECL or
                self.node.get_definition().lexical_parent.kind == CursorKind.STRUCT_DECL):
                object_type = self.node.get_definition().lexical_parent.spelling
        return object_type

    def is_plt(self):
        is_plt = True
        if self.node.get_definition():
            is_plt = False
        return is_plt

    def is_method_call(self):
        is_method_call = False
        if self.node.get_definition():
            if self.node.get_definition().lexical_parent.kind == CursorKind.CLASS_DECL:
                is_method_call = True
        return is_method_call

    def get_definition(self):
        if not self.is_plt():
            f_def = self.node.get_definition()
            # Do not actually know why the definition PARM_DECL can be the definition of a call
            # Best guess is that the parameter is actually a function to be called
            if f_def is not None and f_def.kind != CursorKind.PARM_DECL:
                return create_function_def_node(f_def)
        return None