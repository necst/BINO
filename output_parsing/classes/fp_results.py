import os.path
from classes.false_positive import FalsePositive 


class FPResults(object):


    def __init__(self, f_path):
        # Reading content
        f = open(f_path)
        content = f.read()
        f.close()
        # Parsing file
        self.false_positives = []
        repo_name = content.split("Repository URL:\t")[1].split("\n")[0]
        for binary_file in content.split("Binary: "):
            if "Angr analysis time:" not in binary_file:
                continue
            binary_name = binary_file.split("\n")[0]
            for fp in binary_file.split("Function recognized: "):
                if "Similarity:" not in fp:
                    continue
                extended_name = fp.split("\n")[0]
                class_name = "::".join(extended_name.split("::")[:-1])
                function_name = extended_name.split("::")[-1]
                s = float(fp.split("Similarity: ")[1].split("\n")[0])
                bb_matched = len(fp.split(" - ")) - 1
                self.false_positives.append(FalsePositive(repo_name, binary_name, class_name, function_name, s, bb_matched))


    def get_FP(self, m=None, s=None, method_names=None):
        if m != None and type(m) != int:
            raise Exception("Error for parameter M; expected an integer!")
        if s != None and type(s) != float:
            raise Exception("Error for parameter S; expected a float!")
        if method_names != None and type(method_names) != list:
            raise Exception("Error for parameter methods; expected a list!")
        i = 0
        for false_positive in self.false_positives:
            if m != None and false_positive.bb_matched < m:
                continue
            if s != None and false_positive.s < s:
                continue
            false_positive_full_name = false_positive.get_full_name()
            if method_names != None and false_positive_full_name not in method_names:
                continue
            i += 1
        return i


    def get_FP_by_M(self, m=5):
        i = 0
        for fp in self.false_positives:
            if fp.bb_matched >= m:
                i += 1
        return i


    def get_FP_by_M_and_S(self, m=5, s=0.75):
        i = 0
        for fp in self.false_positives:
            if fp.bb_matched >= m and fp.s >= s:
                i += 1
        return i


    def filter_methods(self, keep=[]):
        i = 0
        while i < len(self.false_positives):
            if self.false_positives[i].get_full_name() in keep:
                i += 1
            else:
                self.false_positives.pop(i)