from fingerprint.internal_classes.fingerprints_collections import FingerprintsCollections
from fingerprint.classes.fingerprint import Fingerprint
from os import listdir
from os.path import join, isdir
from fingerprint.results.results_manager import ResultsManager
from fingerprint.matching.matching import try_match
from utils.name_mangling import demangle
from multiprocessing import Pool
from datetime import datetime


class FingerprintsManager(object):

    def __init__(self, fingerprints_db_path, conf, logger):
        self.fingerprint_db_path = fingerprints_db_path
        self.conf = conf
        self.classes = []
        self._load_fingerprints()
        self.logger = logger


    def _load_fingerprints(self):
        # Loading all the fingerprints classes defined in the configuration
        if self.conf.classes is None:
            classes = listdir(self.fingerprint_db_path)
        else:
            classes = self.conf.classes
        for class_i in classes:
            class_i_path = join(self.fingerprint_db_path, class_i)
            if not isdir(class_i_path):
                raise Exception("Fingerprints for class '%s' don't exist!" % class_i)
            self.classes.append(FingerprintsCollections(class_i_path))


    def _get_fingerprints_collection(self):
        for class_fpcs in self.classes:
            for fpcs in class_fpcs.get_fingerprints_collections():
                yield fpcs


    def _test_target_fingerprints(self, target_fp):
        function_matches = []
        n_basic_blocks = target_fp.get_basic_blocks_count()
        # At least two basic blocks
        if n_basic_blocks <= 1:
            return [False, function_matches, "", 0, 0]
        # Target fp must have minimum  min_basic_block
        if n_basic_blocks < self.conf.minimum_basic_blocks:
            return [False, function_matches, "", 0, 0]
        f_addr = target_fp.function_details.addr
        f_name = target_fp.function_details.function_name
        self.logger.debug("Analyzing function at address 0x%x with basic block count %d and name: '%s'" %(f_addr, n_basic_blocks, f_name))
        start_t = datetime.now()
        # Retrieving all the query fingeprints collections
        for query_fpsc in self._get_fingerprints_collection():
            # Query fp must have minimum min_basic_blocks
            if query_fpsc.get_basic_blocks_count() < self.conf.minimum_basic_blocks:
                continue
            matches_i = list(try_match(target_fp, query_fpsc, self.conf))
            for match_i in matches_i:
                function_matches.append(match_i)
        end_t = datetime.now()
        test_time = end_t - start_t
        return [True, function_matches, "Function sub_%x" % (f_addr - 0x400000), test_time.total_seconds(), n_basic_blocks]


    def test_binary(self, test_binary_path, cfg):
        # Creating target fingerprints
        arguments = []
        for angr_function in cfg.kb.functions.values():
            # If the function is a plt function we don't care
            if angr_function.is_plt:
                continue
            # No blocks? Don't care  
            if angr_function.size == 0:
                continue
            arguments.append([angr_function, cfg, angr_function.name, None, False])
        with Pool(self.conf.processes) as pool:
            target_fps = pool.starmap(Fingerprint, arguments)
        two_d_target_fps = []
        for target_fp in target_fps:
            two_d_target_fps.append([target_fp])
        # Testing target fingerprints one by one
        results_manager = ResultsManager(test_binary_path)
        with Pool(self.conf.processes) as pool:
            two_d_matches = pool.starmap(self._test_target_fingerprints, two_d_target_fps)
        matches = []
        functions_stats = []
        for matches_i in two_d_matches:
            if matches_i[0]:
                matches += matches_i[1]
                functions_stats += [matches_i[2:]]
        for match in matches:
            # Add to matches
            results_manager.add_match(match)
            results_manager.add_statistics(functions_stats)
        return results_manager


    def has_function(self, class_name, function_name):
        for query_fpsc in self._get_fingerprints_collection():
            if query_fpsc.path_name != class_name:
                continue
            function_names = list(query_fpsc.get_function_names())
            if function_name in function_names:
                return True
        return False


    def has_exact_function(self, mangled_name):
        class_name, _ = demangle(mangled_name)
        for query_fpsc in self._get_fingerprints_collection():
            if query_fpsc.path_name != class_name:
                continue
            function_mangled_names = list(query_fpsc.get_function_mangled_names())
            if mangled_name in function_mangled_names:
                return True
        return False