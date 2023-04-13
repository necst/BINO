import pickle
import os.path
from operator import itemgetter


STATS_FILE = "stats.pickle"


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
            

def load_stats_obj():
    global prj_path

    stats_path = os.path.join(prj_path, STATS_FILE)
    if os.path.exists(stats_path) and os.path.isfile(stats_path):
        with open(stats_path, 'rb') as f:
            stats = pickle.load(f)
    else:
        stats = Statistics()
    return stats


if __name__=="__main__":
    global prj_path

    stats_list = []
    prj_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(prj_path)
    # Loading pickle or initializing empty obj
    stats = load_stats_obj()
    for library in stats.libraries:
        if library.counter > 100:
            stats_list.append([library.library_name, library.counter])

    stats_list = sorted(stats_list, key = itemgetter(1))
    for tuple_i in stats_list:
        print("%s: %s" % (tuple_i[0], tuple_i[1]))
    
    # print(stats)