#!/usr/bin/python3

import argparse
import logging
import sys
from os.path import dirname, abspath, join, isdir, exists, isfile
from os import listdir
from stages.sources_builder import sources_builder

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
    The goal of this script is to build the source code of all 
    the public methods in a class.
    """

    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Argument parsing
    parser = argparse.ArgumentParser(description="Sources Builder. It builds sources " +
                                     " starting from classes summary jsons.")
    parser.add_argument("-d",
                        "--debug",
                        dest="debug",
                        action="store_true",
                        help="Debug mode.")
    parser.add_argument("-csp",
                        "--classes-summaries-path",
                        dest="cs_path",
                        type=dir_path,
                        help="Path to a directory which constains classes summaries.")
    parser.add_argument("-csf",
                        "--class-summary-file",
                        dest="cs_file",
                        type=file_path,
                        help="File path to a class summary.")
    parser.add_argument("-dest-path",
                        "--destination-path",
                        dest="destination_path",
                        type=dir_path,
                        help="Destination path of the sources.")
    args = parser.parse_args()
    # Arguments actions
    builder_logger = logging.getLogger('sources_builder')
    if args.debug:
        builder_logger.setLevel(logging.DEBUG)
    else:
        builder_logger.setLevel(logging.INFO)
    builder_logger.addHandler(logging.StreamHandler(sys.stdout))        
    if args.cs_path != None and args.cs_file != None:
        raise Exception("Path of classes summaries and file of a class summary selected at the same time.")
    if args.destination_path != None:
        sources_path = args.destination_path
    else:
        sources_path = join(prj_path, "data", "sources")
    builder_logger.debug("[DEBUG] Used sources path: " + sources_path)
    if args.cs_file == None:
        if args.cs_path != None:
            classes_summaries_path = args.cs_path
        else:
            classes_summaries_path = join(prj_path, "data", "classes_summaries")
        builder_logger.debug("[DEBUG] Used building procedures path: " + classes_summaries_path)
        for file in listdir(classes_summaries_path):
            class_summary_file_path = join(classes_summaries_path, file)
            sources_builder(class_summary_file_path, sources_path)
    else:
        builder_logger.debug("[DEBUG] Used building procedure file: " + args.cs_file)
        sources_builder(args.cs_file, sources_path)

    
    
