from copy import deepcopy

class CapstoneInstruction(object):


    def __init__(self, address, mnemonic, op_str, size):
        self.address = address
        self.mnemonic = mnemonic
        self.op_str = op_str
        self.size = size


    def __eq__(self, other):
        if (self.mnemonic == other.mnemonic and
            self.op_str == other.op_str):
            return True
        return False


    def __copy__(self):
        raise Exception("Shallow copy is not allowed for class: CapstoneInstruction.")


    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


    def __str__(self):
        s = hex(self.address)
        s += ":\t" + self.mnemonic
        s += "\t" + self.op_str
        return s