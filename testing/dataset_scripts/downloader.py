import os.path
import shutil
import subprocess

CANDIDATES = "candidates.csv"
INSPECTED = "inspected.csv"
DOWNLOADED = "downloaded.csv"
WORKDIR = "workdir"
DOWNLOAD_DIR = "downloaded"
INTERESTING_LIBRARIES = ["armadillo"]


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


def get_download_info():
    global prj_path

    inspected_path = os.path.join(prj_path, INSPECTED)
    downloaded_path = os.path.join(prj_path, DOWNLOADED)
    i = 0
    if not os.path.exists(inspected_path):
        f = open(inspected_path, "w")
        f.close()
        i += 1
    if not os.path.exists(downloaded_path):
        f = open(downloaded_path, "w")
        f.close()
        i += 1
    if i == 2:
        return [], []
    # Retrieving inspected
    inspected = []
    f = open(inspected_path)
    content = f.read()
    f.close()
    for line in content.split():
        if line:
            inspected.append(line)
    # Retrieving downloaded
    downloaded = []
    f = open(downloaded_path)
    content = f.read()
    f.close()
    for line in content.split():
        if line:
            downloaded.append(line)
    return inspected, downloaded


def create_new_dir(path):
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)


def create_new_dir_no_deletion(path):
    if not os.path.exists(path):
        os.mkdir(path)


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


def append_prj(file, project):
    global prj_path

    prj_path_tmp = os.path.join(prj_path, file)
    f = open(prj_path_tmp, "a")
    f.write(project + "\n")
    f.close()


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
    # Retrieving projects
    projects = get_projects()
    inspected, downloaded = get_download_info()
    # Check if directory exists, if not create it
    download_path = os.path.join(prj_path, DOWNLOAD_DIR)
    create_new_dir_no_deletion(download_path)
    for project in projects:
        # Check already done
        if project in inspected or project in downloaded:
            continue
        # Create new dir
        create_new_dir(workdir_path)
        os.chdir(workdir_path)
        # Cloning
        print("Analyzing: %s" % project)
        ret_val_1, ret_val_2 = clone_repo(project)
        if ret_val_1 == 8:
            append_prj(INSPECTED, project)
            continue
        elif ret_val_1 != 0:
            raise Exception("Error 1 %s!" % ret_val_1)
        if ret_val_2 != 0:
            raise Exception("Error 2 %s!" % ret_val_2)
        # Joining dir
        repo_name = os.listdir(".")[0]
        os.chdir(repo_name)
        # Parsing
        libraries = get_used_libraries()
        os.chdir(prj_path)
        found = False
        for lib in INTERESTING_LIBRARIES:
            if lib in libraries:
                # Keep prj
                src_path = os.path.join(prj_path, WORKDIR, repo_name)
                dst_path = os.path.join(prj_path, DOWNLOAD_DIR, project.split("https://github.com/")[1].replace("/", "___"))
                shutil.move(src_path, dst_path)
                append_prj(DOWNLOADED, project)
                found = True
                break
        if not found:
            append_prj(INSPECTED, project)