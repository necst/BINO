#!/usr/bin/python3

import argparse
from fingerprint.utils.helper import plot_fingerprint
from fingerprint.classes.fingerprints_collection import load_fingerprints_collection
from utils.name_mangling import demangle
from os.path import join
from fingerprint.internal_classes.fingerprints_collections import FingerprintsCollections

DB_PATH = "data/fingerprints_db/amd64/"

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
        fpc = load_fingerprints_collection(args.file)
        plot_fingerprint(fpc)
    elif args.mangled is not None:
        class_name, method = demangle(args.mangled)
        db_path = join(DB_PATH, class_name)
        fpscs = FingerprintsCollections(db_path, class_name)
        for fpc in fpscs.get_fingerprints_collections():
            if args.mangled in fpc.get_function_mangled_names():
                print("Fingerprint has %d nodes and %d edges." % (fpc.get_basic_blocks_count(), fpc.get_edges_count()))
                for detail in fpc.fingerprints_details:
                    if args.mangled in detail.get_function_mangled_names():
                        print(detail.pp())
                        break
                plot_fingerprint(fpc)
    elif args.func_name is not None and args.class_name is not None:
        db_path = join(DB_PATH, args.class_name)
        fpscs = FingerprintsCollections(db_path, args.class_name)
        for fpc in fpscs.get_fingerprints_collections():
            for mangled in fpc.get_function_mangled_names():
                _, method_name = demangle(mangled)
                if method_name == args.func_name:
                    print("Fingerprint has %d nodes and %d edges." % (fpc.get_basic_blocks_count(), fpc.get_edges_count()))

                    plot_fingerprint(fpc)
                    break
