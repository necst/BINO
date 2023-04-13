from os import listdir
from os.path import join

VOLUMES_PATH = "../volumes"
PROJECTS_PATH = "data/github_projects/projects"
OPTS = ["-O2", "-O3", "-Os"]
METHODS_VECTOR = ["std::vector::push_back",
"std::vector::resize",
"std::vector::emplace_back",
"std::vector::clear"]

METHODS_MAP = ["std::map::operator[]",
"std::map::upper_bound",
"std::map::lower_bound"]

if __name__ == '__main__':
    projects_dir = join(VOLUMES_PATH, "std_vector", PROJECTS_PATH)
    print("Class: std::vector")
    print("Optimization: -O2")
    false_O2_vector = 0
    false_detail_O2_vector = {}
    for prj in listdir(projects_dir):
        prj_dir = join(projects_dir, prj)
        for file in listdir(prj_dir):
            if "-O2.false.txt" not in file:
                continue
            false_path = join(prj_dir, file)
            f = open(false_path)
            cont = f.read()
            f.close()            
            if "Blocks:" in cont: 
                for false in cont.split("Blocks:"):
                    curr_found = []
                    for line in false.split("\n"):
                        if " - Function name: " not in line:
                            continue
                        func_name = line.split(" - Function name: ")[1].split("\n")[0]
                        if func_name in METHODS_VECTOR and func_name not in curr_found:
                            curr_found.append(func_name)
                    if curr_found:
                        false_O2_vector += 1
                        for method_name in curr_found:
                            if method_name in false_detail_O2_vector.keys():
                                false_detail_O2_vector[method_name] += 1
                            else:
                                false_detail_O2_vector[method_name] = 1
    print("False positives: " + str(false_O2_vector))
    print(false_detail_O2_vector)

    print("Optimization: -O3")
    false_O3_vector = 0
    false_detail_O3_vector = {}
    for prj in listdir(projects_dir):
        prj_dir = join(projects_dir, prj)
        for file in listdir(prj_dir):
            if "-O3.false.txt" not in file:
                continue
            false_path = join(prj_dir, file)
            f = open(false_path)
            cont = f.read()
            f.close()            
            if "Blocks:" in cont: 
                for false in cont.split("Blocks:"):
                    curr_found = []
                    for line in false.split("\n"):
                        if " - Function name: " not in line:
                            continue
                        func_name = line.split(" - Function name: ")[1].split("\n")[0]
                        if func_name in METHODS_VECTOR and func_name not in curr_found:
                            curr_found.append(func_name)
                    if curr_found:
                        false_O3_vector += 1
                        for method_name in curr_found:
                            if method_name in false_detail_O3_vector.keys():
                                false_detail_O3_vector[method_name] += 1
                            else:
                                false_detail_O3_vector[method_name] = 1
    print("False positives: " + str(false_O3_vector))
    print(false_detail_O3_vector)

    print("Optimization: -Os")
    false_Os_vector = 0
    false_detail_Os_vector = {}
    for prj in listdir(projects_dir):
        prj_dir = join(projects_dir, prj)
        for file in listdir(prj_dir):
            if "-Os.false.txt" not in file:
                continue
            false_path = join(prj_dir, file)
            f = open(false_path)
            cont = f.read()
            f.close()            
            if "Blocks:" in cont: 
                for false in cont.split("Blocks:"):
                    curr_found = []
                    for line in false.split("\n"):
                        if " - Function name: " not in line:
                            continue
                        func_name = line.split(" - Function name: ")[1].split("\n")[0]
                        if func_name in METHODS_VECTOR and func_name not in curr_found:
                            curr_found.append(func_name)
                    if curr_found:
                        false_Os_vector += 1
                        for method_name in curr_found:
                            if method_name in false_detail_Os_vector.keys():
                                false_detail_Os_vector[method_name] += 1
                            else:
                                false_detail_Os_vector[method_name] = 1
    print("False positives: " + str(false_Os_vector))
    print(false_detail_Os_vector)

    print()
    print()
    print()
    print()

    projects_dir = join(VOLUMES_PATH, "std_map", PROJECTS_PATH)
    print("Class: std::map")
    print("Optimization: -O2")
    false_O2_map = 0
    false_detail_O2_map = {}
    for prj in listdir(projects_dir):
        prj_dir = join(projects_dir, prj)
        for file in listdir(prj_dir):
            if "-O2.false.txt" not in file:
                continue
            false_path = join(prj_dir, file)
            f = open(false_path)
            cont = f.read()
            f.close()            
            if "Blocks:" in cont: 
                for false in cont.split("Blocks:"):
                    curr_found = []
                    for line in false.split("\n"):
                        if " - Function name: " not in line:
                            continue
                        func_name = line.split(" - Function name: ")[1].split("\n")[0]
                        if func_name in METHODS_MAP and func_name not in curr_found:
                            curr_found.append(func_name)
                    if curr_found:
                        false_O2_map += 1
                        for method_name in curr_found:
                            if method_name in false_detail_O2_map.keys():
                                false_detail_O2_map[method_name] += 1
                            else:
                                false_detail_O2_map[method_name] = 1
    print("False positives: " + str(false_O2_map))
    print(false_detail_O2_map)

    print("Optimization: -O3")
    false_O3_map = 0
    false_detail_O3_map = {}
    for prj in listdir(projects_dir):
        prj_dir = join(projects_dir, prj)
        for file in listdir(prj_dir):
            if "-O3.false.txt" not in file:
                continue
            false_path = join(prj_dir, file)
            f = open(false_path)
            cont = f.read()
            f.close()            
            if "Blocks:" in cont: 
                for false in cont.split("Blocks:"):
                    curr_found = []
                    for line in false.split("\n"):
                        if " - Function name: " not in line:
                            continue
                        func_name = line.split(" - Function name: ")[1].split("\n")[0]
                        if func_name in METHODS_MAP and func_name not in curr_found:
                            curr_found.append(func_name)
                    if curr_found:
                        false_O3_map += 1
                        for method_name in curr_found:
                            if method_name in false_detail_O3_map.keys():
                                false_detail_O3_map[method_name] += 1
                            else:
                                false_detail_O3_map[method_name] = 1
    print("False positives: " + str(false_O3_map))
    print(false_detail_O3_map)

    print("Optimization: -Os")
    false_Os_map = 0
    false_detail_Os_map = {}
    for prj in listdir(projects_dir):
        prj_dir = join(projects_dir, prj)
        for file in listdir(prj_dir):
            if "-Os.false.txt" not in file:
                continue
            false_path = join(prj_dir, file)
            f = open(false_path)
            cont = f.read()
            f.close()            
            if "Blocks:" in cont: 
                for false in cont.split("Blocks:"):
                    curr_found = []
                    for line in false.split("\n"):
                        if " - Function name: " not in line:
                            continue
                        func_name = line.split(" - Function name: ")[1].split("\n")[0]
                        if func_name in METHODS_MAP and func_name not in curr_found:
                            curr_found.append(func_name)
                    if curr_found:
                        false_Os_map += 1
                        for method_name in curr_found:
                            if method_name in false_detail_Os_map.keys():
                                false_detail_Os_map[method_name] += 1
                            else:
                                false_detail_Os_map[method_name] = 1
    print("False positives: " + str(false_Os_map))
    print(false_detail_Os_map)  