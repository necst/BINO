from testing.inline_info import InlineInfo
from textwrap import indent


class InlineSummary(object):

    def __init__(self):
        self.inline_info = []


    def __str__(self):
        s = "Inline summary:\n"
        i = 0
        for info in self.inline_info:
            s += ("[" + str(i) + "]").ljust(7, " ") + indent(str(info), " " * 7)[7:] + "\n\n"
            i += 1
        return s[:-2]


    def add_function(self, binary_path, mangled_name, ranges, basic_blocks_count):
        self.inline_info.append(InlineInfo(binary_path, mangled_name, ranges, basic_blocks_count))


    def get_inline_info(self, binary_path=None, class_name=None, function_name=None, ordering=False):
        info_list = []
        for info in self.inline_info:
            if binary_path is not None and info.binary_path != binary_path:
                continue
            if class_name is not None and info.class_name != class_name:
                continue
            if function_name is not None and info.function_name != function_name:
                continue
            if not ordering: 
                yield info
            else:
                info_list.append([info.basic_blocks_count, info])
        if ordering:
            info_list.sort(key=lambda x:x[0], reverse=True)
            for info in info_list:
                yield info[1]


    def has_inlined_functions(self, binary_path):
        for info in self.inline_info:
            if info.binary_path == binary_path:
                return True
        return False