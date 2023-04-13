from json import dumps
from math import isclose

class ResultsManager(object):

    def __init__(self, binary_path):
        self.matches = []
        self.binary_path = binary_path
        self.angr_analysis_time = 0
        self.bino_analysis_time = 0
        self.functions_statistics = []


    def __str__(self):
        s = "Binary: %s\n" % self.binary_path
        s += "Angr analysis time: %s\n" % self.angr_analysis_time
        s += "BINO analysis time: %s\n" % self.bino_analysis_time
        s += "Functions analysis time:\n"
        for stat in self.functions_statistics:
            s += "  - %s: %f(%d BB)\n" % (stat[0], stat[1], stat[2])
        s += "Matches:\n"
        for match in self.matches:
            s += match.pp() + "\n"
        s = s[:-1]
        return s


    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=2)


    def add_match(self, match):
        # Once a match is added the first thing to be checked is whether another match shares the same location
        # If one intermediate node is shared and the functions recognized are the same, one of the two match must be removed.
        # The strategy to remove a match is as follow:
        # 1) Number of nodes: the match with the larger number of nodes is kept.
        # 2) Similarity: if the number of nodes is the same, the function with the larger similarity is kept.
        for match_i in self.matches:
            if not match_i.same_function(match):
                continue
            if match_i.is_submatch(match) or match.is_submatch(match_i):
                # Checking similarity
                if isclose(match.similarity, match_i.similarity):
                    if match.get_nodes_count() > match_i.get_nodes_count():
                        self.matches.remove(match_i)
                        self.matches.append(match)
                elif match.similarity > match_i.similarity:
                    self.matches.remove(match_i)
                    self.matches.append(match)
                return
        # Finally append
        self.matches.append(match)


    def add_statistics(self, stats):
        self.functions_statistics = stats


    def get_matches(self, path_name=None, function_name=None):
        for match in self.matches:
            if path_name is not None and match.path_name != path_name:
                continue
            if function_name is not None and match.function_name != function_name:
                continue
            yield match


    def remove_match(self, match):
        if match not in self.matches:
            raise Exception("Match is not in matches!")
        self.matches.remove(match)