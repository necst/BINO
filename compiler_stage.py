#!/usr/bin/python3

import argparse
import logging
import sys
from os.path import dirname, abspath, join, isdir, exists, isfile
from os import listdir
from stages.compiler import compiler

def dir_path(path):
    if not isdir(path):
        raise argparse.ArgumentTypeError(path + " is not a valid directory path.")
    return path

if __name__ == '__main__':
    """
    The goal of this script is to preprocess the sources generated in the
    previous stage(sources building stage) in order to have a single file
    in which we have the entire source code needed to compile a function.
    This stage is not useful at the moment, it can be useful if we need to
    change something in the code, i.e., force the inline of a specific method.
    """

    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Argument parsing
    parser = argparse.ArgumentParser(description="Compiler. It compiles all the preprocessed source files.")
    parser.add_argument("-d",
                        "--debug",
                        dest="debug",
                        action="store_true",
                        help="Debug mode.")
    parser.add_argument("-sp",
                        "--sources-path",
                        dest="sources_path",
                        type=dir_path,
                        help="Path to a directory which constains preprocessed source files of different classes.")
    parser.add_argument("-sources-path",
                        "--single-sources-path",
                        dest="single_sources_path",
                        type=dir_path,
                        help="Path to a directory which constains preprocessed source files of a single class.")
    parser.add_argument("-dest-path",
                        "--destination-path",
                        dest="destination_path",
                        type=dir_path,
                        help="Destination path of the binaries.")
    args = parser.parse_args()
    # Arguments actions
    compiler_logger = logging.getLogger('compiler')
    if args.debug:
        compiler_logger.setLevel(logging.DEBUG)
    else:
        compiler_logger.setLevel(logging.INFO)
    compiler_logger.addHandler(logging.StreamHandler(sys.stdout))
    if args.sources_path != None and args.single_sources_path != None:
        raise Exception("Single sources path and multiple sources path selected at the same time.")
    if args.destination_path:
        destination_path = args.destination_path
    else:
        destination_path = join(prj_path, "data", "binaries")
    compiler_logger.debug("[DEBUG] Used binary path: " + destination_path)
    if args.single_sources_path != None:
        # Run a single preprocessing build
        compiler_logger.debug("[DEBUG] Used single preprocessed sources path: " + args.single_sources_path)
        compiler(args.single_sources_path, destination_path)
    else:
        if args.sources_path:
            sources_path = args.sources_path
        else:
            sources_path = join(prj_path, "data", "preprocessed_sources")
        compiler_logger.debug("[DEBUG] Used preprocessed sources path: " + sources_path)
        for file in listdir(sources_path):
            compiler(join(sources_path, file), destination_path)