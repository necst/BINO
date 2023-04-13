#!/usr/bin/python3

import argparse
import logging
from os.path import dirname, abspath, join, isdir
from os import listdir
from stages.fingerprinter import fingerprinter
from utils.helper import clear_directory

E_FUNCTIONS_PATH = "data/fingerprint"

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
    # Clearing fingerprint directory
    clear_directory(E_FUNCTIONS_PATH)
    # Argument parsing
    parser = argparse.ArgumentParser(description="Fingerprinter.")
    parser.add_argument("-d",
                        "--debug",
                        dest="debug",
                        action="store_true",
                        help="Debug mode.")
    parser.add_argument("-bp",
                        "--binaries-path",
                        dest="binaries_path",
                        type=dir_path,
                        help="Path to a directory which constains binaries of different classes.")
    parser.add_argument("-sbp",
                        "--single-binaries-path",
                        dest="single_binaries_path",
                        type=dir_path,
                        help="Path to a directory which constains binaries of a single class.")
    parser.add_argument("-dp",
                        "--destination-path",
                        dest="destination_path",
                        type=dir_path,
                        help="Destination path of the fingerprints.")
    args = parser.parse_args()
    # Arguments actions
    fp_logger = logging.getLogger('fingerprinter')
    if args.debug:
        fp_logger.setLevel(logging.DEBUG)
    else:
        fp_logger.setLevel(logging.INFO)
    if args.binaries_path != None and args.single_binaries_path != None:
        raise Exception("Single binaries path and multiple binaries path selected at the same time.")
    if args.destination_path:
        destination_path = args.destination_path
    else:
        destination_path = join(prj_path, "data", "fingerprint")
    fp_logger.debug("Used fingerprints path: " + destination_path)
    if args.single_binaries_path != None:
        # Run a single preprocessing build
        fp_logger.debug("Used single binaries path: " + args.single_binaries_path)
        fingerprinter(args.single_binaries_path, destination_path)
    else:
        if args.binaries_path:
            binaries_path = args.binaries_path
        else:
            binaries_path = join(prj_path, "data", "binaries")
        fp_logger.debug("Used binaries path: " + binaries_path)
        for file in listdir(binaries_path):
            fingerprinter(join(binaries_path, file), destination_path)