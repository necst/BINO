#!/usr/bin/python3

import argparse
from fingerprint.utils.helper import plot_fingerprint
from fingerprint.classes.fingerprint import load_fingerprint
from utils.name_mangling import demangle
from os.path import join
from os import listdir
from fingerprint.internal_classes.fingerprints_collections import FingerprintsCollections

FINGERPRINT_PATH = "data/fingerprint"

if __name__ == '__main__':
    # Argument parsing
    parser = argparse.ArgumentParser(description="Fingerprints Collections Viewer.")

    parser.add_argument("-f",
                        "--file",
                        dest="file",
                        default=None,
                        help="File of the fingerprint collection.")
    parser.add_argument("-m",
                        "--mangled-name",
                        dest="mangled",
                        help="Mangled name of the method to inspect.")
    parser.add_argument("-fn",
                        "--function-name",
                        dest="func_name",
                        help="Name of the method to inspect.")
    parser.add_argument("-cn",
                        "--class-name",
                        dest="class_name",
                        help="Name of the class to inspect.")
    args = parser.parse_args()
    if args.file is not None:
        fp = load_fingerprint(args.file)
        plot_fingerprint(fp)
    elif args.mangled is not None:
        class_name, method = demangle(args.mangled)
        fingerprint_path = join(FINGERPRINT_PATH, class_name, "public")
        for method_dir in listdir(fingerprint_path):
            if (method + "__") in method_dir:
                method_path = join(fingerprint_path, method_dir)
                for file in listdir(method_path):
                    if ".json" in file:
                        continue
                    file_path = join(method_path, file)
                    fp = load_fingerprint(file_path)
                    if fp.function_details.mangled_name == args.mangled:
                        print(fp)
                        plot_fingerprint(fp)
