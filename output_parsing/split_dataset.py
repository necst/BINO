import os
import argparse
import shutil
import random


OUTPUT_DIR = "splitted"
TRAINING_DIR = "training"
TESTING_DIR = "testing"
PROJECTS_DIR = os.path.join("github_projects", "projects")


def dir_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(path + " is not a valid directory path.")
    return path


def remove_projects(prjs_dir, prjs):
    to_be_removed = []
    all_prjs = os.listdir(prjs_dir)
    for prj in all_prjs:
        if prj not in prjs:
            to_be_removed.append(prj)
    for prj in to_be_removed:
        prj_path = os.path.join(prjs_dir, prj)
        shutil.rmtree(prj_path)


if __name__=="__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Dataset splitter.")
    # Required argument
    parser.add_argument(dest="test_dir",
                        type=dir_path,
                        help="Directory that contains the experiments' results.")    
    args = parser.parse_args()
    test_dir = args.test_dir
    if test_dir.endswith("/"):
        test_dir = test_dir[:-1]
    new_test_path = os.path.split(test_dir)[0]
    dir_name = os.path.split(test_dir)[1]
    output_path = os.path.join(new_test_path, OUTPUT_DIR)
    if os.path.exists(output_path) and os.path.isdir(output_path):
        raise Exception("Splitted dataset already exists!")
    # Training
    training_dir = os.path.join(output_path, TRAINING_DIR, dir_name)
    # Testing
    testing_dir = os.path.join(output_path, TESTING_DIR, dir_name)
    # Copying
    shutil.copytree(test_dir, training_dir)
    shutil.copytree(test_dir, testing_dir)
    # For each class split the dataset
    for class_i in os.listdir(test_dir):
        prjs_i_path = os.path.join(test_dir, class_i, PROJECTS_DIR)
        # Directory prjs_directory must exists
        if not os.path.exists(prjs_i_path) or not os.path.isdir(prjs_i_path):
            raise Exception("Directory must contains a directory for each class under test and inside of them the \"github_projects\" directory.")
        prjs = os.listdir(prjs_i_path)
        training_prjs = random.sample(prjs, len(prjs)//2)
        testing_prjs = list(set(prjs) - set(training_prjs))
        training_prjs_dir = os.path.join(training_dir, class_i, PROJECTS_DIR)
        testing_prjs_dir = os.path.join(testing_dir, class_i, PROJECTS_DIR)
        remove_projects(training_prjs_dir, training_prjs)
        remove_projects(testing_prjs_dir, testing_prjs)
