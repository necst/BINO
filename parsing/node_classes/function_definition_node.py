from parsing.node_classes.node import Node
from clang.cindex import CursorKind, AccessSpecifier, StorageClass
from parsing.utils.errors import manage_errors
from parsing.utils.helper import create_function_def_node
from parsing.utils.helper import is_method
from parsing.type_classes.type import Type

class FunctionDefNode(Node):
    def __init__(self, node):
        if not (node.kind == CursorKind.CXX_METHOD or
            node.kind == CursorKind.FUNCTION_TEMPLATE or
            node.kind == CursorKind.FUNCTION_DECL or
            node.kind == CursorKind.CONSTRUCTOR or
            node.kind == CursorKind.DESTRUCTOR or
            node.kind == CursorKind.CONVERSION_FUNCTION):
            raise Exception("Node is not a function definition.")
        super().__init__(node)
        self.name = node.spelling
        self.mangled_name = node.mangled_name

    def get_called_functions(self):
        next_nodes = list(self.node.get_children())
        function_call_nodes = []
        while next_nodes:
            current_node = next_nodes.pop(0)
            try:
                node_kind = current_node.kind
                if node_kind == CursorKind.CALL_EXPR:
                    import parsing.node_classes.call_expression_node as CEN
                    function_call_nodes.append(CEN.CallExprNode(current_node))
            except Exception as e:
                manage_errors(e)    
            next_nodes += current_node.get_children()
        return function_call_nodes


    def is_method(self):
        return False


    def is_static(self):
        if self.node.storage_class == StorageClass.STATIC:
            return True
        else:
            return False


    def get_return_type(self):
        return Type(self.node.type.get_result())


    def get_parameters_types(self):
        arguments = []
        if self.node.kind == CursorKind.FUNCTION_TEMPLATE:
            for child in self.node.get_children():
                if child.kind == CursorKind.PARM_DECL:
                    arguments.append(Type(child.type))
        else:
            for t in self.node.get_arguments():
                arguments.append(Type(t.type))
        return arguments

    def is_inline_declared(self):
        print(dir(self.node))
        print((self.node.displayname))
        input()
