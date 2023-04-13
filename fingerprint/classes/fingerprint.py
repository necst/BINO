import pickle
from fingerprint.internal_classes.function_details import FunctionDetails
from networkx import DiGraph, set_node_attributes
from networkx.algorithms import is_connected, connected_components
from utils.name_mangling import demangle
from utils.angr_helper import get_arch_name
from fingerprint.enums.node_type import NodeType
from copy import deepcopy
from fingerprint.utils.helper import plot_fingerprint 

class Fingerprint(object):


    def __init__(self, angr_function, angr_cfg, function_name="", function_dict=None, strict=True):
        if function_dict is None:
            self.path_name, _ = demangle(function_name)
        else:
            self.path_name = function_dict["path_name"]
        self.strict = strict
        self.arch = get_arch_name(angr_cfg.project.arch.name)
        self.function_details = FunctionDetails(angr_function, angr_cfg, function_name, function_dict)
        # Creating a DiGraph with basic blocks IDs
        self.digraph = DiGraph()
        self._add_nodes()
        self._add_edges()
        # Check for connected components
        self._reduce()
        if self.strict:
            self._reduce_initials()
        # Setting nodes attributes
        self._set_nodes_attributes()
        # Consistency check
        self._consistency_checks()
        

    def __str__(self):
        s = "Function path: %s\n" % self.path_name
        s += "Function name: %s\n" % self.function_details.function_name
        s += "Architecture: %s\n" % self.arch
        s += "Parameters types: %s\n" % self.function_details.types
        s += "Optimization level: %s\n" % self.function_details.optimization_level
        s += "Compiler version: %s\n" % self.function_details.compiler_version
        s += "C++ version: %s\n" % self.function_details.cpp_version
        s += "Edges: %s\n" % self.digraph.edges()
        s += "Basic blocks:\n"
        for bb_id, basic_block in self.function_details.basic_blocks.items():
            s += "  Basic block id: %d\n" % bb_id
            s += basic_block.pp() + "\n\n"
        s = s[:-2]
        return s


    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


    #### PRIVATE METHODS ####


    def _set_nodes_attributes(self):
        attr = {}
        if self.get_basic_blocks_count() == 1:
            node_id = list(self.digraph.nodes())[0]
            attr[node_id] = {"type": NodeType.SINGULAR}
        else:
            for node_id in self.digraph.nodes():
                intermediate = True
                if self.digraph.in_degree(node_id) == 0:
                    # Is an initial node
                    attr[node_id] = {"type": NodeType.INITIAL}
                    intermediate = False
                if self.digraph.out_degree(node_id) == 0:
                    # Can be Final or non return
                    bb = self.function_details.basic_blocks[node_id]
                    intermediate = False
                    if bb.has_no_return_call():
                        attr[node_id] = {"type": NodeType.NORETURN}
                    else:
                        attr[node_id] = {"type": NodeType.FINAL}
                if intermediate:
                    attr[node_id] = {"type": NodeType.INTERMEDIATE}
        set_node_attributes(self.digraph, attr)


    def _consistency_checks(self):
        assert set(self.function_details.basic_blocks.keys()) == set(self.digraph.nodes)
        assert set(self.function_details.edges) == set(self.digraph.edges)
        # Now there should be only one initial block
        if self.strict:
            count_in = 0
            for node_id in self.digraph.nodes():
                if not self.digraph.in_edges(node_id):
                    count_in += 1
            if count_in != 1:
                raise Exception("Not singular initial block!")
     

    def _reduce_initials(self):
        initial_nodes_addrs = []
        for node in self.digraph.nodes():
            if self.digraph.in_degree(node) == 0:
                initial_nodes_addrs.append(self.function_details.get_addr_from_id(node))
        if len(initial_nodes_addrs) != 1:
            # Understanding which one is the real initial node, e.g., the one with the lowest address
            min_addr = min(initial_nodes_addrs)
            # Getting its ID
            start_block_id = self.function_details.get_id_from_addr(min_addr)
            self._cut_dead_starts(start_block_id)


    def _add_nodes(self):
        for basic_block_id in self.function_details.basic_blocks.keys():
            self.digraph.add_node(basic_block_id)


    def _add_edges(self):
        for edge in self.function_details.edges:
            self.digraph.add_edge(edge[0], edge[1])


    def _reduce(self):
        # Ideally, one function's CFG has only 1 connected component and we may have split it with no_return functions
        undirected = self.digraph.to_undirected()
        if not is_connected(undirected):
            # Need to remove some nodes
            # Finding initial nodes addresses
            initial_nodes_addrs = []
            for node in self.digraph.nodes():
                if self.digraph.in_degree(node) == 0:
                    initial_nodes_addrs.append(self.function_details.get_addr_from_id(node))
            # Understanding which one is the real initial node, e.g., the one with the lowest address
            min_addr = min(initial_nodes_addrs)
            # Getting its ID
            start_block_id = self.function_details.get_id_from_addr(min_addr)
            # Looking for its not connected component
            self._remove_connected_components_without(start_block_id)


    def _remove_inner_edges(self, bb_id):
        in_edges = list(self.digraph.in_edges(bb_id))
        for edge in in_edges:
            # From DiGraph
            self.digraph.remove_edge(edge[0], edge[1])
            # From function details
            self.function_details.remove_edge(edge)


    def _remove_outer_edges(self, bb_id):
        outer_edges = list(self.digraph.out_edges(bb_id))
        for edge in outer_edges:
            # From DiGraph
            self.digraph.remove_edge(edge[0], edge[1])
            # From function details
            self.function_details.remove_edge(edge)


    def _remove_connected_components_without(self, basic_block_id):
        undirected = self.digraph.to_undirected()
        while not is_connected(undirected):
            for cc in connected_components(undirected):
                if basic_block_id not in cc:
                    # Removing the entire components
                    to_be_removed = list(cc)
                    for bb_id in to_be_removed:
                        # From DiGraph
                        self.digraph.remove_node(bb_id)
                        # From function details
                        self.function_details.remove_basic_block_by_id(bb_id)
                    # New undirected graph
                    undirected = self.digraph.to_undirected()
                    break


    def _cut_dead_starts(self, real_start):
        new_nodes = [real_start]
        active_nodes = set()
        while new_nodes:
            current_node = new_nodes.pop(0)
            # Already saw -> continue
            if current_node in active_nodes:
                continue
            # Active node
            active_nodes = active_nodes.union([current_node])
            # Never saw -> get outer edge
            for edge in self.digraph.out_edges(current_node):
                new_nodes.append(edge[1])
        # Once active nodes are found
        while active_nodes != set(self.digraph.nodes()):
            for node_id in self.digraph.nodes():
                if node_id not in active_nodes:
                    # From DiGraph
                    self.digraph.remove_node(node_id)
                    # From function details
                    self.function_details.remove_basic_block_by_id(node_id)
                    break                 


    def _clear_graph(self):
        # Digraph
        self.digraph.clear()
        # Function details
        self.function_details.clear()


    def _make_node_initial(self, node_id):
        node = self.digraph.nodes()[node_id]
        if self.get_basic_blocks_count() == 1:
            node["type"] = NodeType.SINGULAR
        else:
            node["type"] = NodeType.INITIAL


    def _make_node_final(self, node_id):
        node = self.digraph.nodes()[node_id]
        if self.get_basic_blocks_count() == 1:
            node["type"] = NodeType.SINGULAR
        else:
            node["type"] = NodeType.FINAL


    def _make_previous_nodes_final(self, node_id):
        for edge in self.digraph.in_edges(node_id):
            self._make_node_final(edge[0])


    def _reduce_starting_from(self, insns):
        # Precheck: instructions must occours only once
        basic_block = []
        for block in self.function_details.basic_blocks.values():
            if block.contains(insns):
                basic_block.append(block)
        if len(basic_block) != 1:
            raise Exception("Non singular initial instructions!")
        # Processing block
        basic_block = basic_block[0]
        # Case #1: block ends with the instructions -> it shouldn't be possible since the delimiters shouldn't be jumps/calls
        # Case #2: block doesn't end with the instructions -> previous edges must be cut
        # In any case, we need to remove previous edge
        bb_id = self.function_details.get_id_from_addr(basic_block.addr)
        if basic_block.ends_with(insns):
            if bb_id in self.get_final_nodes_ids(False):
                self._clear_graph()
                return
            else:
                raise Exception("Basic block ends with initial delimiters!")
        self._remove_inner_edges(bb_id)
        # If the removal generates two or more connected components, we remove the ones without the current block
        self._remove_connected_components_without(bb_id)
        # Now we need only to remove the delimiters and color again :)
        basic_block.remove_instructions_before(insns)
        # Node becomes initial
        self._make_node_initial(bb_id)
        # Removing fake starts
        self._cut_dead_starts(bb_id)
        # Consistency checks
        self._consistency_checks()


    def _reduce_finishing_with(self, insns):
        # Precheck: instructions must occours only once
        basic_block = []
        for block in self.function_details.basic_blocks.values():
            if block.contains(insns):
                basic_block.append(block)
        if len(basic_block) != 1:
            raise Exception("Non singular final instructions!")
        # Processing block
        basic_block = basic_block[0]
        # Case #1: block starts with the instructions -> previous edges must be cut
        # Case #2: block doesn't start with the instructions -> next edges must be cut
        bb_id = self.function_details.get_id_from_addr(basic_block.addr)
        initial_id = self.get_initial_node_id()
        if basic_block.starts_with(insns):
            if bb_id == initial_id:
                # No instructions to be fingerprinted
                self._clear_graph()
                return
        # We want only one final block
        self._remove_outer_edges(bb_id)
        # Removing instructions
        basic_block.remove_instructions_after(insns)
        # If the removal generates two or more connected components, we remove the ones without the initial block
        self._cut_dead_starts(initial_id)
        # Make the node final
        self._make_node_final(bb_id)
        # Consistency checks
        self._consistency_checks()
        # We still want one final node
        if len(list(self.get_final_nodes_ids())) > 1:
            raise Exception("More than one final node after reduction!")
        

    #### PUBLIC METHODS ####


    def get_initial_node_id(self):
        initial_nodes = []
        for node_id in self.digraph.nodes():
            node = self.digraph.nodes()[node_id]
            if node["type"] == NodeType.INITIAL:
                initial_nodes.append(node_id)
        if len(initial_nodes) != 1:
            raise Exception("More than one initial block!")
        return initial_nodes[0]


    def get_final_nodes_ids(self, include_no_return_call=True):
        for node_id in self.digraph.nodes():
            node = self.digraph.nodes()[node_id]
            if node["type"] == NodeType.FINAL:
                if node["type"] == NodeType.NORETURN:
                    if include_no_return_call:
                        yield node_id
                else:
                    yield node_id


    def reduce_between(self, initial_instructions, final_instructions):
        self._reduce_starting_from(initial_instructions)
        self._reduce_finishing_with(final_instructions)


    def is_empty(self):
        if self.get_basic_blocks_count() == 0:
            return True
        return False


    def is_recursive(self):
        mangled_name = self.function_details.mangled_name
        for function_call_mang_name, _, _, is_plt in self.function_details.get_constant_function_calls_info():
            if function_call_mang_name == mangled_name and not is_plt:
                return True
        return False


    def get_basic_blocks_count(self):
        return len(self.digraph.nodes())


    def get_edges_count(self):
        return len(self.digraph.edges())


    def get_optimized_fingerprint(self):
        # First, we need at least two nodes
        if self.get_basic_blocks_count() <= 1:
            return None
        # Then we create a copy
        new_fp = deepcopy(self)
        # From the last node, we get all of the last but one nodes
        last_node_id = list(new_fp.get_final_nodes_ids(False))
        if len(last_node_id) > 1:
            raise Exception("More than one final node after reduction!")
        last_node_id = last_node_id[0]
        last_but_one_edges = list(new_fp.digraph.in_edges(last_node_id))
        last_but_one_node_ids = []
        for edge in last_but_one_edges:
            last_but_one_node_ids.append(edge[0])
        # Trying to remove all edges
        # If one last but one is initial, the fingerprint is not optimizable
        # If one last but one has another edge, the fingerprint is not optimizable
        # If only one last but one, the fingerprint is not optimizable
        if len(last_but_one_node_ids) == 1:
            return None
        for node_id in last_but_one_node_ids:
            node = new_fp.digraph.nodes()[node_id]
            # Initial case
            if node["type"] == NodeType.INITIAL:
                return None
        # Fingerprint is optimizable
        # Collection the color of the last basic block
        bb = new_fp.function_details.basic_blocks[last_node_id]
        bb_color = bb.color
        # Make last but one nodes final
        new_fp._make_previous_nodes_final(last_node_id)
        # Merge colors
        for node_id in last_but_one_node_ids:
            bb_i = new_fp.function_details.basic_blocks[node_id]
            bb_i.color |= bb_color
        # Remove last node
        new_fp._remove_inner_edges(last_node_id)
        # If the removal generates two or more connected components, we remove the ones without the current block
        new_fp._remove_connected_components_without(new_fp.get_initial_node_id())
        return new_fp


    def get_plt_calls(self):
        for plt_call in self.function_details.get_plt_calls():
            yield plt_call


def save_fingerprint(fingerprint, path):
    with open(path, 'wb') as output:
        pickle.dump(fingerprint, output)


def load_fingerprint(path):
    with open(path, 'rb') as output:
        fingerprint = pickle.load(output)
    return fingerprint