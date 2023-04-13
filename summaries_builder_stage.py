#!/usr/bin/python3

import argparse
import logging
import sys
from os.path import dirname, abspath, join, isdir, exists, isfile
from os import listdir
from stages.summary_builder import summary_builder

DEFAULT_SRC_PATH = "data/building_procedures/"
DEFAULT_DST_PATH = "data/classes_summaries/"

def dir_path(path):
    if not isdir(path):
        raise argparse.ArgumentTypeError(path + " is not a valid directory path.")
    return path

def file_path(path):
    if not isfile(path):
        raise argparse.ArgumentTypeError(path + " is not a valid file path.")
    return path

if __name__ == '__main__':
    """
    TODO
    """

    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Argument parsing
    parser = argparse.ArgumentParser(description="Summaries Builder. It builds json that specifies " +
                                     "methods of a class along with parameters type and return type starting from building procedures jsons.")
    parser.add_argument("-d",
                        "--debug",
                        dest="debug",
                        action="store_true",
                        help="Debug mode.")
    parser.add_argument("-bpp",
                        "--building-procedures-path",
                        dest="bs_path",
                        type=dir_path,
                        help="Path to a directory which constains building procedures.")
    parser.add_argument("-bpf",
                        "--building-procedures-file",
                        dest="bs_file",
                        type=file_path,
                        help="Path to a file which is a building procedure.")
    parser.add_argument("-dest-path",
                        "--destination-path",
                        dest="destination_path",
                        type=dir_path,
                        help="Destination path of the sources.")
    args = parser.parse_args()
    # Arguments actions
    summary_logger = logging.getLogger('summary_builder')
    if args.debug:
        summary_logger.setLevel(logging.DEBUG)
    else:
        summary_logger.setLevel(logging.INFO)
    summary_logger.addHandler(logging.StreamHandler(sys.stdout))
    if args.bs_path is not None and args.bs_file is not None:
        raise Exception("Path of building procedures and file of a building procedure selected at the same time.")
    # Fixing destination
    if args.destination_path != None:
        summaries_path = args.destination_path
    else:
        summaries_path = DEFAULT_DST_PATH
    # Calling the summary builder with the correct parameters     
    if args.bs_path is not None:
        for file in listdir(args.bs_path):
            procedure_path = join(args.bs_path, file)
            summary_builder(procedure_path, summaries_path)
    elif args.bs_file is not None:
        summary_builder(args.bs_file, summaries_path)
    else:
        for file in listdir(DEFAULT_SRC_PATH):
            procedure_path = join(DEFAULT_SRC_PATH, file)
            summary_builder(procedure_path, summaries_path)