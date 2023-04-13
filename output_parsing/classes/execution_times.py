from classes.function_execution_time import FunctionExecutionTime
from classes.binary_execution_times import BinaryExecutionTime

class ExecutionTimes(object):


    def __init__(self, f_path):
        # Reading content
        f = open(f_path)
        content = f.read()
        f.close()
        # Parsing file
        self.execution_times = []
        repo_name = content.split("Repository URL:\t")[1].split("\n")[0]
        for binary_file in content.split("Binary: "):
            if "Angr analysis time:" not in binary_file:
                continue
            angr_time = float(binary_file.split("Angr analysis time: ")[1].split("\n")[0])
            bino_time = float(binary_file.split("BINO analysis time: ")[1].split("\n")[0])
            binary_name = binary_file.split("\n")[0]
            functions_times = []
            for line in binary_file.split("Functions analysis time:\n")[1].split("\n"):
                if line and "  - Function" in line:
                    if len(line.split(": ")) > 2:
                        raise Exception("Strange line: %s" % line)
                    time_and_bb = line.split(": ")[1]
                    time = float(time_and_bb.split("(")[0])
                    bb = int(time_and_bb.split("(")[1].split(" BB)")[0])
                    functions_times.append(FunctionExecutionTime(time, bb))
            self.execution_times.append(BinaryExecutionTime(repo_name, binary_name, bino_time, angr_time, functions_times))


    def get_avg_function_time(self):
        n = 0
        tot_exec = 0
        for exec_time in self.execution_times:
            n_part, tot_exec_part = exec_time.get_avg_function_time()
            n += n_part
            tot_exec += tot_exec_part
        return n, tot_exec