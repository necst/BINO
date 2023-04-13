from copy import deepcopy
from fingerprint.matching.match import Match
from fingerprint.enums.node_type import NodeType
from networkx.algorithms import isomorphism
from utils.helper import invert_dictionary, is_subset
from numpy import logical_and, logical_or
from fingerprint.utils.helper import plot_fingerprint


def _produce_matches(match, target_fp, query_dg, query_fp_detail, path_name, similarity):
    # Functions already returned
    matched_functions = []
    # New dictionary for the match, each entry must be {target_addres: Nodetype}
    new_match_dict = {}
    for t_bb_id, q_bb_id in match.items():
        t_insn_addr = list(target_fp.function_details.basic_blocks[t_bb_id].get_instructions_addresses())
        t_addr = target_fp.function_details.basic_blocks[t_bb_id].addr
        q_node_type = query_dg.nodes()[q_bb_id]
        new_match_dict[t_addr] = (t_insn_addr, q_node_type["type"])
    # Dictionary is ready, we have to return a different match for each function recognized
    for func_info in query_fp_detail.functions_info:
        if func_info.function_name not in matched_functions:
            matched_functions.append(func_info.function_name)
            yield Match(new_match_dict, path_name, func_info.function_name, similarity)


def _node_match(node_1, node_2):
    if (node_1["type"] == NodeType.NORETURN or
        node_2["type"] == NodeType.NORETURN):
        if (node_1["type"] != NodeType.NORETURN or
            node_2["type"] != NodeType.NORETURN):
            return False
    return True


def _get_color_vectors(target_color, query_color, intermediate=True):
    target_color_str = bin(target_color)[2:]
    query_color_str = bin(query_color)[2:]
    max_l = max(len(target_color_str), len(query_color_str))
    if not intermediate:
        bitmask_str = "0b" + ("1" * max_l)
        bitmask = int(bitmask_str, 2)
        not_query = bitmask ^ query_color
        not_interesting_colors = not_query & target_color
        query_color |= not_interesting_colors
        query_color_str = bin(query_color)[2:]
    target_color_str = target_color_str.rjust(max_l, "0")
    query_color_str = query_color_str.rjust(max_l, "0")
    target_color_v = map(int, target_color_str)
    query_color_v = map(int, query_color_str)
    return target_color_v, query_color_v


def _match_similarity(target_fp, query_fp_detail, query_dg, match):
    target_color = []
    query_color = []
    for bb_id_t, bb_id_q in match.items():
        query_node = query_dg.nodes()[bb_id_q]
        target_bb = target_fp.function_details.basic_blocks[bb_id_t]
        query_bb = query_fp_detail.basic_blocks[bb_id_q]
        if (query_node["type"] == NodeType.INITIAL or query_node["type"] == NodeType.FINAL):
            t_color_tmp, q_color_tmp = _get_color_vectors(target_bb.color, query_bb.color, False)
        else:
            t_color_tmp, q_color_tmp = _get_color_vectors(target_bb.color, query_bb.color, True)
        target_color += t_color_tmp
        query_color += q_color_tmp
    intersection = logical_and(target_color, query_color)
    union = logical_or(target_color, query_color)
    if union.sum() == 0:
        if intersection.sum() == 0:
            return 1.0
        else:
            return 0.0
    similarity = intersection.sum() / float(union.sum())
    return similarity


def _calls_blocks_equality(target_bb, query_bb, use_static_symbols):
    if (target_bb.has_function_call or query_bb.has_function_call):
        # Both must have a function call
        if (target_bb.has_function_call and query_bb.has_function_call):
            # plt check
            if (target_bb.is_plt or query_bb.is_plt):
                # Both must be from plt
                if (target_bb.is_plt and query_bb.is_plt):
                    # Name and path must be the same
                    if target_bb.function_call_path != query_bb.function_call_path:
                        return False
                    if target_bb.function_call_name != query_bb.function_call_name:
                        return False
                    return True
                else:
                    return False
            else:
                if use_static_symbols:
                    # Check if the name exists, then if the name and path are the same
                    if target_bb.function_call_name:
                        if target_bb.function_call_path != query_bb.function_call_path:
                            return False
                        if target_bb.function_call_name != query_bb.function_call_name:
                            return False
                        return True
                    else:
                        return True
                else:
                    return True
        else:
            return False
    return True


def _create_loop(query_dg):
    # Retrieving final and initial nodes
    initial_node = None
    final_nodes = []
    for node_id in query_dg.nodes():
        node = query_dg.nodes()[node_id]
        if node["type"] == NodeType.INITIAL:
            initial_node = node_id
        if node["type"] == NodeType.FINAL:
            final_nodes.append(node_id)
    # Adding edges from finals to initial
    for node_id in final_nodes:
        query_dg.add_edge(node_id, initial_node)


def _function_calls_equality(target_fp, query_fp_detail, query_fpcs, match, conf):
    for bb_id_t, bb_id_q in match.items():
        target_bb = target_fp.function_details.basic_blocks[bb_id_t]
        query_bb = query_fp_detail.basic_blocks[bb_id_q]
        query_node = query_fpcs.digraph.nodes[bb_id_q]
        if query_node["type"] != NodeType.FINAL and not _calls_blocks_equality(target_bb, query_bb, conf.use_static_symbols):
            return False
    return True


def _try_match(target_fp, query_fpcs, conf, normal=True):
    # Collectiong digraph
    target_dg = target_fp.digraph
    query_dg = query_fpcs.digraph.copy()
    # Precheck, listing plt calls
    if conf.function_call_checking:
        queries_plts = list(query_fpcs.get_plt_calls())
        target_plts = list(target_fp.get_plt_calls())
        found = False
        for query_plts in queries_plts:
            if is_subset(target_plts, query_plts):
                found = True
                break
        if not found:
            return
    if not normal:
        # Add loop edges
        _create_loop(query_dg)
    iso = isomorphism.DiGraphMatcher(target_dg, query_dg, _node_match)
    for match in iso.subgraph_isomorphisms_iter():
        # For each fingerprint detail, performs checks
        for query_fp_detail in query_fpcs.fingerprints_details:
            # First check: function calls equality
            if conf.function_call_checking:
                if not _function_calls_equality(target_fp, query_fp_detail, query_fpcs, match, conf):
                    continue
            # Second check: colors
            similarity = 1.0
            if conf.color_checking:
                similarity = _match_similarity(target_fp, query_fp_detail, query_dg, match)
                if similarity < conf.similarity_threshold:
                    continue
            # Match found
            for match_i in _produce_matches(match, target_fp, query_dg, query_fp_detail, query_fpcs.path_name, similarity):
                yield match_i


def try_match(target_fp, query_fpcs, conf):
    for match in _try_match(target_fp, query_fpcs, conf, True):
        yield match
    for match in _try_match(target_fp, query_fpcs, conf, False):
        yield match