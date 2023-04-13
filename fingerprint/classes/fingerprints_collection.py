from fingerprint.internal_classes.fingerprint_details import FingerprintDetails
from networkx.algorithms.isomorphism import DiGraphMatcher
import pickle
from fingerprint.enums.merge_result import MergeResult
from fingerprint.matching.merging import node_match

class FingerprintsCollection(object):

    def __init__(self, fp):
        self.path_name = fp.path_name
        self.digraph = fp.digraph.copy()
        self.arch = fp.arch
        self.fingerprints_details = [FingerprintDetails(fp.function_details)]


    def __str__(self):
        s = "Collection for class: %s\n" % self.path_name
        s += "Arch: %s\n" % self.arch
        s += "Nodes count: %d\n" % len(self.digraph.nodes())
        s += "Nodes: %s\n" % str(self.digraph.nodes())
        s += "Edges count: %d\n" % len(self.digraph.edges())
        s += "Edges: %s\n" % str(self.digraph.edges())
        s += "Fingerprint details: \n"
        i = 0
        for fpd in self.fingerprints_details:
            s += "Details number: %d" % i
            s += fpd.pp(spaces=2)
            s += "\n\n\n\n"
        return s[:-4]


    def try_merge(self, fp):
        digm = DiGraphMatcher(self.digraph, fp.digraph, node_match=node_match)
        if digm.is_isomorphic():
            for match in digm.isomorphisms_iter():
                # If one match is 100% equal just append function info
                for fpd in self.fingerprints_details:
                    merge_result = fpd.try_merge(match, fp.function_details)
                    if merge_result == MergeResult.MERGED:
                        return MergeResult.MERGED
                    elif merge_result == MergeResult.ALREADY_MERGED:
                        return MergeResult.ALREADY_MERGED
            self.fingerprints_details.append(FingerprintDetails(fp.function_details, match))
            return MergeResult.MERGED
        return MergeResult.NOT_MERGED


    def get_basic_blocks_count(self):
        return len(self.digraph.nodes())


    def get_edges_count(self):
        return len(self.digraph.edges())


    def get_function_names(self):
        seen_function_names = []
        for fp_det in self.fingerprints_details:
            for function_name in fp_det.get_function_names():
                if function_name not in seen_function_names:
                    seen_function_names.append(function_name)
                    yield function_name


    def get_function_mangled_names(self):
        seen_function_mangled_names = []
        for fp_det in self.fingerprints_details:
            for function_mangled_name in fp_det.get_function_mangled_names():
                if function_mangled_name not in seen_function_mangled_names:
                    seen_function_mangled_names.append(function_mangled_name)
                    yield function_mangled_name


    def get_plt_calls(self):
        for fp_det in self.fingerprints_details:
            yield list(fp_det.get_plt_calls())


def save_fingerprints_collection(fingerprints_collection, path):
    with open(path, 'wb') as output:
        pickle.dump(fingerprints_collection, output)


def load_fingerprints_collection(path):
    with open(path, 'rb') as output:
        fingerprints_collection = pickle.load(output)
    return fingerprints_collection