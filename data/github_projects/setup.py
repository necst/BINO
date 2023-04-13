#!/usr/bin/python3

import argparse
import logging
import sys
from os.path import dirname, abspath, isdir, isfile
from os import chdir, listdir
from subprocess import call


IGNORE = ["setup.py", "classes_candidates", "candidates.csv", "valid_projects.csv", "invalid_projects.csv"]

def clean():
    cmd = ["rm", "-rf", "global_cache"]
    call(cmd)
    cmd = ["rm", "candidates.csv"]
    call(cmd)


def setup():
    for file in listdir("."):
        if file in IGNORE:
            continue
        if ".7z" in file and isfile(file):
            cmd = ["7z", "x", file, "-oprojects"]
            call(cmd)
            cmd = ["mv", "projects/projects", "global_cache"]
            call(cmd)
            cmd = ["rm", file]
            call(cmd)
            cmd = ["rm", "-rf", "projects"]
            call(cmd)
        if ".csv" in file and isfile(file):
            cmd = ["mv", file, "candidates.csv"]
            call(cmd)


if __name__ == '__main__':
    """
    The goal of this script is to decompress the 7z of projects and
    prepare the environment
    """

    # Projecj path
    prj_path = dirname(abspath(__file__))
    chdir(prj_path)
    # Parsing arguments
    parser = argparse.ArgumentParser(description="Environment setup.")
    parser.add_argument("-c",
                    "--clean",
                    dest="clean",
                    action="store_true",
                    help="Clean the directory.")
    args = parser.parse_args()
    # Arguments actions
    if args.clean:
        clean()
    else:
        setup()