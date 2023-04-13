import os
import os.path
from classes.opt_results import OptResults


OPT_LEVEL = ["-O2", "-O3", "-Os", "-Ofast"]


class ProjectResults(object):


    def __init__(self, prj_path):
        self.opt_results = []
        for f_results in os.listdir(prj_path):
            for opt in OPT_LEVEL:
                if (".%s." % opt) in f_results:
                    if "dwarf.txt" in f_results:
                        tp_path = os.path.join(prj_path, f_results)
                        fp_path = os.path.join(prj_path, f_results.replace("dwarf.txt", "false.txt"))
                        info_path = os.path.join(prj_path, f_results.replace("dwarf.txt", "output.txt"))
                        self.opt_results.append(OptResults(opt, tp_path, fp_path, info_path))


    def get_stats(self, m=None, s=None, method_names=None, opts=None, known=None):
        n = 0
        tp = 0
        fp = 0
        for opt_res in self.opt_results:
            n += opt_res.get_N(m, method_names, opts, known)
            tp += opt_res.get_TP(m, s, method_names, opts, known)
            fp += opt_res.get_FP(m, s, method_names, opts)
        return n, tp, fp


    def get_stats_by_M(self, m=5):
        n = 0
        tp = 0
        fp = 0
        for opt_res in self.opt_results:
            n += opt_res.get_N_by_M(m)
            tp += opt_res.get_TP_by_M(m)
            fp += opt_res.get_FP_by_M(m)
        return n, tp, fp


    def get_stats_by_M_and_S(self, m=5, s=0.75):
        n = 0
        tp = 0
        fp = 0
        for opt_res in self.opt_results:
            n += opt_res.get_N_by_M(m)
            tp += opt_res.get_TP_by_M_and_S(m, s)
            fp += opt_res.get_FP_by_M_and_S(m, s)
        return n, tp, fp


    def filter_methods(self, keep=[]):
        for opt_res in self.opt_results:
            opt_res.filter_methods(keep=keep)


    def get_avg_function_time(self):
        n = 0
        tot_exec = 0
        for opt_res in self.opt_results:
            n_part, tot_exec_part = opt_res.get_avg_function_time()
            n += n_part
            tot_exec += tot_exec_part
        return n, tot_exec