class BasicBlockSimple(object):

    def __init__(self, basic_block):
        self.color                      = basic_block.color
        self.is_plt                     = basic_block.is_plt
        self.has_function_call          = basic_block.has_function_call
        self.function_call_path         = basic_block.function_call_path
        self.function_call_name         = basic_block.function_call_name


    def __str__(self):
        return self.pp(spaces=0)


    def pp(self, spaces=2):
        spaces_chars = spaces * " "
        s = spaces_chars + "Color: " + bin(self.color) + "\n"
        if self.has_function_call:
            if self.function_call_path:
                s += spaces_chars + "Function call name: %s::%s\n" % (self.function_call_path, self.function_call_name)
            else:
                s += spaces_chars + "Function call name: %s\n" % self.function_call_name
            s += spaces_chars + "Library call: %s\n" % str(self.is_plt)
        return s[:-1]