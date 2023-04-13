class GlobalStatistics(object):

    def __init__(self):
        self.global_stats = []
        self.projects_count = 0
        self.size_amount = 0
        self.bino_analysis_time = 0
        self.angr_analysis_time = 0

    def __str__(self):
        s = "Projects count: %s\n" % str(self.projects_count)
        s += "Size amount: %d bytes\n" % self.size_amount
        s += "Angr analysis time: %d seconds\n" % self.angr_analysis_time
        s += "BINO analysis time: %d seconds\n" % self.bino_analysis_time
        for stats in self.global_stats:
            s += str(stats) + "\n\n" + ("%" * 60) + "\n\n"
        s = s[:-64]
        return s

    def merge_statistics(self, stats):
        for stats_obj in self.global_stats:
            if stats.optimization_level == stats_obj.optimization_level:
                stats_obj.merge_statistics(stats)
                return
        self.global_stats.append(stats)

