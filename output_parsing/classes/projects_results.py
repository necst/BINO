from classes.project_results import ProjectResults
import os.path

class ProjectsResults(object):


    def __init__(self, prjs_path):
        self.prjs_results = []
        for prj in os.listdir(prjs_path):
            self.prjs_results.append(ProjectResults(os.path.join(prjs_path, prj)))


    def get_stats_by_M(self, M=5):
        n = 0
        tp = 0
        fp = 0
        for prj in self.prjs_results:
            n_i, tp_i, fp_i = prj.get_stats_by_M(M)
            n += n_i
            tp += tp_i
            fp += fp_i
        return n, tp, fp


    def get_stats_by_M_and_S(self, m=5, s=0.75):
        n = 0
        tp = 0
        fp = 0
        for prj in self.prjs_results:
            n_i, tp_i, fp_i = prj.get_stats_by_M_and_S(m, s)
            n += n_i
            tp += tp_i
            fp += fp_i
        return n, tp, fp


    def get_stats(self, m=None, s=None, method_names=None, opts=None, known=None):
        n = 0
        tp = 0
        fp = 0
        for prj in self.prjs_results:
            n_i, tp_i, fp_i = prj.get_stats(m, s, method_names, opts, known)
            n += n_i
            tp += tp_i
            fp += fp_i
        return n, tp, fp 


    def filter_methods(self, keep=[]):
        for prj in self.prjs_results:
            prj.filter_methods(keep=keep)


    def merge(self, other):
        self.prjs_results += other.prjs_results


    def get_avg_function_time(self):
        n = 0
        exec_tot = 0
        for prj in self.prjs_results:
            n_part, exec_tot_part = prj.get_avg_function_time()
            n += n_part
            exec_tot += exec_tot_part
        return exec_tot / n, n, exec_tot