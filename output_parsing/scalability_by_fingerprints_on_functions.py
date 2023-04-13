import sys
sys.path.insert(0, '..')
import argparse
import os
from classes.projects_results import ProjectsResults
from fingerprint.classes.fingerprints_collection import load_fingerprints_collection

M = 5
PROJECTS_DIR = os.path.join("github_projects", "projects")
OPTS = []
OPTS += ["-O2"]
OPTS += ["-O3"]
OPTS += ["-Ofast"]
OPTS += ["-Os"]


def dir_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(path + " is not a valid directory path.")
    return path


def compute_fingerprints_amount(prj_path, class_name):
    fdb_path = os.path.join(prj_path, "..", "data", "fingerprints_db", "amd64", class_name)
    n_fps = 0
    for fpc_dir in os.listdir(fdb_path):
        nodes = int(fpc_dir.split("_")[0])
        if nodes < M:
            continue
        fpc_path = os.path.join(fdb_path, fpc_dir)
        for fpc_file in os.listdir(fpc_path):
            fpc_file_path = os.path.join(fpc_path, fpc_file)
            fpc = load_fingerprints_collection(fpc_file_path)
            n_fps += len(fpc.fingerprints_details)
    return n_fps



if __name__=="__main__":
    # Projecj path
    prj_path = os.path.dirname(os.path.abspath(__file__))
    # Argument parsing
    parser = argparse.ArgumentParser(description="Script to test M.")
    # Required argument
    parser.add_argument(dest="test_dir",
                        type=dir_path,
                        help="Directory that contains the experiments' results.")    
    args = parser.parse_args()
    # Iterating over classes under test
    test_dir = args.test_dir
    classes = os.listdir(test_dir)
    for class_i in classes:
        prjs_i_path = os.path.join(test_dir, class_i, PROJECTS_DIR)
        # Directory prjs_directory must exists
        if not os.path.exists(prjs_i_path) or not os.path.isdir(prjs_i_path):
            raise Exception("Directory must contains a directory for each class under test and inside of them the \"github_projects\" directory.")
        prjs_res = ProjectsResults(prjs_i_path)
        avg_func_time, _, _ = prjs_res.get_avg_function_time()
        n_fps = compute_fingerprints_amount(prj_path, class_i)
        print("Average function time for class %s is %f" %(class_i, avg_func_time))
        print("Fingeprints amount for class %s is %d" %(class_i, n_fps))