from classes.tp_results import TPResults
from classes.fp_results import FPResults
from classes.execution_times import ExecutionTimes


class OptResults(object):


    def __init__(self, opt, tp_path, fp_path, info_path):
        self.opt = opt
        self.tp_results = TPResults(tp_path, info_path)
        self.fp_results = FPResults(fp_path)
        self.execution_times = ExecutionTimes(fp_path)


    def get_N(self, m=None, method_names=None, opts=None, known=None):
        if opts != None and type(opts) != list:
            raise Exception("Error for parameter options; expected a list!")
        if self.opt in opts:
            return self.tp_results.get_N(m, method_names, known)
        return 0


    def get_TP(self, m=None, s=None, method_names=None, opts=None, known=None):
        if opts != None and type(opts) != list:
            raise Exception("Error for parameter options; expected a list!")
        if self.opt in opts:
            return self.tp_results.get_TP(m, s, method_names, known)
        return 0


    def get_FP(self, m=None, s=None, method_names=None, opts=None):
        if opts != None and type(opts) != list:
            raise Exception("Error for parameter options; expected a list!")
        if self.opt in opts:
            return self.fp_results.get_FP(m, s, method_names) 
        return 0       


    def get_N_by_M(self, m=5):
        return self.tp_results.get_N_by_M(m)


    def get_TP_by_M(self, m=5):
        return self.tp_results.get_TP_by_M(m)


    def get_FP_by_M(self, m=5):
        return self.fp_results.get_FP_by_M(m)

    
    def get_N_by_M_and_S(self, m=5, s=0.75):
        return self.tp_results.get_N_by_M_and_S(m, s)


    def get_TP_by_M_and_S(self, m=5, s=0.75):
        return self.tp_results.get_TP_by_M_and_S(m, s)


    def get_FP_by_M_and_S(self, m=5, s=0.75):
        return self.fp_results.get_FP_by_M_and_S(m, s)


    def filter_methods(self, keep=[]):
        self.tp_results.filter_methods(keep=keep)
        return self.fp_results.filter_methods(keep=keep)
    

    def get_avg_function_time(self):
        return self.execution_times.get_avg_function_time()
