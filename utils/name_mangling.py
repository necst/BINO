import subprocess
from utils.helper import ends_with

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

def demangle_cppfilt(name):
    cmd = ['c++filt', name]
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    demangled = (pipe.stdout.readline()).decode("ascii")
    demangled = demangled.split("\n")[0]
    return demangled

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

def remove_optimization_from_mangled(s):
    if ".isra" in s:
        return s.split(".isra")[0]
    return s

def demangle(s):
    s = remove_optimization_from_mangled(s)
    s = demangle_cppfilt(s)
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


def is_cold_symbol(s):
    if ends_with(s, ".cold"):
        return True
    return False