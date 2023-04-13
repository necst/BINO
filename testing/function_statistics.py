class FunctionStatistics(object):

    def __init__(self, mangled_name, function_name, count=1, found=0):
        self.mangled_name = mangled_name
        self.function_name = function_name
        self.count = count
        self.found = found


    def __str__(self):
        s = self.mangled_name + "\t" 
        s += self.function_name + "\t"
        s += str(self.count) + "\t"
        s += str(self.found)
        return s