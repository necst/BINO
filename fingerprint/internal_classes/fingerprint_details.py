from fingerprint.internal_classes.function_info import FunctionInfo
from fingerprint.internal_classes.basic_block_simple import BasicBlockSimple
from fingerprint.matching.merging import blocks_equality
from fingerprint.enums.merge_result import MergeResult
from copy import deepcopy
from utils.helper import invert_dictionary

class FingerprintDetails(object):

    def __init__(self, function_details, match=None):
        if match is None:
            # Standard init
            self._standard_init(function_details)
        else:
            # Need to adjust id values if needed
            equals_ids = True
            for key, value in match.items():
                if key != value:
                    equals_ids = False
                    break
            if not equals_ids:
                # Match init
                self._match_init(function_details, match)
            else:
                # Standard init
                self._standard_init(function_details)
        # Many functions can have the same features, so we save information about those function too
        self.functions_info = [FunctionInfo(function_details)]


    def __str__(self):
        return self.pp(spaces=0)


    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


    def _match_init(self, function_details, match):
        # First fixing basic blocks
        tmp_blocks_dict = {}
        for bb_id_1, bb_id_2 in match.items():
            tmp_blocks_dict[bb_id_1] =  BasicBlockSimple(function_details.basic_blocks[bb_id_2])
        self.basic_blocks = tmp_blocks_dict
        # Then edges
        # Need to invert match dictionary for a faster execution
        inv_match = invert_dictionary(match)
        # Fixing edges
        self.edges = []
        for edge in function_details.edges:
            new_s_id = inv_match[edge[0]]
            new_e_id = inv_match[edge[1]]
            self.edges.append((new_s_id, new_e_id))


    def _standard_init(self, function_details):
        # Edges can be just copied
        self.edges = function_details.edges.copy()
        # Basic blocks must be simplified
        self.basic_blocks = {}
        for bb_id in function_details.basic_blocks.keys():
            self.basic_blocks[bb_id] = BasicBlockSimple(function_details.basic_blocks[bb_id])

    
    def pp(self, spaces=2):
        spaces_chars = spaces * " "
        s = ""
        s += spaces_chars + "Edges: %s\n" % str(self.edges)
        s += spaces_chars + "Basic blocks:\n"
        for block_id in self.basic_blocks.keys():
            s += (spaces+2) * " " + "Basic block id: %d\n" % block_id
            s += self.basic_blocks[block_id].pp(spaces=spaces+2)
            s += "\n\n"
        return s[:-2]


    def try_merge(self, match, candidate_fp):
        # self.blocks.keys() and match.keys() share the same ids
        # candidate_fp.blocks.keys() and match.items() share the same ids
        # First check if blocks are equal
        for b1_id, b2_id in match.items():
            b1 = self.basic_blocks[b1_id]
            b2 = candidate_fp.basic_blocks[b2_id]
            if not blocks_equality(b1, b2):
                return MergeResult.NOT_MERGED
        # Fingerprints are equal, now we try to add the function info to the list
        for func_info in self.functions_info:
            if func_info.is_info_equal(candidate_fp):
                return MergeResult.ALREADY_MERGED
        # If we reach this point, it means that we have not found similar function info. Hence, we add these info
        self.functions_info.append(FunctionInfo(candidate_fp))
        return MergeResult.MERGED


    def get_function_names(self):
        seen_function_names = []
        for func_info in self.functions_info:
            if func_info.function_name not in seen_function_names:
                seen_function_names.append(func_info.function_name)
                yield func_info.function_name


    def get_function_mangled_names(self):
        seen_function_mangled_names = []
        for func_info in self.functions_info:
            if func_info.mangled_name not in seen_function_mangled_names:
                seen_function_mangled_names.append(func_info.mangled_name)
                yield func_info.mangled_name


    def get_plt_calls(self):
        for bb in self.basic_blocks.values():
            if bb.has_function_call and bb.is_plt:
                if bb.function_call_path:
                    yield bb.function_call_path + "::" + bb.function_call_name
                else:
                    yield bb.function_call_name