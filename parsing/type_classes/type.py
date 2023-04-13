from clang.cindex import TypeKind

class Type(object):

    def __init__(self, ptype):
        self.ptype = ptype
        self.str_repr = Type.get_long_str_repr(ptype)

    def __str__(self):
        return self.str_repr

    @staticmethod
    def get_long_str_repr(ptype):
        n_temps = ptype.get_num_template_arguments()
        if (n_temps > 0 and ptype.kind != TypeKind.TYPEDEF and "typename " not in ptype.spelling):
            str_repr = ptype.spelling.split("<")[0] + "<"
            for i in range(n_temps):
                str_repr += Type.get_long_str_repr(ptype.get_template_argument_type(i)) + ", "
            str_repr = str_repr[:-2] + ">"
        else:
            str_repr = ptype.spelling
        return str_repr


    def is_const_qualified(self):
        return self.ptype.get_pointee().is_const_qualified()


    def is_reference(self):
        if TypeKind.LVALUEREFERENCE == self.ptype.kind:
            return True
        else:
            return False

    def is_rvalue(self):
        if TypeKind.RVALUEREFERENCE == self.ptype.kind:
            return True
        else:
            return False

    def is_const_reference(self):
        if self.is_const_qualified() and self.is_reference():
            return True
        return False