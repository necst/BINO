class MatchingConfigs(object):

    def __init__(self):
        self.output_file = None
        self.classes = None
        self.color_checking = True
        self.function_call_checking = True
        self.similarity_threshold = 0.75
        self.minimum_basic_blocks = 5
        self.use_static_symbols = False
        self.processes = 1

    
    def __str__(self):
        return self.pp(spaces=0)


    def toJSON(self):
        return ""


    def pp(self, spaces=2):
        spaces_chars = spaces * " "
        s = ""
        if self.output_file is None:
            s += spaces_chars + "Output file: stdout\n"
        else:
            s += spaces_chars + "Output file: %s\n" % self.output_file
        if self.classes is None:
            s += spaces_chars + "Classes tested: All available\n"
        else:
            s += spaces_chars + "Classes tested: %s\n" % self.classes
        s += spaces_chars + "Using static symbols: %s\n" % self.use_stati_symbols
        s += spaces_chars + "Minimum basic blocks: %d\n" % self.minimum_basic_blocks
        s += spaces_chars + "Processes: %d\n" % self.processes
        s += spaces_chars + "Function call checking: %s\n" % str(self.function_call_checking)
        s += spaces_chars + "Color checking: %s\n" % str(self.color_checking)
        if self.color_checking:
            s += spaces_chars + "Similarity threshold: %f\n" % self.similarity_threshold
        return s[:-1]
