from os import listdir, chdir
from os.path import dirname, abspath, join, isdir, exists, isfile
import ast
import numpy as np

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

    def add_n_to_known(self, method_name, n):
        for method in self.known_methods:
            if method.method_name == method_name:
                method.n += n
                return
        new_method = MethodStatisticsSpecific(method_name)
        new_method.n += n
        self.known_methods.append(new_method)

    def add_tp_to_known(self, method_name, tp):
        for method in self.known_methods:
            if method.method_name == method_name:
                method.tp += tp
                return


    def add_n_to_unknown(self, method_name, n):
        for method in self.unknown_methods:
            if method.method_name == method_name:
                method.n += n
                return
        new_method = MethodStatisticsSpecific(method_name)
        new_method.n += n
        self.unknown_methods.append(new_method)


    def add_tp_to_unknown(self, method_name, tp):
        for method in self.unknown_methods:
            if method.method_name == method_name:
                method.tp += tp
                return


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


    def get_n(self):
        n = 0
        for method in self.overall_methods:
            n += method.n
        return n


    def get_tp(self):
        tp = 0
        for method in self.overall_methods:
            tp += method.tp
        return tp


    def get_fp(self):
        fp = 0
        for method in self.overall_methods:
            fp += method.fp
        return fp   



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


    def add_n_to_known(self, method_name, n, opt):
        if self.class_name + "::" + method_name not in METHODS:
            return
        for opt_stat in self.optimization_statistics:
            if opt == opt_stat.optimization:
                opt_stat.add_n_to_known(method_name, n)


    def add_tp_to_known(self, method_name, tp, opt):
        if self.class_name + "::" + method_name not in METHODS:
            return
        for opt_stat in self.optimization_statistics:
            if opt == opt_stat.optimization:
                opt_stat.add_tp_to_known(method_name, tp)


    def add_n_to_unknown(self, method_name, n, opt):
        if self.class_name + "::" + method_name not in METHODS:
            return
        for opt_stat in self.optimization_statistics:
            if opt == opt_stat.optimization:
                opt_stat.add_n_to_unknown(method_name, n)


    def add_tp_to_unknown(self, method_name, tp, opt):
        if self.class_name + "::" + method_name not in METHODS:
            return
        for opt_stat in self.optimization_statistics:
            if opt == opt_stat.optimization:
                opt_stat.add_tp_to_unknown(method_name, tp)


    def add_false_positive(self, opt, method_full_name):
        if method_full_name not in METHODS:
            return
        for opt_stat in self.optimization_statistics:
            if opt == opt_stat.optimization:
                opt_stat.add_false_positive(method_full_name.split("::")[2])        


    def merge(self):
        for opt_stat in self.optimization_statistics:
            opt_stat.merge()


    def get_n_from_opt(self, opt):
        for stat in self.optimization_statistics:
            if stat.optimization == opt:
                return stat.get_n()


    def get_tp_from_opt(self, opt):
        for stat in self.optimization_statistics:
            if stat.optimization == opt:
                return stat.get_tp()


    def get_fp_from_opt(self, opt):
        for stat in self.optimization_statistics:
            if stat.optimization == opt:
                return stat.get_fp()


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
            stats_obj.add_n_to_known(method_name, n, opt_level)
        for line in unknown_methods.split("\n"):
            if not line or line[0] != "_":
                continue
            method_name = line.split("\t")[1]
            n = int(line.split("\t")[2])
            tp = int(line.split("\t")[3])
            stats_obj.add_n_to_unknown(method_name, n, opt_level)
    return stats_obj



def parse_false_positives(git_path, stats, similarity_threshold):
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
            if "Function recognized: " in content:
                for block in content.split("Function recognized: ")[1:]:
                    false_p_function = block.split("\n")[0]
                    similarity = float(block.split("Similarity: ")[1].split("\n")[0])
                    if similarity >= similarity_threshold:
                        stats.add_false_positive(opt_level, false_p_function)


def get_methods(s):
    for line in s.split("\n"):
        if line and line[0] == "_":
            mangled = line.split("\t")[0]
            function_name = line.split("\t")[0]
            yield mangled, function_name


def get_similarity(class_name, function_name, file_path, ranges):
    f = open(file_path)
    content = f.read()
    f.close()
    recognized = content.split("Function recognized: ")
    overpos = 0
    similarity = -1
    max_matched = 0
    for recogn in recognized:
        if class_name.replace("_", "::") + "::" + function_name not in recogn:
            continue
        blocks_matched = 0
        for line in recogn.split("\n"):
            if line and line.startswith(" - "):
                block_addr = int(line.split(" - ")[1].split(":")[0], 16)
                for range_i in ranges:
                    if range_i[0] <= block_addr < range_i[1]:
                        blocks_matched += 1
                        break
        if blocks_matched > max_matched:
            max_matched = blocks_matched
            similarity = float(recogn.split("Similarity: ")[1].split("\n")[0])
    if similarity == -1:
        for recogn in recognized:
            if class_name.replace("_", "::") + "::" + function_name not in recogn:
                continue
            for line in recogn.split("\n"):    
                if line and line.startswith(" - ") and "FINAL" not in line:
                    block_addr = int(line.split(" - ")[1].split(":")[0], 16)
                    for i in range(10):
                        for range_i in ranges:
                            if range_i[0] <= block_addr + i < range_i[1]:
                                similarity = float(recogn.split("Similarity: ")[1].split("\n")[0])
                                return similarity
        print(ranges)
        print(function_name)
        raise Exception("Not found in file %s" % file_path)
    return similarity



def parse_true_positives(git_path, stats, class_name, similarity_threshold):
    file_path = join(git_path, "git_testing_output.csv")
    f = open(file_path)
    git_output = f.read()
    f.close()
    known_methods = {}  
    # List of mangled names for know and unknown
    for opt_cont in git_output.split("%"*60):
        known_methods_cont = opt_cont.split("Unknown functions:")[0]
        unknown_methods_cont = opt_cont.split("Unknown functions:")[1]
        for mangled, name in get_methods(known_methods_cont):
            if mangled not in known_methods.keys():
                known_methods[mangled] = name
    prjs_path = join(git_path, "projects")
    for prj in listdir(prjs_path):
        prj_path = join(prjs_path, prj)
        for file in listdir(prj_path):
            if "dwarf.txt" not in file:
                continue
            opt_level = file.split(prj)[1].split(".")[1]
            if opt_level not in ["-O2", "-O3", "-Os"]:
                raise Exception(file)
            f = open(join(prj_path, file))
            content = f.read()
            f.close()
            if not content:
                continue
            if "\n\n\n" not in content:
                if "Mangled name: " not in content:
                    continue
                if "Found: False" in content:
                    continue
                mangled_name = content.split("Mangled name: ")[1].split("\n")[0]
                function_name = content.split("Function name: ")[1].split("\n")[0]
                f = open(join(prj_path, file.replace("dwarf", "recognized")))
                cont_s = f.read()
                f.close()
                similarity = float(cont_s.split("Similarity: ")[1].split("\n")[0])
                if similarity < similarity_threshold:
                    continue
                if mangled_name in known_methods.keys():
                    stats.add_tp_to_known(function_name, 1, opt_level)
                else:
                    stats.add_tp_to_unknown(function_name, 1, opt_level)
            else:
                for block in content.split("\n\n\n"):
                    if "Mangled name: " not in block:
                        continue
                    if "Found: False" in block:
                        continue
                    mangled_name = block.split("Mangled name: ")[1].split("\n")[0]
                    function_name = block.split("Function name: ")[1].split("\n")[0]

                    ranges = block.split("Ranges: ")[1].split("\n")[0]
                    ranges = ast.literal_eval(ranges)
                    similarity = get_similarity(class_name, function_name, join(prj_path, file.replace("dwarf", "recognized")), ranges)
                    if similarity < similarity_threshold:
                        continue
                    if mangled_name in known_methods.keys():
                        stats.add_tp_to_known(function_name, 1, opt_level)
                    else:
                        stats.add_tp_to_unknown(function_name, 1, opt_level)


def get_case_stats(class_case_path, class_case, class_name, similarity_threshold):
    git_path = join(class_case_path, "data", "github_projects")
    stats = parse_output(git_path, class_name, class_case)
    parse_true_positives(git_path, stats, class_name, similarity_threshold)
    stats.merge()
    parse_false_positives(git_path, stats, similarity_threshold)
    return stats



def get_class_all_stats(class_name, similarity_threshold):
    for class_case in listdir(class_name):
        class_case_path = join(class_name, class_case)
        yield get_case_stats(class_case_path, class_case, class_name, similarity_threshold)


if __name__ == '__main__':
    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Changing to wd
    chdir(prj_path)
    print("Optimization\tSimilarity\tN\tTP\tFP\tRecall\tPrecision\tF1-Score")
    for opt in ["-O2", "-O3", "-Os"]:
        for similarity_threshold in np.arange(0.75, 1, 0.01):
            n = 0
            tp = 0
            fp = 0
            for class_name in listdir("."):
                if isdir(class_name):
                    for stat in get_class_all_stats(class_name, similarity_threshold):
                        n += stat.get_n_from_opt(opt)
                        tp += stat.get_tp_from_opt(opt)
                        fp += stat.get_fp_from_opt(opt)
            precision = tp / (tp + fp)
            recall = tp / n
            f1_score = 2 * ((recall * precision) / (recall + precision))
            print("%s\t%f\t%d\t%d\t%d\t%f\t%f\t%f" % (opt, similarity_threshold, n, tp, fp, recall, precision, f1_score))

