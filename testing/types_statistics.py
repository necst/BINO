from testing.function_statistics import FunctionStatistics

class TypesStatistics(object):

    def __init__(self, query_db):
        self.query_db = query_db
        self.known_functions = []
        self.unknown_functions = []


    def __str__(self):
        s = "Known functions:\n"
        s += "Mangled name\tFunction name\tCount\tFound\n"
        for func in self.known_functions:
            s += str(func) + "\n"
        s += "\n"
        s += "Unknown functions:\n"
        s += "Mangled name\tFunction name\tCount\tFound\n"
        for func in self.unknown_functions:
            s += str(func) + "\n"
        return s


    @staticmethod
    def _add_to_functions(f_collection, mangled_name, function_name):
        for func in f_collection:
            if func.mangled_name == mangled_name:
                func.count += 1
                return
        new_func = FunctionStatistics(mangled_name, function_name)
        f_collection.append(new_func)


    @staticmethod
    def _merge_function_statistics(functions_statistics_1, functions_statistics_2):
        new_functions = []
        for func_stat_2 in functions_statistics_2:
            found = False
            for func_stat_1 in functions_statistics_1:
                if func_stat_1.mangled_name == func_stat_2.mangled_name:
                    func_stat_1.count += func_stat_2.count
                    func_stat_1.found += func_stat_2.found
                    found = True
                    break
            if not found:
                new_functions.append(func_stat_2)
        if new_functions:
            functions_statistics_1 += new_functions

    @staticmethod
    def _add_found(functions_statistics, mangled_name):
        for func in functions_statistics:
            if func.mangled_name == mangled_name:
                func.found += 1
                if func.found > func.count:
                    raise Exception("Found more than the functions counted")
                return True
        return False


    def add_function(self, mangled_name, function_name):
        if self.query_db.has_exact_function(mangled_name):
            TypesStatistics._add_to_functions(self.known_functions, mangled_name, function_name)
        else:
            TypesStatistics._add_to_functions(self.unknown_functions, mangled_name, function_name)


    def merge_statistics(self, functions_statistics):
        TypesStatistics._merge_function_statistics(self.known_functions, functions_statistics.known_functions)
        TypesStatistics._merge_function_statistics(self.unknown_functions, functions_statistics.unknown_functions)


    def add_found(self, mangled_name):
        if TypesStatistics._add_found(self.known_functions, mangled_name):
            return
        if TypesStatistics._add_found(self.unknown_functions, mangled_name):
            return
        raise Exception("Function " + mangled_name + " not found!")