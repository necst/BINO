#!/usr/bin/python3

import argparse
import logging
from os.path import dirname, abspath, join, isdir, exists, isfile
from stages.tester import tester
from fingerprint.matching.matching_configurations import MatchingConfigs
import multiprocessing as mp

FINGERPRINT_DB_PATH = "data/fingerprints_db"

def dir_path(path):
    if not isdir(path):
        raise argparse.ArgumentTypeError(path + " is not a valid directory path.")
    return path


def file_path(path):
    if not isfile(path):
        raise argparse.ArgumentTypeError(path + " is not a valid file path.")
    return path


def valid_path(path):
    if not exists(path):
        raise argparse.ArgumentTypeError(path + " is not a valid path.")
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
    parser = argparse.ArgumentParser(description="Tester.")
    parser.add_argument(dest="test_binary_path",
                        type=file_path,
                        help="Binary to test.")
    parser.add_argument("-d",
                        "--debug",
                        dest="debug",
                        action="store_true",
                        help="Debug mode.")
    parser.add_argument("-fp",
                        "--fingerprints-path",
                        dest="fingerprints_path",
                        type=dir_path,
                        help="Path to a directory which constains fingerprints of different classes.")
    parser.add_argument("-cs",
                        "--classes", 
                        dest="classes_names",
                        nargs="+", 
                        help="List of classes to test. If not specified all classes inside the path are considered.")
    parser.add_argument("-o",
                        "--output-file",
                        dest="output_file",
                        help="Path to a file which will contain the output of the test. If not specified will print on stdout.")
    parser.add_argument("-mbb",
                        "--minimum-basic-blocks",
                        dest="min_bb",
                        default=5,
                        type=int,
                        help="Minimum number of basic block.")
    parser.add_argument("-ec",
                        "--enable-color",
                        dest="color_check",
                        action="store_true",
                        help="Enable color strategy.")
    parser.add_argument("-s",
                        "--similarity",
                        dest="similarity_threshold",
                        default=0.88,
                        type=float,
                        help="Sets the similarity value.")
    parser.add_argument("-efc",
                        "--enable-function-call",
                        dest="function_call_check",
                        action="store_true",
                        help="Enable function call checking.")
    parser.add_argument("-css",
                        "--check-static-symbols",
                        dest="check_static_symbols",
                        action="store_true",
                        help="Check static symbols, i.e., symbols of the binary.")
    parser.add_argument("-p",
                        "-processes",
                        dest="processes",
                        default=1,
                        type=int,
                        help="Number of processes to use.")
    args = parser.parse_args()
    # Arguments actions
    tester_logger = logging.getLogger('tester')
    if args.debug:
        tester_logger.setLevel(logging.DEBUG)
    else:
        tester_logger.setLevel(logging.INFO)
    if args.fingerprints_path != None:
        fingerprints_path = args.fingerprints_path
    else:
        fingerprints_path = join(prj_path, FINGERPRINT_DB_PATH)
    conf = MatchingConfigs()
    if not args.color_check:
        conf.color_checking = False
    else:
        conf.color_checking = True
        conf.similarity_threshold = args.similarity_threshold
    if not args.function_call_check:
        conf.function_call_checking = False
    else:
        conf.function_call_checking = True
    conf.processes = args.processes
    if conf.processes > mp.cpu_count():
        raise Exception("Cannot spawn %d processes. Your machine only have %d!" % (conf.processes, mp.cpu_count()))
    conf.minimum_basic_blocks = args.min_bb
    if args.classes_names is not None:
        conf.classes = args.classes_names
    else:
        conf.classes = None
    if args.output_file is not None:
        conf.output_file = args.output_file
    else:
        conf.output_file = None
    if args.check_static_symbols:
        conf.use_stati_symbols = True
    else:
        conf.use_stati_symbols = False
    tester_logger.debug("Used binaries path: " + args.test_binary_path)
    tester_logger.debug("Used fingerprints path: " + fingerprints_path)
    tester_logger.debug("Configurations:")
    for line in conf.pp().split("\n"):
        tester_logger.debug(" -" + line)
    tester(fingerprints_path, args.test_binary_path, conf)