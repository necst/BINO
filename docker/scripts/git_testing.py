#!/usr/bin/python3

import argparse
from pickle import TRUE
import subprocess
from os.path import isfile, exists, join, isdir, dirname, abspath, islink
from os import getcwd, chdir, mkdir, listdir, stat, remove, rename
from fingerprint.classes.fingerprints_manager import FingerprintsManager
from fingerprint.matching.matching_configurations import MatchingConfigs
from stages.tester import tester
from shutil import rmtree, copytree
from stages.tester import tester
import logging
from utils.file_info import file_info
from testing.output_manager import OutputManager
from testing.statistics import Statistics
from testing.dwarf import Dwarf
from testing.inline_summary import InlineSummary
from utils.name_mangling import demangle
from subprocess import TimeoutExpired
import sys
import time
import angr
"""
This file is used only for testing, and so all the Classes and function
it uses alone are all this file.
"""

# Parameters
PROCESSES = 4
COLOR_CHECKING = True
FUNCTION_CALL_CHECKING = True
SIMILARITY_THRESHOLD = 0.75
MIN_BB = 5
# Files
CANDIDATES = "data/github_projects/candidates.csv"
FILE_VALID_REPO = "data/github_projects/valid_projects.csv"
FILE_INVALID_REPO = "data/github_projects/invalid_projects.csv"
OUTPUT = "data/github_projects/git_testing_output"
# Directories
PROJECTS_DIR = "data/github_projects/projects"
CACHE_DIR = "data/github_projects/global_cache"
WORKING_DIR = "data/github_projects/working_dir"
FINGERPRINT_DB_PATH_ARCH = "data/fingerprints_db/amd64"
FINGERPRINT_DB_PATH = "data/fingerprints_db"

OPT_LEVEL = ["-O2", "-O3", "-Os", "-Ofast"]


def is_binary(path):
    if path[-2:] == ".o":
        return False
    f = open(path, "rb")
    content = f.read()
    f.close()
    if b'\x7f\x45\x4c\x46' == content[0:4]:
        return True
    return False


def is_library(path):
    if path[-2:] == ".a":
        return True
    if path[-3:] == ".so":
        return True
    return False


def is_stripped(file_path):
    info = file_info(file_path)
    if "not stripped" in info:
        return False
    else:
        return True


def get_binary(path):
    ret_binaries = []
    for file in listdir(path):
        file_path = join(path, file)
        if islink(file_path):
            continue
        if isfile(file_path):
            if is_binary(file_path):
                ret_binaries.append(file_path)
        elif isdir(file_path):
            ret_binaries += get_binary(file_path)
    return ret_binaries


def has_libraries(path):
    for file in listdir(path):
        file_path = join(path, file)
        if islink(file_path):
            continue
        if isfile(file_path):
            if is_library(file_path):
                return True
        else:
            if has_libraries(file_path):
                return True
    return False    


def get_github_url(api_path):
    splitted_b = api_path.split("/")
    git_url = "https://github.com/" + splitted_b[-2] + "/" + splitted_b[-1] 
    return git_url


def initialize_file(path):
    if not isfile(path):
        f = open(path, "w")
        f.close()


def in_file(file_path, api_path):
    f = open(file_path)
    content = f.read()
    f.close()
    if api_path in content:
        return True
    return False


def clear_directory(path):
    for file in listdir(path):
        if isfile(join(path,file)):
            remove(join(path,file))
        else:
            rmtree(join(path,file))


def check_includes(classes):
    for class_name in classes:
        class_name = class_name.replace("std::", "")
        cmd = ["grep", "-r", "<" + class_name + ">", "."]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, _ = process.communicate()
        if stdout:
            return True
    return False


def check_makefile():
    for file in listdir("."):
        if isfile(file):
            if file == "Makefile":
                return True
    return False


def basic_block_count(basic_blocks, ranges):
    basic_blocks_ranges = []
    # Retriving all of the blocks of the inline function
    for range_i in ranges:
        for addr in range(range_i[0], range_i[1]):
            for bb in basic_blocks:
                low_addr = bb.addr
                high_addr = bb.addr + bb.size
                if low_addr <= addr + 0x400000 < high_addr:
                    if bb not in basic_blocks_ranges:
                        basic_blocks_ranges.append(bb)
    return len(basic_blocks_ranges)


def clone_repo(repo_url):
    cmd = ["wget", repo_url]
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return_code = out.wait()
    if return_code != 0:
        content = "\n".join(out.stderr.readlines())
        if "404 Not Found" in content:
            return 404
        elif "429 too many requests" in content:
            return 429
        else:
            print(content)
            return -1
    clear_directory(".")
    cmd = ["git", "clone", repo_url]
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return_code = out.wait()    
    return return_code


def test_repository(repo_url, out_manager, query_db, classes, tester_logger, enable_cache):
    # Preparing environment
    old_path = getcwd()
    prj_name = repo_url.split("https://github.com/")[1].replace("/", "___")
    # Cheking if cached
    cached = False
    for file in listdir(CACHE_DIR):
        file_path = join(CACHE_DIR, file)
        if file == prj_name and isdir(file_path):
            cached = True
    chdir(WORKING_DIR)
    clear_directory(".")
    mkdir("cache")
    mkdir("prj_dir")
    chdir("cache")
    clear_directory(".")
    if not cached:
        # Cloning directory
        return_code = clone_repo(repo_url)
        if return_code == 429:
            raise Exception("Clone limited!")
        elif return_code == 404:
            print("Project not found!")
            chdir(old_path)
            return -1
        elif return_code != 0: 
            raise Exception("Unknown return code!")
        # Creating copy in 'prj_dir'
        cur_prj_name = listdir(".")[0]
        rename(cur_prj_name, prj_name)
        copy_path = join("..", "cache", prj_name)
        chdir("../prj_dir")
        copytree(copy_path, prj_name, symlinks=True)
        chdir(prj_name)
        if not check_includes(classes):
            print("No includes!")
            chdir(old_path)
            return -1
        if not check_makefile():
            print("No makefile!")
            chdir(old_path)
            return -1
        # Compile
        cmd = ['make', 'CXXFLAGS=-std=c++14 -s -lm -lpthread']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            _, stderr = process.communicate(timeout=60)
        except TimeoutExpired as E:
            print("Compilation timeouted")
            process.kill()
            chdir(old_path)
            return -1
        if stderr:
            print("Compilation error: ")
            try:
                f = open("../../../compilation_errors.txt", "a+")
                f.write(stderr.decode())
                f.write("\n\n" + "=" * 30 + "\n\n")
                f.close()
            except:
                f.close()
            chdir(old_path)
            return -1
        # Finding the file(s)   
        binaries = get_binary(".")
        # Check for binaries
        if not binaries:
            print("No binaries!")
            chdir(old_path)
            return -1
        if has_libraries("."):
            print("Has libraries!")
            chdir(old_path)
            return -1        
        # Checks for size
        for binary in binaries:
            # Check for  stripped
            if not is_stripped(binary):
                print("Can't control compilation flags")
                f = open("../../../not_controllable.txt", "a+")
                f.write(repo_url + "\n")
                f.close()
                chdir(old_path)
                return -1
        chdir("..")
        clear_directory(".")
        copytree(copy_path, prj_name, symlinks=True)
        chdir(prj_name)
        cmd = ['make', 'CXXFLAGS=-std=c++14 -lm -lpthread']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process.communicate()
        if stderr:
            print("Compilation error: ")
            try:
                f = open("../../../compilation_errors.txt", "a+")
                f.write(stderr.decode())
                f.write("\n\n" + "=" * 30 + "\n\n")
                f.close()
            except:
                f.close()
            chdir(old_path)
            return -1
        for binary in binaries:
            # Check for not stripped
            if is_stripped(binary):
                print("Can't control compilation flags")
                f = open("../../../not_controllable.txt", "a+")
                f.write(repo_url + "\n")
                f.close()
                chdir(old_path)
                return -1
        chdir("..")
        clear_directory(".")
    else:
        # Copying from cache
        copy_path = join("..", "..", "global_cache", prj_name)
        copytree(copy_path, prj_name, symlinks=True)
        chdir("../prj_dir")

    # Path here is ".../prj_dir"

    # Creating directory for outputs
    output_path = join("..", "..", "..", "..", PROJECTS_DIR, prj_name)
    # Checking if it exists
    if exists(output_path) and isdir(output_path):
        rmtree(output_path)
    mkdir(output_path)

    # STARTING TESTING
    # Not stripped
    i = 0
    copy_path = join("..", "cache", prj_name)
    for optimization_level in OPT_LEVEL:
        tester_logger.debug("Compiling the project with %s optimization." % optimization_level)
        # Need to copy the project in the current directory
        clear_directory(".")

        copytree(copy_path, prj_name, symlinks=True)
        chdir(prj_name)

        # Writing output files
        file_path_output = join("..", "..", "..", "..", "..", PROJECTS_DIR, prj_name, prj_name + "." + optimization_level + ".output.txt")
        file_path_false_positive = join("..", "..", "..", "..", "..", PROJECTS_DIR, prj_name, prj_name + "." + optimization_level + ".false.txt")
        file_path_recognized = join("..", "..", "..", "..", "..", PROJECTS_DIR, prj_name, prj_name + "." + optimization_level + ".recognized.txt")
        file_path_dwarf = join("..", "..", "..", "..", "..", PROJECTS_DIR, prj_name, prj_name + "." + optimization_level + ".dwarf.txt")
        f_output = open(file_path_output, "w")
        f_false = open(file_path_false_positive, "w")
        f_reco = open(file_path_recognized, "w")
        f_dwarf = open(file_path_dwarf, "w")
        f_output.write("Repository URL:\t" + repo_url + "\n\n")
        f_false.write("Repository URL:\t" + repo_url + "\n\n")
        f_reco.write("Repository URL:\t" + repo_url + "\n\n")
        f_dwarf.write("Repository URL:\t" + repo_url + "\n\n")

        # Compiling the project
        CXXFLAGS = 'CXXFLAGS=' + optimization_level +  ' -std=c++14 -gdwarf-4 -lm -lpthread'
        cmd = ['make', CXXFLAGS]        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process.communicate()

        # Finding the file(s)   
        binaries = get_binary(".")

        # Preparing counters
        stats = Statistics(query_db, optimization_level)

        # Retriving all of the inlined functions
        call_info = InlineSummary()
        binary_dwarf_list = []
        for binary in binaries:
            dwarf = Dwarf(binary)
            function_count = 0
            # Loading the binary with angr
            project = angr.Project(binary, load_options={'auto_load_libs': False})
            cfg = project.analyses.CFGFast(normalize=True)
            basic_blocks = []
            # Retriving all of the basic blocks
            for func in cfg.kb.functions.values():
                if func.size == 0:
                    continue
                for block in func.blocks:
                    if block.size == 0:
                        continue
                    basic_blocks.append(block)
            # Sorting basic blocks
            basic_blocks.sort(key=lambda x: x.addr)
            for mangled_name, ranges in dwarf.get_inlined_subroutines_info():
                class_name, function_name = demangle(mangled_name)
                if class_name not in classes:
                    continue
                # Need to count the number of basic blocks
                bb_count = basic_block_count(basic_blocks, ranges)
                if bb_count < MIN_BB:
                    continue
                if stats.add_function(mangled_name, class_name, function_name):
                    call_info.add_function(binary, mangled_name, ranges, bb_count)
                    function_count += 1
            if function_count > 0:
                binary_dwarf_list.append([binary, dwarf])

        # Testing
        # Generating configuration file
        conf = MatchingConfigs()
        conf.classes = classes
        conf.output_file = "tmp_results.json"
        conf.processes = PROCESSES
        conf.color_checking = COLOR_CHECKING
        conf.function_call_checking = FUNCTION_CALL_CHECKING
        conf.similarity_threshold = SIMILARITY_THRESHOLD
        conf.minimum_basic_blocks = MIN_BB
        conf.use_static_symbols = False
        if call_info.inline_info:
            i += 1
            for tuple_i in binary_dwarf_list:
                binary = tuple_i[0]
                dwarf = tuple_i[1]
                fingerprints_path = join("..", "..", "..", "..", "..", FINGERPRINT_DB_PATH)
                results_manager = tester(fingerprints_path, binary, conf)
                found_str = stats.add_results(results_manager, call_info, binary, dwarf)
                f_reco.write("File: " + binary + "\n\n")
                f_reco.write(found_str + "\n\n")
                f_false.write(str(results_manager) + "\n\n")
                out_manager.update_size(stat(binary).st_size)
                out_manager.update_bino_analysis_time(results_manager.bino_analysis_time)
                out_manager.update_angr_analysis_time(results_manager.angr_analysis_time)
            # Merging results in the output manager
            out_manager.merge_statistics(stats)
            # Writing results
            f_output.write(str(stats))
            f_dwarf.write(str(call_info))
            # Closing files
            f_output.close()
            f_false.close()
            f_reco.close()
            f_dwarf.close()
        else:
            # Closing files
            f_output.close()
            f_false.close()
            f_reco.close()
            f_dwarf.close()
            # Deleting files
            remove(file_path_output)
            remove(file_path_false_positive)
            remove(file_path_recognized)
            remove(file_path_dwarf)

        chdir("..")
        

    clear_directory(".")

    if i == 0:
        rmtree(output_path)
    else:
        # Increasing projects count
        out_manager.increase_project_number()

    # Caching the repo and returning
    if not cached and enable_cache:
        cache_dir_path = join("..", "..", "..", "..", CACHE_DIR, prj_name)
        copytree(copy_path, cache_dir_path, symlinks=True)
    chdir(old_path)
    return 0 


if __name__ == '__main__':
    sys.setrecursionlimit(0x100000)
    # Argument parsing
    parser = argparse.ArgumentParser(description="Git Tester.")
    parser.add_argument("-d",
                        "--debug",
                        dest="debug",
                        action="store_true",
                        help="Debug mode.")
    parser.add_argument("-cs",
                        "--classes", 
                        dest="classes_names",
                        nargs="+", 
                        help="List of classes to test. If not specified all classes inside the path are considered.")
    parser.add_argument("-ec",
                        "--enable-cache", 
                        dest="enable_cache",
                        action="store_true",
                        help="Projects are stored in a cache directory. If the testing phase is performed again, there's no need to clone them again.")
    args = parser.parse_args()
    # Arguments actions
    tester_logger = logging.getLogger('tester')
    if args.debug:
        tester_logger.setLevel(logging.DEBUG)
    else:
        tester_logger.setLevel(logging.INFO)
    if args.classes_names:
        classes = args.classes_names
    else:
        classes = None
    # Loggers
    tester_logger = logging.getLogger('tester')
    logging.getLogger('angr').setLevel('ERROR')
    logging.getLogger('cle').setLevel('ERROR')
    # Project path
    prj_path = dirname(abspath(__file__))
    # Initialize output file
    out_manager = OutputManager(OUTPUT)
    # Generating configuration file
    conf = MatchingConfigs()
    conf.classes = classes
    # Collecting fingerprints in order to know if we can recognize target functions
    query_db = FingerprintsManager(FINGERPRINT_DB_PATH_ARCH, conf, tester_logger)
    # Initialize files
    initialize_file(FILE_VALID_REPO)
    initialize_file(FILE_INVALID_REPO)
    # Checking projects directory
    if not exists(PROJECTS_DIR):
        mkdir(PROJECTS_DIR)
    # Checking working directory
    if not exists(WORKING_DIR):
        mkdir(WORKING_DIR)
    # Checking cache directory
    if not exists(CACHE_DIR):
        mkdir(CACHE_DIR)
    # Opening candidates
    f = open(CANDIDATES)
    content = f.read()
    f.close()
    for line in content.split("\n"):
        api_path = line.split('"')[1]
        if in_file(FILE_VALID_REPO, api_path) or in_file(FILE_INVALID_REPO, api_path):
            continue
        print("Testing " + api_path)
        repo_url = get_github_url(api_path)
        # Testing repo
        results = test_repository(repo_url, out_manager, query_db, classes, tester_logger, args.enable_cache)
        if results == -1:
            # Add to invalid repo
            f = open(FILE_INVALID_REPO, "a")
            f.write(api_path + "\n")
            f.close()
            time.sleep(5)
        else:
            f = open(FILE_VALID_REPO, "a")
            f.write(api_path + "\n")
            f.close()
            out_manager.update_files()
        print("Done.")