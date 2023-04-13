#!/usr/bin/python3.7

from os.path import dirname, abspath, join, isdir, exists, isfile, split
from os import listdir, mkdir, system, remove
from shutil import rmtree, copyfile
from parsing.classes.cpp_parser import CppParser
from clang.cindex import CursorKind
from operator import itemgetter
import subprocess
import logging
import json
from configurations.utils.helper import get_cpp_version
from utils.compiler import get_gpp_version
from multiprocessing import Process


COMPILER_OPTS = ["-O2", "-O3", "-Os", "-Ofast"]
PARALLEL_PROCESS = 16

"""
Compiler's goal is to compile with the options provided above, parse the sources
to get the mangled names of the functions that are getting called inside the methos,
edit the json to add such knowledge with mangled names and finally generate the gcc
summary of inlining.
"""

def _get_file_offset(calls_info, mang_name):
    for val in calls_info:
        if val[0] == mang_name:
            return val[1]
    return -1

def _remove_duplicates(offsets):
    offsets_indexes = []
    for offset in offsets:
        if offset[0] not in offsets_indexes:
            offsets_indexes.append(offset[0])
    offsets_indexes = list(set(offsets_indexes))
    new_offsets = []
    for offset_index in offsets_indexes:
        for offset in offsets:
            if offset_index == offset[0]:
                new_offsets.append(offset)
                break
    return new_offsets


def _get_functions_called_info(method_definition):
    functions_info = []
    mangled_names = []
    definitions = [method_definition]
    while definitions:
        current_definition = definitions.pop(0)
        list_calls = current_definition.get_called_functions()
        for call in list_calls:
            call_definition = call.get_definition()
            if call_definition is not None:
                if not call_definition.node.mangled_name:
                    raise Exception("Method without mangled name!")
                mangled_name = call_definition.node.mangled_name
                offset = call_definition.node.location.offset
                if (mangled_name not in mangled_names and
                    mangled_name != method_definition.node.mangled_name):
                    mangled_names.append(mangled_name)
                    functions_info.append([mangled_name, offset])
                    definitions.append(call_definition)
    return functions_info

def _get_function_sizes(info_inliner):
    sizes = []
    lines = info_inliner.split("\n")
    i = 0
    for line in lines:
        i += 1
        if "self size:" in line:
            if "int main" in lines[i - 4]:      
                continue
            if "void wrapper" in lines[i - 4]:
                continue   
            size = int(line.split("self size:")[1].strip(" "))
            sizes.append(size)
    sizes = list(set(sizes))
    sizes.sort(reverse=True)
    return sizes


def _get_inlined_method_definition(cpp_object, preprocessed_src_path, method_name):
    # Retrieving function wrapper
    list_defs = cpp_object.get_function_definitions("wrapper")
    # Retrieving the call to the method
    list_calls = list_defs[0].get_called_functions()
    for call in list_calls:
        definition = call.get_definition()
        if definition != None:
            if definition.name == method_name:
                return definition
    return None

def _compiler_directory_multiprocess(directory_src_path, directory_dst_path, method, gpp_version, cpp_version, compiler_logger):
    method_src_path = join(directory_src_path, method)
    method_dst_path = join(directory_dst_path, method)
    mkdir(method_dst_path)
    # 2nd step: compile and place in folders
    j = 1
    methods = listdir(method_src_path)
    for preprocessed_src in methods:
        # Not considering json directly
        if preprocessed_src[-5:] == ".json":
            continue
        # Loading json output of preprocessor
        old_json_path = join(method_src_path, preprocessed_src[:-2] + ".json")
        with open(old_json_path) as f:
            old_json = json.load(f)
        # Parsing method to get the function called inside
        preprocessed_src_path = join(method_src_path, preprocessed_src)
        cpp_object = CppParser(preprocessed_src_path, include_headers=True)
        method_definition = _get_inlined_method_definition(cpp_object, preprocessed_src_path, old_json["method_name"])
        if method_definition is None:
            compiler_logger.info("[INFO] Compilation error with file: " + preprocessed_src_path)
            continue
        method_mangled_name = method_definition.mangled_name
        calls_info = _get_functions_called_info(method_definition)
        method_offset = method_definition.node.location.offset 
        if calls_info:
            old_json['calls'] = [i[0] for i in calls_info]
        else:
            old_json['calls'] = []
        # Compiling and getting info about inlined calls
        for opt in COMPILER_OPTS:
            cmd = ["g++" , "-std=" + cpp_version, "-fdump-ipa-inline-optimized-missed=/dev/stdout", opt, "-fno-access-control", "-w", preprocessed_src_path, "-o","/dev/null" ]
            if "compiler_options" in old_json.keys():
                for opt2 in old_json["compiler_options"]:
                    cmd += [opt2]
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                compiler_logger.error("[ERROR] Compilation error with the command:\n" +
                                            ' '.join(cmd) + '\n'
                                            "Error:\n" + stderr.decode("utf-8"))
                continue
            info_inliner = stdout.decode("utf-8")
            # From the inline info we need to retrieve the sizes of the functions
            sizes = _get_function_sizes(info_inliner)
            # Checking for duplicates
            if set(old_json['calls']) != set(list(set(old_json['calls']))):
                raise Exception("Duplicates in parsing function calls for file " + preprocessed_src_path + "!")
            if not sizes:
                sizes = [-1]
            else:
                sizes = [1, 500]
            for size in sizes:
                binary_name = method + "_" + str(j)
                binary_path = join(method_dst_path,  binary_name)
                # Compiling
                if size == -1:
                    cmd = ["g++" , "-std=" + cpp_version, opt, "-fno-access-control", "-w", preprocessed_src_path, "-o", binary_path]
                else:
                    cmd = ["g++" , "-std=" + cpp_version, opt, "-fno-access-control", "-w", preprocessed_src_path, "-o", binary_path, "--param", "max-inline-insns-auto=" + str(size)]
                if "compiler_options" in old_json.keys():
                    for opt2 in old_json["compiler_options"]:
                        cmd += [opt2]
                process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=None)
                stderr = process.stderr.read()
                if stderr:
                    compiler_logger.error("[ERROR] Compilation error with the command:\n" +
                                                ' '.join(cmd) + '\n'
                                                "Error:\n" + stderr.decode("utf-8"))
                    raise Exception("Failed in forcing no inline for file " + preprocessed_src_path + ".")
                else:
                    compiler_logger.debug("[DEBUG] " + ' '.join(cmd))
                # Renaming json and adding compile opt
                new_json_name = method + "_" + str(j) + ".json"
                new_json_path = join(method_dst_path,  new_json_name)
                new_json = old_json.copy()
                new_json['optimization'] = opt
                new_json['mangled_name'] = method_mangled_name
                new_json['function_name'] = new_json['method_name'] 
                new_json['path_name'] = new_json['class_name']
                new_json['compiler_version'] = gpp_version
                new_json['cpp_version'] = cpp_version
                del new_json['class_name']
                del new_json['method_name']
                with open(new_json_path, 'w') as f:
                    json.dump(new_json, f, indent=2)
                j += 1
    if j == 1:
        rmtree(method_dst_path)

def _compile_directory(src_path, dst_path, compiler_logger, directory):
    directory_src_path = join(src_path, directory)
    directory_dst_path = join(dst_path, directory)
    if not exists(directory_src_path) or not isdir(directory_src_path):
        raise Exception("Path " + directory_src_path + " doesn't exists!")
    if exists(directory_dst_path) and isdir(directory_dst_path):
        rmtree(directory_dst_path)
    mkdir(directory_dst_path)
    # Retrieving compiler version
    gpp_version = get_gpp_version()
    # Loading cpp version from configuration file
    cpp_version = get_cpp_version()
    # Spawning Processes
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
            p = Process(target=_compiler_directory_multiprocess, 
                        args=(directory_src_path,
                                directory_dst_path,
                                dir_src_path_list[i],
                                gpp_version,
                                cpp_version,
                                compiler_logger))
            processes.append(p)
        # Launching them
        for p in processes:
            p.start()
        # Waiting them
        for p in processes:
            p.join()

def compiler(src_path, dst_path):
    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Logger
    compiler_logger = logging.getLogger('compiler')
    # Path checks
    if not isdir(src_path):
        raise Exception(src_path + " is not a directory path")
    if not isdir(dst_path):
        raise Exception(dst_path + " is not a directory path")
    # Compilation section
    compiler_logger.info("[INFO] Joining " + src_path + " directory.")
    directory = split(src_path)[1]
    # Creating destination directory
    directory_dst_path = join(dst_path, directory)
    if exists(directory_dst_path) and isdir(directory_dst_path):
        rmtree(directory_dst_path)
        compiler_logger.debug("[DEBUG] Removed " + directory_dst_path + " directory.")
    mkdir(directory_dst_path)
    compiler_logger.debug("[DEBUG] Created " + directory_dst_path + " directory.")
    # Compiling methods
    compiler_logger.info("[INFO] Compiling methods...")
    _compile_directory(src_path, directory_dst_path, compiler_logger, "public")
    compiler_logger.info("[INFO] Methods compiled.")
