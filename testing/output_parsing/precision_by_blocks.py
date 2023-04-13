from os import listdir, chdir
from os.path import dirname, abspath, join, isdir, exists, isfile
import ast

METHODS = {
# "std::vector::push_back" : 0.78
"std::vector::clear" : 0.82
# "std::vector::resize" : 0.89,
# "std::vector::erase" : 0.88,
# "std::vector::reserve" : 0.76,
# "std::map::operator[]" : 0.82,
# "std::map::lower_bound" : 0.89,
# "std::map::upper_bound" : 0.88,
# "std::map::find" : 0.84,
# "std::deque::pop_front" : 0.95,
# "std::deque::push_back" : 0.89,
# "std::deque::operator[]" : 0.95
}

def get_bb_stats(file_path):
    f = open(file_path)
    cont = f.read()
    f.close()
    new_dict = {}
    if not cont:
        return new_dict
    if "Function recognized: " not in cont:
        return new_dict
    for match in cont.split("Function recognized: ")[1:]:
        func_name = match.split("\n")[0]
        similarity = float(match.split("Similarity: ")[1].split("\n")[0])
        blocks = match.count(" - ")
        if func_name in METHODS.keys():
            if similarity >= METHODS[func_name]:
                if blocks in new_dict.keys():
                    new_dict[blocks] += 1
                else:
                    new_dict[blocks] = 1
    return new_dict


def get_case_stats(class_case_path, class_case, class_name):
    git_path = join(class_case_path, "data", "github_projects")
    prjs_path = join(git_path, "projects")
    recognized = {}
    false = {}
    for prj in listdir(prjs_path):
        prj_path = join(prjs_path, prj)
        for file in listdir(prj_path):
            file_path = join(prj_path, file)
            if "recognized.txt" in file:
                new_recognized = get_bb_stats(file_path)
                recognized = {k: new_recognized.get(k, 0) + recognized.get(k, 0) for k in set(new_recognized) | set(recognized)}
            if "false.txt" in file:
                new_false = get_bb_stats(file_path)
                false = {k: false.get(k, 0) + new_false.get(k, 0) for k in set(new_false) | set(false)}
    return recognized, false



def get_class_all_stats(class_name):
    recognized = {}
    false = {}
    for class_case in listdir(class_name):
        class_case_path = join(class_name, class_case)
        new_recognized, new_false = get_case_stats(class_case_path, class_case, class_name)
        recognized = {k: new_recognized.get(k, 0) + recognized.get(k, 0) for k in set(new_recognized) | set(recognized)}
        false = {k: false.get(k, 0) + new_false.get(k, 0) for k in set(new_false) | set(false)}
    return recognized, false


if __name__ == '__main__':
    # Projecj path
    prj_path = dirname(abspath(__file__))
    # Changing to wd
    chdir(prj_path)
    recognized = {}
    false = {}
    for class_name in listdir("."):
        if isdir(class_name):
            new_recognized, new_false = get_class_all_stats(class_name)
            recognized = {k: new_recognized.get(k, 0) + recognized.get(k, 0) for k in set(new_recognized) | set(recognized)}
            false = {k: false.get(k, 0) + new_false.get(k, 0) for k in set(new_false) | set(false)}

    print("Recognized:")
    print(recognized)
    print("False:")
    print(false)
