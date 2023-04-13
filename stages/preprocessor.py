from os.path import dirname, abspath, join, isdir, exists, isfile, split
from os import listdir, mkdir, system
from shutil import rmtree
import subprocess
import logging
from os.path import abspath, dirname
import json

def _generate_data_types(tokens):
    if len(tokens) == 1:
        token_name = tokens[0]["token_name"]
        token_values = tokens[0]["token_values"]
        new_tokens = []
        for value in token_values:
            new_tokens.append([{"token_name": token_name, "token_value": value}])
        return new_tokens
    token_name = tokens[0]["token_name"]
    token_values = tokens[0]["token_values"]
    new_tokens = []
    for next_tokens in _generate_data_types(tokens[1:]):
        for value in token_values:
            new_tokens.append([{"token_name": token_name, "token_value": value}] + next_tokens)
    return new_tokens


def _preprocess_directory(src_path, dst_path, preprocessor_logger, directory):
    directory_src_path = join(src_path, directory)
    directory_dst_path = join(dst_path, directory)
    if not exists(directory_src_path) or not isdir(directory_src_path):
        raise Exception("Path " + directory_src_path + " doesn't exists!")
    if exists(directory_dst_path) and isdir(directory_dst_path):
        rmtree(directory_dst_path)
    mkdir(directory_dst_path)
    for source_file in listdir(directory_src_path):
        # Handling json with .cpp
        if source_file[-5:] == ".json":
            continue
        # Reading json
        old_json_path = join(directory_src_path, source_file[:-4] + ".json")
        with open(old_json_path) as f:
            old_json = json.load(f)
        source_file_path = join(directory_src_path, source_file)
        if not isfile(source_file_path):
            raise Exception(source_file_path + " is not a file.")
        data_types = _generate_data_types(old_json["tokens"])
        method_name = source_file.split(".")[0]
        directory_method_path = join(directory_dst_path, method_name)
        mkdir(directory_method_path)
        j = 1
        for data_type in data_types:
            compiling_define = []
            preprocessed_name = source_file.split(".")[0]
            for token in data_type:
                compiling_define.append("-D" + token["token_name"] + "=" + token["token_value"])
            preprocessed_name += "_" + str(j)
            preprocessed_name += ".i"
            preprocessed_path = join(directory_method_path, preprocessed_name)
            cmd = ["cc" , "-E", source_file_path, "-o", preprocessed_path]
            cmd += compiling_define
            # Preprocessed file
            cmd = ["cc" , "-E", source_file_path, "-o", preprocessed_path]
            cmd += compiling_define
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            stderr = process.stderr.read()
            if stderr:
                preprocessor_logger.error("[ERROR] Compilation error with the command:\n" +
                                          ' '.join(cmd) + '\n'
                                          "Error:\n" + stderr.decode("utf-8"))
                continue
            else:
                preprocessor_logger.debug("[DEBUG] " + ' '.join(cmd))
            # Json file
            dict_json = old_json.copy()
            dict_json["types"] = data_type
            del dict_json["tokens"]
            json_name = preprocessed_name.split(".i")[0] + ".json"
            json_path = join(directory_method_path, json_name)
            with open(json_path, 'w') as fp:
                json.dump(dict_json, fp, indent=2)
            j += 1

def preprocessor(src_path, dst_path):
    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Logger
    preprocessor_logger = logging.getLogger('preprocessor')
    # Path checks
    if not isdir(src_path):
        raise Exception(src_path + " is not a file path")
    if not isdir(dst_path):
        raise Exception(dst_path + " is not a file path")
    # Compilation section
    preprocessor_logger.info("[INFO] Joining " + src_path + " directory.")
    directory = split(src_path)[1]
    # Preprocess all of the files in the binaries folder
    # Step 1: creating the folder. Also checking if the folder
    # already exists
    directory_dst_path = join(dst_path, directory)
    if exists(directory_dst_path) and isdir(directory_dst_path):
        # Remove the directory and its content
        rmtree(directory_dst_path)
        preprocessor_logger.debug("[DEBUG] Removed " + directory_dst_path + " directory.")
    mkdir(directory_dst_path)
    preprocessor_logger.debug("[DEBUG] Created " + directory_dst_path + " directory.")
    # Step 2: for all file preprocess it N times with different
    # data types. All of the files of a compiler configuration 
    # must be collected in a folder. Every file contains a 
    # C/C++ define not defined to define at compilation time.
    preprocessor_logger.info("[INFO] Preprocessing methods...")
    _preprocess_directory(src_path, directory_dst_path, preprocessor_logger, "public")
    preprocessor_logger.info("[INFO] Preprocessed methods.")
    preprocessor_logger.info("[INFO] Preprocessing done.")
