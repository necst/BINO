class BinaryExecutionTime(object):


    def __init__(self, repo_name, binary_name, bino_time, angr_time, functions_times):
        self.repo_name = repo_name
        self.binary_name = binary_name
        self.bino_time = bino_time
        self.angr_time = angr_time
        self.functions_times = functions_times


    def get_bino_time(self):
        return self.bino_time
    

    def get_avg_function_time(self):
        tot_exec = 0
        for func_time in self.functions_times:
            tot_exec += func_time.time
        return len(self.functions_times), tot_exec