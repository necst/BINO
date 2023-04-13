from fingerprint.enums.node_type import NodeType
from json import dumps
from copy import deepcopy


class Match(object):


    def __init__(self, match, path_name, function_name, similarity=1.0):
        self._build_match(match)
        self.path_name = path_name
        self.function_name = function_name
        self.similarity = similarity


    def __str__(self):
        return self.pp(spaces=0)


    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=2)


    def pp(self, spaces=2):
        white_spaces = " " * spaces
        if self.path_name:
            function_name_full = self.path_name + "::" + self.function_name
        else:
            function_name_full = self.function_name
        s = white_spaces + "Function recognized: %s\n" % function_name_full
        s += white_spaces + "Similarity: %f\n" % self.similarity
        s += white_spaces + "Blocks matched:\n"
        for block in self.blocks:
            s += white_spaces + " - 0x%x: %s\n" % (block["address"], block["type"])
        s = s[:-1]
        return s

    
    def _build_match(self, match):
        self.blocks = []
        for t_address, block_info in match.items():
            tmp_dict = {}
            tmp_dict["address"] = t_address - 0x400000
            tmp_dict["type"] = str(block_info[1])
            addresses = block_info[0]
            fixed_addresses = []
            for addr in addresses:
                fixed_addresses.append(addr - 0x400000)
            tmp_dict["instructions_addresses"] = fixed_addresses   
            self.blocks.append(tmp_dict)


    def same_function(self, other):
        if (self.path_name == other.path_name and
            self.function_name == other.function_name):
            return True
        else:
            return False


    def get_nodes_count(self):
        return len(self.blocks)


    def is_submatch(self, other):
        nodes_i = []
        nodes_j = []
        for block in self.blocks:
            nodes_i.append(block["address"])
        for block in other.blocks:
            nodes_j.append(block["address"])
        nodes_i = set(nodes_i)
        nodes_j = set(nodes_j)
        if nodes_i.issubset(nodes_j):
            return True
        else:
            return False


    def get_blocks_instructions_addresses(self, initial=True, finals=True):
        for block in self.blocks:
            if not initial and block["type"] == str(NodeType.INITIAL):
                continue
            if not finals and block["type"] == str(NodeType.FINAL):
                continue
            yield block["instructions_addresses"]