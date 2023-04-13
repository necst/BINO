#!/usr/bin/python3

import argparse
import logging
import sys
from os.path import dirname, abspath, join, isdir, exists, isfile
from os import listdir
from stages.preprocessor import preprocessor

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
    parser = argparse.ArgumentParser(description="Preprocessor. It generates source" +
                                     " files for each method in which is contained all the code of that specific method.")
    parser.add_argument("-d",
                        "--debug",
                        dest="debug",
                        action="store_true",
                        help="Debug mode.")
    parser.add_argument("-sp",
                        "--sources-path",
                        dest="sources_path",
                        type=dir_path,
                        help="Path to a directory which constains source files of different classes.")
    parser.add_argument("-sources-path",
                        "--single-sources-path",
                        dest="single_sources_path",
                        type=dir_path,
                        help="Path to a directory which constains source files of a single class.")
    parser.add_argument("-dest-path",
                        "--destination-path",
                        dest="destination_path",
                        type=dir_path,
                        help="Destination path of the preprocessed sources.")
    args = parser.parse_args()
    # Arguments actions
    preprocessor_logger = logging.getLogger('preprocessor')
    if args.debug:
        preprocessor_logger.setLevel(logging.DEBUG)
    else:
        preprocessor_logger.setLevel(logging.INFO)
    preprocessor_logger.addHandler(logging.StreamHandler(sys.stdout))
    if args.sources_path != None and args.single_sources_path != None:
        raise Exception("Single sources path and multiple sources path selected at the same time.")
    if args.destination_path:
        destination_path = args.destination_path
    else:
        destination_path = join(prj_path, "data", "preprocessed_sources")
    preprocessor_logger.debug("[DEBUG] Used preprocessed sources path: " + destination_path)
    if args.single_sources_path != None:
        # Run a single preprocessing build
        preprocessor_logger.debug("[DEBUG] Used single sources path: " + args.single_sources_path)
        preprocessor(args.single_sources_path, destination_path)
    else:
        if args.sources_path:
            sources_path = args.sources_path
        else:
            sources_path = join(prj_path, "data", "sources")
        preprocessor_logger.debug("[DEBUG] Used sources path: " + sources_path)
        for file in listdir(sources_path):
            preprocessor(join(sources_path, file), destination_path)