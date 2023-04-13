import json
from os.path import join, exists, abspath, dirname, split, isdir
from os import mkdir
from shutil import rmtree

class BuildingProcedure(object):

    def __init__(self, json_path):
        self.json_path = json_path
        self._get_json_dict()
        # Creating working directory
        self._create_workdir()
        # Creating file to parse
        self.source_path = join(self.workdir, "source.cpp")
        f = open(self.source_path, "w")
        if "standard_include" in self.json_dict.keys():
            f.write("#include <" + self.json_dict["standard_include"] + ">")
        else:
            f.write('#include "' + self.json_dict["absolute_include"] + '"')
        f.close()   


    def __del__(self):
        self._delete_workdir()


    def _delete_workdir(self):
        rmtree(self.workdir)


    def _create_workdir(self):
        file_path = dirname(abspath(__file__))
        parent_path = split(file_path)[0]
        self.workdir = join(parent_path, "data", "working_dir", "tmp_source_dir")
        if not (exists(self.workdir) and isdir(self.workdir)):
            mkdir(self.workdir)


    def _get_json_dict(self):
        # Creating JSON dictionary
        f = open(self.json_path, "r")
        json_content = f.read()
        f.close()
        self.json_dict = json.loads(json_content)
        if (not "standard_include" in self.json_dict.keys() and 
                not "absolute_include" in self.json_dict.keys()):
            raise Exception("Json file " 
                    + self.json_path 
                    + " without absolute or standard include.")