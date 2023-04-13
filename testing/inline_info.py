from utils.name_mangling import demangle

class InlineInfo(object):

    def __init__(self, binary_path, mangled_name, ranges, count):
        self.binary_path = binary_path
        self.mangled_name = mangled_name
        self.ranges = ranges
        self.basic_blocks_count = count
        self.class_name, self.function_name = demangle(mangled_name)
        self.found = False
        self.match = None


    def __str__(self):
        s = ""
        s += "Binary path: " + self.binary_path + "\n"
        s += "Mangled name: " + self.mangled_name + "\n"
        s += "Class name: " + self.class_name + "\n"
        s += "Function name: " + self.function_name + "\n"
        s += "# Basic Blocks: " + str(self.basic_blocks_count) + "\n"
        s += "Ranges: ["
        for range_i in self.ranges:
            s += "[" + hex(range_i[0]) + ", " + hex(range_i[1]) + "], "
        s = s[:-2] + "]\n"
        s += "Found: " + str(self.found) + "\n"
        s += str(self.match) + "\n"
        return s
