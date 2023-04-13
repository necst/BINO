from clang.cindex import CursorKind
from utils.name_mangling import demangle
from parsing.utils.node_tree_str import NodeTreeStr

### Auxiliar functions ###

def _get_function_path_names(name):
    path_name = ""
    if "::" in name:
        parts = name.split("::")
        path_name = "::".join(parts[:-1])
        function_name = parts[-1]
        return path_name, function_name
    return path_name, name


### Public functions ###

def is_function(node):
    node_kind = node.kind
    if(node_kind == CursorKind.CXX_METHOD or
        node_kind == CursorKind.FUNCTION_TEMPLATE or
        node_kind == CursorKind.FUNCTION_DECL or
        node_kind == CursorKind.CONSTRUCTOR or
        node_kind == CursorKind.DESTRUCTOR or
        node_kind == CursorKind.CONVERSION_FUNCTION):
        return True
    else:
        return False

def is_method(node):
    node_kind = node.kind
    if (node_kind == CursorKind.CXX_METHOD or
        node_kind == CursorKind.FUNCTION_TEMPLATE or
        node_kind == CursorKind.CONSTRUCTOR or
        node_kind == CursorKind.DESTRUCTOR or
        node_kind == CursorKind.CONVERSION_FUNCTION):
        return True
    elif node_kind == CursorKind.FUNCTION_DECL:
        return False
    else:
        raise Exception("Node is not a function definition! It's a " + str(node.kind))

def create_function_def_node(f_def):
    if is_method(f_def):
        import parsing.node_classes.method_definition_node as MDN
        return MDN.CxxMethodDefNode(f_def)
    else:
        import parsing.node_classes.function_definition_node as FDN
        return FDN.FunctionDefNode(f_def)

def strip_parenthesis(s, left_par='(', right_par=')'):
    # TODO Check parenthesis same time
    saved_operator = ""
    if left_par == '<' and "operator<<" in s:
        saved_operator = "operator<<"
        s = s.replace("operator<<", "operator$IRTOKEN$")
    elif right_par == '>' and "operator>>" in s:
        saved_operator = "operator>>"
        s = s.replace("operator>>", "operator$IRTOKEN$")
    elif left_par == '<' and "operator<" in s:
        saved_operator = "operator<"
        s = s.replace("operator<", "operator$IRTOKEN$")
    elif right_par == '>' and "operator>" in s:
        saved_operator = "operator>"
        s = s.replace("operator>", "operator$IRTOKEN$")
    elif "operator()" in s and left_par == '(':
        saved_operator = "operator()"
        s = s.replace("operator()", "operator$IRTOKEN$")
    elif "operator[]" in s and left_par == '[':
        saved_operator = "operator[]"
        s = s.replace("operator[]", "operator$IRTOKEN$")

    while(True):
        len_s = len(s)
        # Find first parenthesis
        counter = 0
        for i in range(len_s):
            if s[i] == left_par:
                counter = 1
                start = i
                break
        if counter == 0:
            s = s.replace("operator$IRTOKEN$", saved_operator)
            return s
        for i in range(start + 1, len_s):
            if s[i] == left_par:
                counter += 1
            elif s[i] == right_par:
                counter -= 1
            if counter == 0:
                end = i
                break
        if counter != 0:
            raise Exception("Unbalanced parenthesis!")
        s = s[0:start] + s[end + 1:len_s]

def mangle_names(s):
    s = get_mangled_name_without_optimization(s)
    s = demangle(s)
    s = strip_parenthesis(s)
    s = strip_parenthesis(s, "<", ">")
    s = strip_parenthesis(s, "[", "]")
    if " const" in s:
        s = s.replace(" const", "")
    if (s == "operator delete" or
        s == "operator new"):
        return _get_function_path_names(s)
    while True:
        if len(s) > 0 and s[len(s) - 1] == " ":
            s = s[:-1]
        else:
            break
    while s.count(" ") > 0:
        s = s.split(" ")[1]
    return _get_function_path_names(s)

def get_mangled_name_without_optimization(s):
    if ".isra" in s:
        return s.split(".isra")[0]
    return s