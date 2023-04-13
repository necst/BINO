import clang.cindex
from parsing.node_classes.class_definition_node import ClassDefNode
from parsing.node_classes.call_expression_node import CallExprNode
from parsing.node_classes.method_definition_node import CxxMethodDefNode
from parsing.node_classes.function_definition_node import FunctionDefNode
from parsing.utils.node_tree_str import NodeTreeStr
from parsing.utils.errors import manage_errors
from clang.cindex import CursorKind, AccessSpecifier
clang.cindex.Config.set_library_path('/usr/lib/llvm-__CLANG_VERSION__/lib/')

class CppParser(object):

    def __init__(self, file, std='', include_headers=True):
        self.file = file
        self.std = std
        self.include_headers = include_headers
        # Parsing the file
        index = clang.cindex.Index.create()
        # Args are:
        # * -x c++: specify language
        # * -std=<c++_version>
        # * -D__CODE_GENERATOR__: define for code generation
        if std:
            args = ['-x', 'c++', '-std=' +  self.std, '-D__CODE_GENERATOR__']
        else:
            args = ['-x', 'c++', '-D__CODE_GENERATOR__']
        self.root = index.parse(self.file, args).cursor

    def __str__(self):
        if self.include_headers:
            return str(NodeTreeStr(self.root))
        else:
            return str(NodeTreeStr(self.root, self.file))

    #### Public methods ####

    def get_class_definition(self, class_name):
        next_nodes = list(self.root.get_children())
        class_nodes = []
        while next_nodes:
            current_node = next_nodes.pop(0)
            if (not self.include_headers and
                    self.file != current_node.location.file.name):
                continue
            try:
                node_kind = current_node.kind
                is_definition = current_node.is_definition()
                if node_kind == CursorKind.CLASS_TEMPLATE and is_definition:
                    class_def = ClassDefNode(current_node)
                    current_class_name = class_def.get_name(templates=False)
                    if class_name == current_class_name:
                        class_nodes.append(class_def)
            except Exception as e:
                manage_errors(e)     
            next_nodes += current_node.get_children()
        if len(class_nodes) > 1:
            raise Exception("More than one class named '" + class_name + "' found.")
        if len(class_nodes) == 0:
            raise Exception("Class named '" + class_name + "' not found.")
        return class_nodes[0]


    def get_function_calls(self, function_name):
        next_nodes = list(self.root.get_children())
        function_call_nodes = []
        while next_nodes:
            current_node = next_nodes.pop(0)
            if (not self.include_headers and
                    self.file != current_node.location.file.name):
                continue
            try:
                node_kind = current_node.kind
                if node_kind == CursorKind.CALL_EXPR:
                    current_function_call_name = current_node.displayname
                    if current_function_call_name == function_name:
                        function_call_nodes.append(CallExprNode(current_node))
            except Exception as e:
                manage_errors(e)     
            next_nodes += current_node.get_children()
        return function_call_nodes


    def get_function_definitions(self, function_name, method_call=False, class_name=""):
        next_nodes = list(self.root.get_children())
        function_nodes = []
        while next_nodes:
            current_node = next_nodes.pop(0)
            if (not self.include_headers and
                    self.file != current_node.location.file.name):
                continue
            try:
                node_kind = current_node.kind
                if((node_kind == CursorKind.CXX_METHOD or
                    node_kind == CursorKind.FUNCTION_TEMPLATE) and
                    method_call and
                    current_node.spelling == function_name and
                    current_node.is_definition() and
                    (current_node.semantic_parent.kind == CursorKind.CLASS_DECL or
                    current_node.semantic_parent.kind == CursorKind.STRUCT_DECL or 
                    current_node.semantic_parent.kind == CursorKind.CLASS_TEMPLATE) and
                    current_node.semantic_parent.spelling == class_name):
                    function_nodes.append(CxxMethodDefNode(current_node))
                elif((node_kind == CursorKind.CXX_METHOD or
                    node_kind == CursorKind.FUNCTION_TEMPLATE) and
                    method_call and
                    current_node.is_definition() and
                    current_node.spelling == function_name and
                    (current_node.semantic_parent.kind == CursorKind.CLASS_DECL or
                    current_node.semantic_parent.kind == CursorKind.STRUCT_DECL or 
                    current_node.semantic_parent.kind == CursorKind.CLASS_TEMPLATE) and
                    class_name == ""):
                    function_nodes.append(CxxMethodDefNode(current_node))
                elif(node_kind == CursorKind.FUNCTION_DECL and
                    not method_call and
                    current_node.is_definition() and
                    current_node.spelling == function_name):
                    function_nodes.append(FunctionDefNode(current_node))
            except Exception as e:
                manage_errors(e)
            next_nodes += current_node.get_children()
        return function_nodes

    def get_method_calls(self):
        next_nodes = list(self.root.get_children())
        method_calls = []
        while next_nodes:
            current_node = next_nodes.pop(0)
            if (not self.include_headers and
                    current_node is not None and
                    current_node.location is not None and
                    current_node.location.file is not None and
                    current_node.location.file.name is not None and
                    self.file != current_node.location.file.name):
                continue
            try:
                node_kind = current_node.kind
                if node_kind == CursorKind.CALL_EXPR:
                    node_definition = current_node.get_definition()
                    if node_definition is not None:
                        if((node_definition.kind == CursorKind.CXX_METHOD or
                            node_definition.kind == CursorKind.FUNCTION_TEMPLATE) and
                            (node_definition.semantic_parent.kind == CursorKind.CLASS_DECL or
                            node_definition.semantic_parent.kind == CursorKind.STRUCT_DECL or 
                            node_definition.semantic_parent.kind == CursorKind.CLASS_TEMPLATE)):
                                method_called = CxxMethodDefNode(node_definition)
                                method_calls.append(method_called)
            except Exception as e:
                manage_errors(e)
            next_nodes += current_node.get_children()
        return method_calls

    def get_cursors_at_line(self, line_number, cursor_type):
        next_nodes = list(self.root.get_children())
        cursors = []
        while next_nodes:
            current_node = next_nodes.pop(0)
            if (current_node is not None and
                    current_node.location is not None and
                    current_node.location.file is not None and
                    current_node.location.file.name is not None and
                    self.file != current_node.location.file.name):
                continue
            try:
                if (current_node.location.line == line_number and
                    cursor_type == current_node.kind):
                    cursors.append(current_node)
            except Exception as e:
                manage_errors(e)
            next_nodes += current_node.get_children()
        return cursors