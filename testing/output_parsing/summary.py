from os import listdir
from os.path import join
import copy

VOLUMES_PATH = "../volumes"
# TESTING_OUTPUT = "data/github_projects/git_testing_output.csv"
TESTING_OUTPUT = "git_testing_output.csv"

def get_test_info(s):
    dict_info = {}
    for line in s.split("\n"):
        if line and line[0] == "_":
            values = line.split("\t")
            func_name = values[1]
            found = values[2]
            recognized = values[3]
            if func_name in dict_info.keys():
                counters = dict_info[func_name]
                counters[0] += int(found)
                counters[1] += int(recognized)
            else:
                dict_info[func_name] = [int(found), int(recognized)]
    return dict_info


def print_all(known, unknown):
    final = copy.deepcopy(known)
    for key in unknown.keys():
        counters = unknown[key]
        if key in final.keys():
            final[key][0] += counters[0]
            final[key][1] += counters[1]
        else:
            final[key] = counters
    print("Overall:")
    print("Function name\tFound\tRecognized")
    for key in final.keys():
        print(key + "\t" + str(final[key][0]) + "\t" + str(final[key][1]))
    print("")
    print("Known fingerprints:")
    print("Function name\tFound\tRecognized")
    for key in known.keys():
        print(key + "\t" + str(known[key][0]) + "\t" + str(known[key][1]))
    print("")
    print("Unknown fingerprints:")
    print("Function name\tFound\tRecognized")
    for key in unknown.keys():
        print(key + "\t" + str(unknown[key][0]) + "\t" + str(unknown[key][1]))
    print("")
    print("")


if __name__ == '__main__':
    for directory in listdir(VOLUMES_PATH):
        file_path = join(VOLUMES_PATH, directory, TESTING_OUTPUT)
        directory = directory.replace("_", "::")
        print("Class: " + directory + "\n")
        f = open(file_path)
        content = f.read()
        f.close()
        for c_level in content.split("%" * 60):
            opt_level = c_level.split("Optimization level:\t")[1].split("\n")[0]
            c_split = c_level.split("Unknown functions:\n")
            c_known = c_split[0]
            c_unknown = c_split[1]
            dic_known = get_test_info(c_known)
            dic_unknown = get_test_info(c_unknown)
            print("Optimization level: " + opt_level + "\n")
            print_all(dic_known, dic_unknown)