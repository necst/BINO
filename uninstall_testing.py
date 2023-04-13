#!/usr/bin/python3

from os.path import isfile, exists, isdir, join, dirname, abspath
from os import remove, listdir, mkdir
from shutil import rmtree, copyfile

if __name__ == '__main__':
    """
    Uninstaller for the testing environment
    """

    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Paths
    images_path = join(prj_path, "docker", "images")
    templates_path = join(prj_path, "docker", "templates")
    scripts_path = join(prj_path, "docker", "scripts")
    # Removing docker-compose
    if exists("docker-compose.yml") and isfile("docker-compose.yml"):
        remove("docker-compose.yml")
    # Deleting images directory
    if exists(images_path) and isdir(images_path):
        rmtree(images_path)