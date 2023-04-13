#!/usr/bin/python3.7

from os.path import isdir, isfile, join
from datetime import datetime
import logging
import angr
from utils.angr_helper import get_arch_name
from fingerprint.classes.fingerprints_manager import FingerprintsManager


def tester(fingerprints_directory, test_binary_path, conf):
    # Logger
    tester_logger = logging.getLogger('tester')
    logging.getLogger('angr').setLevel('ERROR')
    logging.getLogger('cle').setLevel('ERROR')
    # Path Checks
    if not isdir(fingerprints_directory):
        raise Exception(fingerprints_directory + " is not a directory path")
    if not isfile(test_binary_path):
        raise Exception(test_binary_path + " is not a file path")
    # Analyzing test binary with Angr
    tester_logger.info("Testing binary: " + test_binary_path)
    tester_logger.debug("Analyzing the binary with Angr...")
    start_t = datetime.now()
    project = angr.Project(test_binary_path, load_options={'auto_load_libs': False})
    cfg = project.analyses.CFGFast(normalize=True)
    end_t = datetime.now()
    angr_analysis_time = end_t - start_t
    tester_logger.debug("Binary Analyzed. Elapsed time: %s" % angr_analysis_time)
    arch = get_arch_name(project.arch.name)
    tester_logger.debug("Recognized architecture: %s" % arch)
    # Checking if a db exists for such an arch
    arch_path = join(fingerprints_directory, arch)
    if not isdir(fingerprints_directory):
        raise Exception("Couldn't find a fingerprints database for the architecture: %s." % arch)
    tester_logger.debug("Using fingerprints database: %s" % arch_path)
    # Creating fingerprint manager
    tester_logger.debug("Loading fingerprints database...")
    fp_manager = FingerprintsManager(arch_path, conf, tester_logger)
    tester_logger.debug("Fingerprints database loaded.")
    # Testing binary
    tester_logger.debug("Testing binary...")
    start_t = datetime.now()
    results_manager = fp_manager.test_binary(test_binary_path, cfg)
    end_t = datetime.now()
    test_time = end_t - start_t
    tester_logger.debug("Testing Done. Elapsed time: %s" % test_time)
    results_manager.angr_analysis_time = angr_analysis_time.seconds + angr_analysis_time.microseconds/1e6
    results_manager.bino_analysis_time = test_time.seconds + test_time.microseconds/1e6
    if conf.output_file is None:
        for line in str(results_manager).split("\n"):
            tester_logger.info(line)
    else:
        f = open(conf.output_file, "w")
        f.write(results_manager.toJSON())
        f.close()
    return results_manager
