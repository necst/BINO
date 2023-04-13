from os import listdir
from os.path import join

VOLUMES_PATH = "../volumes"
PROJECTS_PATH = "data/github_projects/projects"

projects = []

if __name__ == '__main__':
    for directory in listdir(VOLUMES_PATH):
        projects_dir = join(VOLUMES_PATH, directory, PROJECTS_PATH)
        new_prjs =  listdir(projects_dir)
        projects = list(set(new_prjs).union(set(projects)))

print(len(projects))