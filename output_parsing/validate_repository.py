import argparse
import os.path
import os


PROJECTS_DIR = os.path.join("github_projects", "projects")
OPTS = []
OPTS += ["-O2"]
# OPTS += ["-O3"]
# OPTS += ["-Os"]
# OPTS += ["-Ofast"]


def dir_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(path + " is not a valid directory path.")
    return path


if __name__=="__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Script to test M.")
    # Required argument
    parser.add_argument(dest="test_dir",
                        type=dir_path,
                        help="Directory that contains the experiments' results.")  
    args = parser.parse_args()
    # Iterating over classes under test
    test_dir = args.test_dir
    for class_i in os.listdir(test_dir):
        prjs_i_path = os.path.join(test_dir, class_i, PROJECTS_DIR)
        # Directory prjs_directory must exists
        if not os.path.exists(prjs_i_path) or not os.path.isdir(prjs_i_path):
            raise Exception("Directory must contains a directory for each class under test and inside of them the \"github_projects\" directory.")
        completed = []
        not_completed = []
        for prj in os.listdir(prjs_i_path):
            prj_path = os.path.join(prjs_i_path, prj)
            for file_i in os.listdir(prj_path):
                found = False
                file_path = os.path.join(prj_path, file_i)
                for opt in OPTS:
                    if (".%s.output.txt" % opt) in file_path:
                        found = True
                        break
                if found:
                    break
            prj_path = "https://api.github.com/repos/%s" % (prj.replace("___", "/"))
            if found:
                completed.append(prj_path)
            else:
                not_completed.append(prj_path)
        print("Class: %s" % class_i)
        print("Completed:")
        print("\n".join(completed))
        print("Not completed:")
        print("\n".join(not_completed))