from fingerprint.internal_classes.basic_block import BasicBlock
from utils.angr_helper import get_jumps_addresses, get_block_function_call_offset, get_angr_offset_name
from utils.name_mangling import remove_optimization_from_mangled
from utils.name_mangling import demangle
from copy import deepcopy

class FunctionDetails(object):


    def __init__(self, angr_function, angr_cfg, function_name="", function_dict=None):
        self.addr = angr_function.addr
        if function_dict is not None:
            self.mangled_name = function_dict["mangled_name"]           
            self.optimization_level = function_dict["optimization"]
            self.function_name = function_dict["function_name"]
            self.types = function_dict["types"]
            self.compiler_version = function_dict["compiler_version"]
            self.cpp_version = function_dict["cpp_version"]
        else:
            self.mangled_name = function_name
            self.optimization_level = None
            _, self.function_name = demangle(function_name)
            self.types = {}
            self.compiler_version = None
            self.cpp_version = None
        # Recreating graph
        self._add_basic_blocks(angr_function, angr_cfg)
        self._add_jump_types(angr_function)


    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


    def _add_basic_blocks(self, angr_function, angr_cfg):
        self.basic_blocks = {}
        block_id = 1
        for block in angr_function.blocks:
            has_function_call, offset = get_block_function_call_offset(angr_function, block)
            if has_function_call:
                if offset in angr_cfg.kb.functions:
                    function_cfg = angr_cfg.kb.functions[offset]
                    fc_angr_name = function_cfg.name
                    fc_offset_name = get_angr_offset_name(offset)
                    if fc_angr_name == fc_offset_name:
                        function_called_name = ""
                    else:
                        function_called_name = function_cfg.name
                        function_call_mangled_name = remove_optimization_from_mangled(function_called_name)
                    self.basic_blocks[block_id] = BasicBlock(block, function_call_mangled_name, function_cfg.is_plt, offset)
                else:
                    self.basic_blocks[block_id] = BasicBlock(block, "", False, -1) # Register CALL/JUMP
            else:
                self.basic_blocks[block_id] = BasicBlock(block)
            block_id += 1


    def _add_jump_types(self, angr_function):
        self.edges = []
        for basic_block in angr_function.blocks:
            starting_id = self.get_id_from_addr(basic_block.addr)
            basic_block_j = self.basic_blocks[starting_id]
            if basic_block_j.has_no_return_call():
                continue
            for addr in get_jumps_addresses(basic_block):
                if self.block_address_exists(addr):
                    landing_id = self.get_id_from_addr(addr)
                    self.edges.append((starting_id, landing_id))


    def get_id_from_addr(self, addr):
        for basic_block_id, basic_block in self.basic_blocks.items():
            if basic_block.addr == addr:
                return basic_block_id
        raise Exception("Basic block at address 0x%x not found in the dictionary!" % addr)


    def get_addr_from_id(self, bb_id):
        return self.basic_blocks[bb_id].addr


    def remove_basic_block_by_id(self, bb_id):
        for basic_block_id in self.basic_blocks.keys():
            if basic_block_id == bb_id:
                del self.basic_blocks[basic_block_id]
                break
        tmp_edges = self.edges.copy()
        for edge in tmp_edges:
            if bb_id in edge:
                self.edges.remove(edge)


    def block_address_exists(self, addr):
        for basic_block in self.basic_blocks.values():
            if basic_block.addr == addr:
                return True
        return False


    def block_id_exists(self, bb_id):
        for basic_block_id, in self.basic_blocks.keys():
            if basic_block_id == bb_id:
                return True
        return False


    def remove_edge(self, edge):
        for edge_i in self.edges:
            if edge_i == edge:
                self.edges.remove(edge_i)
                break


    def clear(self):
        self.edges = []
        self.basic_blocks = {}


    def get_constant_function_calls_info(self):
        for bb in self.basic_blocks.values():
            if (bb.has_function_call and bb.function_call_name):
                yield bb.function_call_mangled_name, bb.function_call_path, bb.function_call_name, bb.is_plt


    def get_non_return_block_ids(self):
        for bb_id, bb in self.basic_blocks.items():
            if bb.has_no_return_call():
                yield bb_id


    def get_plt_calls(self):
        for bb in self.basic_blocks.values():
            if bb.has_function_call and bb.is_plt:
                if bb.function_call_path:
                    yield bb.function_call_path + "::" + bb.function_call_name
                else:
                    yield bb.function_call_name