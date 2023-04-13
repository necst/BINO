from os import listdir
from os.path import join

VOLUMES_PATH = "../volumes"
PROJECTS_PATH = "data/github_projects/projects"

if __name__ == '__main__':
    for directory in listdir(VOLUMES_PATH):
        projects_dir = join(VOLUMES_PATH, directory, PROJECTS_PATH)
        directory = directory.replace("_", "::")
        print("Class: " + directory)
        print("Projects: " + str(len(listdir(projects_dir))))