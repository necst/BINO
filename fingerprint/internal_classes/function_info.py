from copy import deepcopy

class FunctionInfo(object):

    def __init__(self, function_details):
        self.mangled_name       = function_details.mangled_name
        self.optimization_level = function_details.optimization_level
        self.function_name      = function_details.function_name
        self.types              = function_details.types.copy()
        self.compiler_version   = function_details.compiler_version
        self.cpp_version        = function_details.cpp_version


    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    
    def is_info_equal(self, function_details):
        if self.mangled_name != function_details.mangled_name:
            return False
        if self.optimization_level != function_details.optimization_level:
            return False
        if self.function_name != function_details.function_name:
            return False
        if len(self.types) != len(function_details.types):
            return False
        for i in range(len(self.types)):
            if self.types[i] != function_details.types[i]:
                return False
        if self.compiler_version != function_details.compiler_version:
            return False
        if self.cpp_version != function_details.cpp_version:
            return False
        return True