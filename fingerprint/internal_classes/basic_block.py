from fingerprint.internal_classes.capstone_instruction import CapstoneInstruction
from utils.name_mangling import demangle
from fingerprint.utils.constants import NO_RETURN_FUNCTIONS
from fingerprint.enums.colors import Colors
from fingerprint.enums.colors import InstructionClass as IC
from configurations.utils.helper import get_ignored_colors
from utils.helper import index_of, starts_with, ends_with
from copy import deepcopy

# TO BE REMOVED
from os.path import exists

class BasicBlock(object):

    # TODO: add attribute for indirect jumps and syscall
    # BEST is an enum for the type of the function call
    def __init__(self, angr_block, function_call_mangled_name="", library_call=None, function_call_address=0):
        # Saving address
        self.addr = angr_block.addr
        # Saving capstone
        self.capstone_insns = []
        for ins in angr_block.capstone.insns:
            address = ins.insn.address
            mnemonic = ins.insn.mnemonic
            op_str = ins.insn.op_str
            size = ins.insn.size
            c_instruction = CapstoneInstruction(address, mnemonic, op_str, size)
            self.capstone_insns.append(c_instruction)
        # Saving bytes
        self.bytes = angr_block.bytes
        # Saving function call info
        if (function_call_address != 0):
            self.is_plt = library_call
            self.has_function_call = True
        else:
            self.is_plt = None
            self.has_function_call = False
        self.function_call_address = function_call_address
        self.function_call_mangled_name = function_call_mangled_name
        self.function_call_path, self.function_call_name = demangle(self.function_call_mangled_name)
        # Coloring
        self._color()


    def __str__(self):
        s = "Block address: 0x%x\n" % self.addr
        if self.has_function_call:
            if self.function_call_address > 0:
                if self.function_call_path:
                    s += "Function call name: %s::%s\n" % (self.function_call_path, self.function_call_name)
                else:
                    s += "Function call name: %s\n" % self.function_call_name
                s += "Function call address: 0x%x\n" % self.function_call_address
            s += "Library call: %s\n" % str(self.is_plt)
        s += "Color: " + bin(self.color) + "\n"
        s += "Instructions:\n"
        for ins in self.capstone_insns:
            s += '%s\n' % str(ins)
        s = s[:-1]
        return s


    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


    #### PRIVATE METHODS ####


    def _color(self):
        # Loading configurations
        ignored_colors = get_ignored_colors()
        # Setting color
        self.color = int(IC.EMPTY)
        for ins in self.capstone_insns:
            color = Colors.get(ins.mnemonic, None)
            if color == None:
                if exists("../../missing_inst.txt"):
                    f = open("../../missing_inst.txt", "a")
                else:
                    f = open("../../missing_inst.txt", "w")
                f.write(ins.mnemonic + '\n')
                f.close()
                continue
            if color in ignored_colors:
                continue
                # raise Exception('Instruction "' + ins.mnemonic + '" not known.')
            self.color |= color


    def _remove_function_call(self):
        if self.has_function_call:
            self.is_plt = None
            self.has_function_call = False            
            self.function_call_address = ""
            self.function_call_mangled_name = ""
            self.function_call_path = ""
            self.function_call_name = ""


    #### PUBLIC METHODS ####


    def pp(self, spaces=2):
        spaces_str = " " * spaces
        s = spaces_str + "Block address: 0x%x\n" % self.addr
        if self.has_function_call:
            if self.function_call_address > 0:
                if self.function_call_path:
                    s += spaces_str + "Function call name: %s::%s\n" % (self.function_call_path, self.function_call_name)
                else:
                    s += spaces_str + "Function call name: %s\n" % self.function_call_name
                s += spaces_str + "Function call address: 0x%x\n" % self.function_call_address
            s += spaces_str + "Library call: %s\n" % str(self.is_plt)
        s += spaces_str + "Color: " + bin(self.color) + "\n"
        s += spaces_str + "Instructions:\n"
        for ins in self.capstone_insns:
            s += spaces_str + '%s\n' % str(ins)
        s = s[:-1]
        return s


    def has_no_return_call(self):
        if not self.has_function_call:
            return False
        if self.function_call_path == "":
            function_call_name = self.function_call_name
        else:
            function_call_name = self.function_call_path + "::" + self.function_call_name
        if function_call_name in NO_RETURN_FUNCTIONS:
            return True
        return False


    def contains(self, insns):
        if insns in self.bytes:
            return True
        return False


    def starts_with(self, insns):
        return starts_with(self.bytes, insns)


    def ends_with(self, insns):
        return ends_with(self.bytes, insns)


    def remove_instructions_before(self, insns):
        index = index_of(self.bytes, insns)
        if index < 0:
            raise Exception("Instructions are not present in the basic block!")
        self.bytes = self.bytes[index+len(insns):]
        if not self.bytes:
            raise Exception("No more instructions in the basic block!")
        bytes_length = len(self.bytes)
        tot_bytes = 0
        for index in range(len(self.capstone_insns))[::-1]:
            tot_bytes += self.capstone_insns[index].size
            if tot_bytes == bytes_length:
                break
            if tot_bytes > bytes_length:
                raise Exception("Error occured while removing delimiters instructions!")
        self.capstone_insns = self.capstone_insns[index:]
        self.addr = self.capstone_insns[0].address
        self._color()


    def remove_instructions_after(self, insns):
        index = index_of(self.bytes, insns)
        if index < 0:
            raise Exception("Instructions are not present in the basic block!")
        self.bytes = self.bytes[:index]
        if not self.bytes:
            raise Exception("No more instructions in the basic block!")
        bytes_length = len(self.bytes)
        tot_bytes = 0
        for index in range(len(self.capstone_insns)):
            tot_bytes += self.capstone_insns[index].size
            if tot_bytes == bytes_length:
                index += 1
                break
            if tot_bytes > bytes_length:
                raise Exception("Error occured while removing delimiters instructions!")
        self.capstone_insns = self.capstone_insns[:index]
        self._remove_function_call()
        self._color()


    def get_instructions_addresses(self):
        for ins in self.capstone_insns:
            yield ins.address

    def is_nop_block(self):
        if len(self.capstone_insns) == 1 and self.capstone_insns[0].mnemonic == "nop":
            return True
        return False