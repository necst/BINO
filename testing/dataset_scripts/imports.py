import subprocess
import os.path
import os
import shutil
import pickle


CANDIDATES = "candidates.csv"
STATS_FILE = "stats.pickle"
WORKDIR = "workdir"

class LibraryStatistics(object):


    def __init__(self, library_name):
        self.library_name = library_name
        self.counter = 1


    def __str__(self):
        s = "%s: \t%d" % (self.library_name, self.counter)
        return s


    def increase(self):
         self.counter += 1


class Statistics(object):


    def __init__(self):
        self.libraries = []
        self.seen_projects = []
        self.invalid_projects = []


    def __str__(self):
        s = "Libraries:\n"
        for library_obj in self.libraries:
            s += str(library_obj) + "\n"
        s = s[:-1]
        return s


    def order(self):
        pass


    def append_stats(self, libraries):
        to_append = []
        for library_name in libraries:
            found = False
            for library_obj in self.libraries:
                if library_name == library_obj.library_name:
                    found = True
                    library_obj.increase()
                    break
            if not found:
                to_append.append(library_name)
        for library_name in to_append:
            self.libraries.append(LibraryStatistics(library_name))


    def already_seen(self, project):
        if project in self.seen_projects:
            return True
        return False


    def already_invalid(self, project):
        if project in self.invalid_projects:
            return True
        return False


    def add_seen(self, project):
        if not self.already_seen(project):
            self.seen_projects.append(project)


    def add_invalid(self, projects):
        if not self.already_invalid(project):
            self.invalid_projects.append(project)
        

def get_projects():
    # Reading the file
    f = open(CANDIDATES)
    content = f.read()
    f.close()
    # Parsing projects for url
    projects = []
    for line in content.split('\n'):
        if "api.github" in line:
            url = line.split('"')[1].split('"')[0]
            url = url.replace("api.", "")
            url = url.replace("repos/", "")
            projects.append(url)
    return projects


def clear_directory(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path,file)):
            os.remove(os.path.join(path,file))
        else:
            shutil.rmtree(os.path.join(path,file))


def clone_repo(repo_url):
    cmd = ["wget", repo_url]
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return_code = out.wait()
    if return_code != 0:
        return return_code, 0
    clear_directory(".")
    cmd = ["git", "clone", repo_url]
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return_code = out.wait()
    return 0, return_code


def create_new_dir(path):
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)


def load_stats_obj():
    global prj_path

    stats_path = os.path.join(prj_path, STATS_FILE)
    if os.path.exists(stats_path) and os.path.isfile(stats_path):
        with open(stats_path, 'rb') as f:
            stats = pickle.load(f)
    else:
        stats = Statistics()
    return stats


def store_stats_obj(stats_obj):
    global prj_path

    stats_path = os.path.join(prj_path, STATS_FILE)
    with open(stats_path, 'wb') as f:
        pickle.dump(stats_obj, f)



def get_used_libraries():
    cmd = ["grep", "-R", "#include", "."]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    output = output.decode()
    libraries = []
    for line in output.split("\n"):
        if "#include" not in line:
            continue
        line = line.split("#include")[1]
        if '\"' in line:
            library_name = line.split('"')[1]
        elif '<' in line and '>' in line:
            library_name = line.split('<')[1].split('>')[0]
        else:
            print("Strange line: %s" % line)
            continue
        libraries.append(library_name)
    libraries = list(set(libraries))
    return libraries


if __name__ == "__main__":
    global prj_path

    prj_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(prj_path)
    workdir_path = os.path.join(prj_path, WORKDIR)
    # Retrieving project
    projects = get_projects()
    # Loading pickle or initializing empty obj
    stats = load_stats_obj()
    for project in projects:
        # Check already done
        if stats.already_seen(project):
            continue
        print("Analyzing: %s" % project)
        # Create new dir
        create_new_dir(workdir_path)
        os.chdir(workdir_path)
        # Cloning
        ret_val_1, ret_val_2 = clone_repo(project)
        if ret_val_1 == 8:
            stats.add_invalid(project)
            continue
        elif ret_val_1 != 0:
            raise Exception("Error 1 %s!" % ret_val_1)
        if ret_val_2 != 0:
            raise Exception("Error 2 %s!" % ret_val_2)
        # Joining dir
        os.chdir(os.listdir(".")[0])
        # Parsing
        libraries = get_used_libraries()
        # Appending results
        stats.append_stats(libraries)
        stats.add_seen(project)
        # Saving pickle
        store_stats_obj(stats)
        # Going back in dir
        os.chdir(prj_path)
