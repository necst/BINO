from os import listdir
from os.path import join
import subprocess

def demangle(name):
    cmd = ['c++filt', name]
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    demangled = (pipe.stdout.readline()).decode("ascii")
    demangled = demangled.split("\n")[0]
    return demangled



VOLUMES_PATH = "../volumes"
OUTPUT_PATH = "data/github_projects/git_testing_output.csv"
METHODS = ["std::vector::push_back",
"std::vector::resize",
"std::vector::emplace_back",
"std::vector::clear",
"std::map::operator[]",
"std::map::upper_bound",
"std::map::lower_bound"]



if __name__ == '__main__':
    f = open("unrecognized_stat.csv", "w")
    for directory in listdir(VOLUMES_PATH):
        projects_dir = join(VOLUMES_PATH, directory, OUTPUT_PATH)
        directory = directory.replace("_", "::")
        f.write("Class: " + directory + "\n")
        f_tmp = open(projects_dir)
        content = f_tmp.read()
        f_tmp.close()
        for block in content.split("Unknown functions:"):
            if "Known functions:" in block:
                block = block.split("Known functions:")[0]
            for line in block.split("\n"):
                if not line:
                    continue
                if line[0] != "_":
                    continue
                values = line.split("\t")
                if directory + "::" + values[1] not in METHODS:
                    continue
                mangled = values[0]
                found = int(values[2])
                recognized = int(values[3])
                demangled = demangle(mangled)
                f.write(demangled + "\t" + str(found - recognized)+ "\t" + str(recognized) + "\n")
        f.write("\n\n")
