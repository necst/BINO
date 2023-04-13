from os import listdir
from os.path import join

VOLUMES_PATH = "../volumes"
PROJECTS_PATH = "data/github_projects/projects"
METHODS = ["std::vector::push_back",
"std::vector::resize",
"std::vector::emplace_back",
"std::vector::clear",
"std::map::operator[]",
"std::map::upper_bound",
"std::map::lower_bound"]

fps_blocks = {}

if __name__ == '__main__':
    for directory in listdir(VOLUMES_PATH):
        projects_dir = join(VOLUMES_PATH, directory, PROJECTS_PATH)
        directory = directory.replace("_", "::")
        for prj in listdir(projects_dir):
            prj_dir = join(projects_dir, prj)
            for file in listdir(prj_dir):
                if ".false.txt" not in file:
                    continue
                file_path = join(prj_dir, file)
                f = open(file_path)
                content = f.read()
                f.close()
                if "Blocks: " in content:
                    fps = content.split("Blocks: ")
                    for fp in fps:
                        if fp[0] != "{":
                            continue
                        functions = []
                        for line in fp.split("\n"):
                            if " - Function name: " not in line:
                                continue
                            func_name = line.split(" - Function name: ")[1].split("\n")[0]
                            if func_name in METHODS:         
                                if func_name not in functions:
                                    functions.append(func_name)
                        if not functions:
                            continue
                        blocks = fp.split("{")[1].split("}")[0]
                        n_blocks = len(blocks.split(","))
                        if n_blocks in fps_blocks.keys():
                            fps_blocks[n_blocks][0] += 1
                            fps_blocks[n_blocks][1] = list(set(fps_blocks[n_blocks][1]).union(set(functions)))
                        else:
                            fps_blocks[n_blocks] = [1, functions.copy()]
    print(fps_blocks)