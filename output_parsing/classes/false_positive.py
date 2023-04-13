class FalsePositive(object):


    def __init__(self, repo_name, binary_name, class_name, function_name, s, bb_matched):
        self.repo_name = repo_name
        self.binary_name = binary_name
        self.class_name = class_name
        self.function_name = function_name
        self.s = s
        self.bb_matched = bb_matched


    def __str__(self):
        s = "Repository name: %s\n" % self.repo_name
        s += "Binary name: %s\n" % self.binary_name
        s += "Class name: %s\n" % self.class_name
        s += "Function name: %s\n" % self.function_name
        s += "Similarity: %f\n" % self.s
        s += "# Basic blocks matched: %d" % self.bb_matched
        return s
        

    def get_str_repr(self, spaces=2):
        s = ""
        for line in str(self):
            s += (" " * spaces) + line + "\n"
        return s[:-1]


    def get_full_name(self):
        return "%s::%s" % (self.class_name, self.function_name)