import os.path
from classes.sample import Sample


class TPResults(object):


    def __init__(self, f_path, info_path):
        # Reading content
        f = open(f_path)
        content = f.read()
        f.close()
        # Getting known methods
        known_methods = self._get_known_methods(info_path)
        # Parsing file
        self.samples = []
        repo_name = content.split("Repository URL:\t")[1].split("\n")[0]
        for sample in content.split("Binary path: "):
            if "Mangled name: " not in sample:
                continue
            binary_name = sample.split("\n")[0]
            mangled_name = sample.split("Mangled name: ")[1].split("\n")[0]
            if mangled_name in known_methods:
                known = True
            else:
                known = False
            class_name = sample.split("Class name: ")[1].split("\n")[0]
            function_name = sample.split("Function name: ")[1].split("\n")[0]
            bb_number = int(sample.split("# Basic Blocks: ")[1].split("\n")[0])
            if sample.split("Found: ")[1].split("\n")[0] == "True":
                found = True
            else:
                found = False
            if found:
                s = float(sample.split("Similarity: ")[1].split("\n")[0])
                bb_matched = len(sample.split(" - ")) - 1
            else:
                s = None
                bb_matched = None
            self.samples.append(Sample(repo_name, binary_name, mangled_name, known, class_name, function_name, bb_number, found, s, bb_matched))

            
    def _get_known_methods(self, info_path):
        # Reading content
        f = open(info_path)
        content = f.read()
        f.close()
        known = []
        if "Unknown functions:" in content:
            content = content.split("Unknown functions:")[0]
        if "Known functions:" in content:
            for line in content.split("\n"):
                if line and line[0] == '_':
                    known.append(line.split("\t")[0])
        return known
        

    def get_N(self, m=None, method_names=None, known=None):
        if m != None and type(m) != int:
            raise Exception("Error for parameter M; expected an integer!")
        if method_names != None and type(method_names) != list:
            raise Exception("Error for parameter methods; expected a list!")
        if known != None and type(known) != bool:
            raise Exception("Error for parameter known; expected a bool!")
        i = 0
        for sample in self.samples:
            if m != None and sample.bb_number < m:
                continue
            sample_full_name = sample.get_full_name()
            if method_names != None and sample_full_name not in method_names:
                continue
            if known != None and sample.known != known:
                continue
            i += 1
        return i


    def get_TP(self, m=None, s=None, method_names=None, known=None):
        if m != None and type(m) != int:
            raise Exception("Error for parameter M; expected an integer!")
        if s != None and type(s) != float:
            raise Exception("Error for parameter S; expected a float!")
        if method_names != None and type(method_names) != list:
            raise Exception("Error for parameter methods; expected a list!")
        if known != None and type(known) != bool:
            raise Exception("Error for parameter known; expected a bool!")
        i = 0
        for sample in self.samples:
            if not sample.found:
                continue
            if m != None and sample.bb_number < m:
                continue
            if s != None and sample.s < s:
                continue
            sample_full_name = sample.get_full_name()
            if method_names != None and sample_full_name not in method_names:
                continue
            if known != None and sample.known != known:
                continue
            i += 1
        return i


    def get_N_by_M(self, m=5):
        i = 0
        for sample in self.samples:
            if sample.bb_number >= m:
                i += 1
        return i


    def get_TP_by_M(self, m=5):
        i = 0
        for sample in self.samples:
            if sample.bb_number >= m and sample.found:
                i += 1
        return i


    def get_TP_by_M_and_S(self, m=5, s=0.75):
        i = 0
        for sample in self.samples:
            if sample.found and sample.bb_number >= m and sample.s >= s:
                i += 1
        return i


    def filter_methods(self, keep=[]):
        i = 0
        while i < len(self.samples):
            if self.samples[i].get_full_name() in keep:
                i += 1  
            else:
                self.samples.pop(i)