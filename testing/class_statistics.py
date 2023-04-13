from testing.types_statistics import TypesStatistics

class ClassStatistics(object):

    def __init__(self, query_db, class_name):
        self.class_name = class_name
        self.false_positives = 0
        self.types_statistics = TypesStatistics(query_db)


    def __str__(self):
        s = "Class name:\t" + self.class_name + "\n"
        s += "False positives:\t" + str(self.false_positives) + "\n"
        s += str(self.types_statistics)
        return s


    def add_function(self, mangled_name, function_name):
        self.types_statistics.add_function(mangled_name, function_name)


    def merge_statistics(self, class_stats):
        self.false_positives += class_stats.false_positives
        self.types_statistics.merge_statistics(class_stats.types_statistics)


    def add_found(self, mangled_name):
        self.types_statistics.add_found(mangled_name)