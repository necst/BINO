from os.path import split, exists
from pickle import load, dump
from testing.global_statistics import GlobalStatistics

class OutputManager(object):

    def __init__(self, file_path):
        name = split(file_path)[1]
        if "." in name:
            raise Exception("File extension specified!")
        self.path_obj = file_path + ".p"
        self.path_file = file_path + ".csv"
        if not exists(self.path_obj):
            self.output = GlobalStatistics()
        else:
            f = open(self.path_obj, "rb")
            self.output = load(f)
            f.close()


    def __str__(self):
        s = str(self.output)
        return s


    def merge_statistics(self, stats):
        self.output.merge_statistics(stats)


    def update_files(self):
        f = open(self.path_obj, "wb")
        dump(self.output, f)
        f.close()
        f = open(self.path_file, "w")
        f.write(str(self))
        f.close()


    def increase_project_number(self):
        self.output.projects_count += 1


    def update_size(self, new_binary_size):
        self.output.size_amount += new_binary_size


    def update_bino_analysis_time(self, new_bino_analysis_time):
        self.output.bino_analysis_time += new_bino_analysis_time


    def update_angr_analysis_time(self, new_angr_analysis_time):
        self.output.angr_analysis_time += new_angr_analysis_time