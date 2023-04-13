import angr 
import logging
import json
from utils.angr_helper import get_function_by_name
from os.path import isdir, join, exists, dirname, abspath, split
from os import listdir, mkdir
from fingerprint.delimiters.helper import get_delimiters
from fingerprint.classes.fingerprint import Fingerprint, save_fingerprint
from shutil import rmtree
from multiprocessing import Process


# Global variables
delimiters = {}

PARALLEL_PROCESS = 8
FPS_PATH = "data/fingerprint"
PID = 0
I = 0

def _fingerprint_method_multiprocess(directory_src_path, directory_dst_path, method, fp_logger):
    method_src_path = join(directory_src_path, method)
    method_dst_path = join(directory_dst_path, method)
    mkdir(method_dst_path)
    i = 1
    for binary_src in listdir(method_src_path):
        # Not considering json and cpp
        if binary_src[-5:] == ".json" or binary_src[-4:] == ".cpp":
            continue
        # Creating angr project
        binary_src_path = join(method_src_path, binary_src)
        project = angr.Project(binary_src_path, load_options={'auto_load_libs': False})
        cfg = project.analyses.CFGFast(normalize=True)
        # Retrieving the initial and final delimiters
        initial_delimiters, final_delimiters = get_delimiters(project.arch.name)
        # Retrieving the wrapper function
        func_cfg = get_function_by_name(project, cfg, "wrapper")
        # Loading the json file
        json_path = join(method_src_path, binary_src + ".json")
        with open(json_path) as json_file:
            binary_dict = json.load(json_file)
        # Creating enriched blocks
        try:
            fp = Fingerprint(angr_function=func_cfg, angr_cfg=cfg, function_dict=binary_dict)
        except:
            fp_logger.error("Failed to fingerprint binary %s" % binary_src_path)
            continue
        # Reduction
        fp.reduce_between(initial_delimiters, final_delimiters)
        # Checking if it is empty
        if fp.is_empty():
            continue
        if fp.is_recursive():
            continue
        # Saving pickle
        fp_file_path = join(method_dst_path, binary_src + ".p")
        save_fingerprint(fp, fp_file_path)
        i += 1
        # Trying to save the optimized version
        optimized_fp = fp.get_optimized_fingerprint()
        if optimized_fp is not None:
            # Saving pickle
            fp_file_path = join(method_dst_path, binary_src + "_optimized.p")
            save_fingerprint(optimized_fp, fp_file_path)
            i += 1            
    if i == 1:
        fp_logger.warning("Path " + method_src_path + " not fingerprinted.")
        rmtree(method_dst_path)
    fp_logger.debug("Fingerprinted " + method + ".")

def _fingerprint_directory(src_path, dst_path, fp_logger, directory):
    directory_src_path = join(src_path, directory)
    directory_dst_path = join(dst_path, directory)
    if not exists(directory_src_path) or not isdir(directory_src_path):
        raise Exception("Path " + directory_src_path + " doesn't exists!")
    if exists(directory_dst_path) and isdir(directory_dst_path):
        rmtree(directory_dst_path)
    mkdir(directory_dst_path)
    dir_src_path_list = listdir(directory_src_path)
    for index in range(len(dir_src_path_list))[::PARALLEL_PROCESS]:
        start = index
        if index + PARALLEL_PROCESS > len(dir_src_path_list):
            end = len(dir_src_path_list)
        else:
            end = index + PARALLEL_PROCESS
        processes = []
        # Generating processes
        for i in range(start, end):
            p = Process(target=_fingerprint_method_multiprocess, 
                        args=(directory_src_path,
                                directory_dst_path,
                                dir_src_path_list[i],
                                fp_logger))
            processes.append(p)
        # Launching them
        for p in processes:
            p.start()
        # Waiting them
        for p in processes:
            p.join()


def fingerprinter(src_path, dst_path):
    """
    Public function. It is used to produce fingerprints of the methods of a class.

    Parameters:
    - binary_path: full path of a directory in which it is stored the
        binaries you want to fingerprint.
    - fingerprints_path: full path of a directory in which will be 
        stored another directory which will contain the fingerprints.
    """


    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Loggers
    fp_logger = logging.getLogger('fingerprinter')
    logging.getLogger('angr').setLevel('ERROR')
    logging.getLogger('cle').setLevel('ERROR')
    # Path checks
    if not isdir(src_path):
        raise Exception(src_path + " is not a file path")
    if not isdir(dst_path):
        raise Exception(dst_path + " is not a file path")
    # Fingerprinting section
    fp_logger.info("Joining " + src_path + " directory.")
    class_directory = split(src_path)[1]
    # Creating destination directory
    directory_dst_path = join(dst_path, class_directory)
    if exists(directory_dst_path) and isdir(directory_dst_path):
        rmtree(directory_dst_path)
        fp_logger.debug("Removed " + directory_dst_path + " directory.")
    mkdir(directory_dst_path)
    fp_logger.debug("Created " + directory_dst_path + " directory.")
    _fingerprint_directory(src_path, directory_dst_path, fp_logger, "public", )
