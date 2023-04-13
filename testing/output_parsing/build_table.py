from os import listdir, chdir
from os.path import dirname, abspath, join, isdir, exists, isfile

METHODS = ["std::vector::push_back",
"std::vector::clear",
"std::vector::resize",
"std::vector::erase",
"std::vector::reserve",
"std::map::operator[]",
"std::map::lower_bound",
"std::map::upper_bound",
"std::map::count",
"std::map::at",
"std::map::find",
"std::deque::pop_front",
"std::deque::push_back",
"std::deque::push_front",
"std::deque::push_back",
"std::deque::operator[]"
]

class MethodStatisticsGeneral(object):

    def __init__(self, method_name):
        self.method_name = method_name
        self.n = 0
        self.tp = 0
        self.fp = 0

    def __str__(self):
        s = "%s\t%d\t%d\t%d" % (self.method_name, self.n, self.tp, self.fp)
        return s


class MethodStatisticsSpecific(object):

    def __init__(self, method_name):
        self.method_name = method_name
        self.n = 0
        self.tp = 0


    def __str__(self):
        s = "%s\t%d\t%d" % (self.method_name, self.n, self.tp)
        return s

class OptimizationStatistics(object):


    def __init__(self, optimization):
        self.optimization = optimization
        self.known_methods = []
        self.unknown_methods = []
        self.overall_methods = []
        self.f1_score = 0


    def __str__(self):
        s = "Optimization Level: %s\n" % self.optimization
        s += "F1-Score: %f\n" % self.f1_score
        s += "Overall:\n"
        for method in self.overall_methods:
            s += str(method) + "\n"
        s += "\n"
        s += "Known methods:\n"
        for method in self.known_methods:
            s += str(method) + "\n"
        s += "\n"
        s += "Unknown methods:\n"
        for method in self.unknown_methods:
            s += str(method) + "\n"
        return s[:-1]


    def compute_f1(self):
        n = 0
        tp = 0
        fp = 0
        for method in self.overall_methods:
            n += method.n
            tp += method.tp
            fp += method.fp
        precision = tp / (tp + fp)
        recall = tp / n
        self.f1_score = 2 * ((recall * precision) / (recall + precision))

    def add_to_known(self, method_name, n, tp):
        for method in self.known_methods:
            if method.method_name == method_name:
                method.n += n
                method.tp += tp
                return
        new_method = MethodStatisticsSpecific(method_name)
        new_method.n += n
        new_method.tp += tp
        self.known_methods.append(new_method)


    def add_to_unknown(self, method_name, n, tp):
        for method in self.unknown_methods:
            if method.method_name == method_name:
                method.n += n
                method.tp += tp
                return
        new_method = MethodStatisticsSpecific(method_name)
        new_method.n += n
        new_method.tp += tp
        self.unknown_methods.append(new_method)


    def add_false_positive(self, method_name):
        for method in self.overall_methods:
            if method.method_name == method_name:
                method.fp += 1


    def merge(self):
        methods = []
        for method in self.known_methods:
            if method.method_name not in methods:
                methods.append(method.method_name)
        for method in self.unknown_methods:
            if method.method_name not in methods:
                methods.append(method.method_name)
        for method_name in methods:
            self.overall_methods.append(MethodStatisticsGeneral(method_name))
        for method in self.overall_methods:
            for method_known in self.known_methods:
                if method.method_name == method_known.method_name:
                    method.n += method_known.n
                    method.tp += method_known.tp
                    break
            for method_unknown in self.unknown_methods:
                if method.method_name == method_unknown.method_name:
                    method.n += method_unknown.n
                    method.tp += method_unknown.tp
                    break
        


class Statistics(object):

    def __init__(self, class_name, case):
        self.class_name = class_name.replace("_", "::")
        self.case = case
        self.optimization_statistics = []


    def __str__(self):
        s = "Class: " + self.class_name + "\n\n"
        s += "Case: " + self.case + "\n\n"
        for opt_stat in self.optimization_statistics:
            s += str(opt_stat) + "\n\n"
        s = s[:-2]
        return s


    def compute_f1(self):
        for opt_stat in self.optimization_statistics:
            opt_stat.compute_f1()


    def add_optimization_level(self, opt):
        self.optimization_statistics.append(OptimizationStatistics(opt))


    def add_to_known(self, method_name, n, tp, opt):
        if self.class_name + "::" + method_name not in METHODS:
            print(method_name)
            return
        for opt_stat in self.optimization_statistics:
            if opt == opt_stat.optimization:
                opt_stat.add_to_known(method_name, n, tp)


    def add_to_unknown(self, method_name, n, tp, opt):
        if self.class_name + "::" + method_name not in METHODS:
            return
        for opt_stat in self.optimization_statistics:
            if opt == opt_stat.optimization:
                opt_stat.add_to_unknown(method_name, n, tp)


    def add_false_positive(self, opt, method_full_name):
        if method_full_name not in METHODS:
            return
        for opt_stat in self.optimization_statistics:
            if opt == opt_stat.optimization:
                opt_stat.add_false_positive(method_full_name.split("::")[2])        


    def merge(self):
        for opt_stat in self.optimization_statistics:
            opt_stat.merge()


def parse_output(git_path, class_name, class_case):
    file_path = join(git_path, "git_testing_output.csv")
    stats_obj = Statistics(class_name, class_case)
    f = open(file_path)
    content = f.read()
    f.close()
    for opt_cont in content.split("%" * 60):
        opt_level = opt_cont.split("Optimization level:\t")[1].split("\n")[0]
        stats_obj.add_optimization_level(opt_level)
        known_methods = opt_cont.split("Unknown functions:")[0]
        unknown_methods = opt_cont.split("Unknown functions:")[1]
        for line in known_methods.split("\n"):
            if not line or line[0] != "_":
                continue
            method_name = line.split("\t")[1]
            n = int(line.split("\t")[2])
            tp = int(line.split("\t")[3])
            stats_obj.add_to_known(method_name, n, tp, opt_level)
        for line in unknown_methods.split("\n"):
            if not line or line[0] != "_":
                continue
            method_name = line.split("\t")[1]
            n = int(line.split("\t")[2])
            tp = int(line.split("\t")[3])
            stats_obj.add_to_unknown(method_name, n, tp, opt_level)
    return stats_obj



def parse_false_positives(git_path, stats):
    prjs_path = join(git_path, "projects")
    for prj in listdir(prjs_path):
        prj_path = join(prjs_path, prj)
        for file in listdir(prj_path):
            if "false.txt" not in file:
                continue
            opt_level = file.split(prj)[1].split(".")[1]
            if opt_level not in ["-O2", "-O3", "-Os"]:
                raise Exception(file)
            f = open(join(prj_path, file))
            content = f.read()
            f.close()
            for line in content.split("\n"):
                if "Function recognized: " not in line:
                    continue
                false_p_function = line.split("Function recognized: ")[1].split("\n")[0]
                stats.add_false_positive(opt_level, false_p_function)



def get_case_stats(class_case_path, class_case, class_name):
    git_path = join(class_case_path, "data", "github_projects")
    stats = parse_output(git_path, class_name, class_case)
    stats.merge()
    parse_false_positives(git_path, stats)
    stats.compute_f1()
    print("&&&&&&&&")
    print(stats)



def get_class_all_stats(class_name):
    for class_case in listdir(class_name):
        class_case_path = join(class_name, class_case)
        stat_case = get_case_stats(class_case_path, class_case, class_name)


if __name__ == '__main__':
    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Changing to wd
    chdir(prj_path)
    for class_name in listdir("."):
        if isdir(class_name):
            class_all_stats = get_class_all_stats(class_name)
