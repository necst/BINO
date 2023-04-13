from copy import deepcopy
from sys import path_hooks
from testing.class_statistics import ClassStatistics
from utils.name_mangling import demangle
from copy import deepcopy

def _check_instructions_mangled_name(addresses_list, match, dwarf):
    for addr in addresses_list:
        for mangled in dwarf.get_inlined_subroutines_mangled_name_by_addr(addr):
            path_name, function_name = demangle(mangled)
            if path_name == match.path_name and function_name == match.function_name:
                return True
        return False
    return False  


def _check_instructions(addresses_list, ranges):
    for addr in addresses_list:
        for range_i in ranges:
            low = range_i[0]
            high = range_i[1]
            if low <= addr < high:
                return True
    return False


def _check_correctness_partial(match, dwarf, inline_info):
    # Check same name
    if match.path_name != inline_info.class_name or match.function_name != inline_info.function_name:
        return False 
    matched_count = 0
    inline_count = 0
    ranges = inline_info.ranges
    found_blocks = list(match.get_blocks_instructions_addresses(finals=False, initial=True))
    invalid_block = False
    for addresses_list in found_blocks:
        if not _check_instructions(addresses_list, ranges):
            if not _check_instructions_mangled_name(addresses_list, match, dwarf):
                invalid_block = True
            else:
                matched_count += 1
        else:
            inline_count += 1
            matched_count += 1
    if invalid_block:
        if match.get_nodes_count() * 0.8 >= matched_count:
            return 0
    return inline_count


def _check_correctness(match, inline_info):
    # Check same name
    if match.path_name != inline_info.class_name or match.function_name != inline_info.function_name:
        return False
    # Check match correctness
    ranges = inline_info.ranges
    found_blocks = list(match.get_blocks_instructions_addresses(finals=False, initial=True))
    if not found_blocks:
        return False
    for addresses_list in found_blocks:
        if not _check_instructions(addresses_list, ranges):
            return False
    return True


def _is_false_positive(dwarf, match):
    # Checking if the match is a false positive or not
    class_name = match.path_name
    # Case 1: the function is from the same class
    # Case 2: the match is code from the same class
    found_blocks = list(match.get_blocks_instructions_addresses(finals=False, initial=False))
    found_blocks_addrs = []
    for addresses_list in found_blocks:
        found_blocks_addrs += list(addresses_list)    
    for addr in found_blocks_addrs:
        # if dwarf.get_file_index_by_addr(addr) != 0: TODO:CHeck it
            # Need to check that the inlined instructions come from a library of the same class
        for mang in dwarf.get_subprograms_mangled_name_by_addr(addr):
            class_name_real, _ = demangle(mang)
            if class_name_real == class_name:
                return False
        for mang in dwarf.get_inlined_subroutines_mangled_name_by_addr(addr):
            class_name_real, _ = demangle(mang)
            if class_name_real == class_name:
                return False
    return True


class Statistics(object):

    def __init__(self, query_db, optimization_level):
        self.query_db = query_db
        self.optimization_level = optimization_level
        self.classes = []


    def __str__(self):
        s = "Optimization level:\t" + str(self.optimization_level) + "\n\n"
        i = 0
        for class_obj in self.classes:
            s += str(class_obj) + "\n" + ("x" * 60) + "\n\n"
            i +=1
        if i != 0:
            s = s[:-63]
        return s


    def _add_false_positives(self, result_manager, dwarf):
        # Removing false false positives
        # TODO: can be done better but triggers errors
        for match in list(result_manager.get_matches()):
            if not _is_false_positive(dwarf, match):
                result_manager.remove_match(match)
        # Now adding the false positives
        for match in result_manager.get_matches():
            added_classes = []
            class_name = match.path_name
            for class_obj in self.classes:
                if (class_obj.class_name == class_name and 
                    class_name not in added_classes):
                    class_obj.false_positives += 1
                    added_classes.append(class_name)
                    break


    def _add_to_class(self, mangled_name, class_name, function_name):
        for class_obj in self.classes:
            if class_obj.class_name == class_name:
                class_obj.add_function(mangled_name, function_name)
                return
        new_class = ClassStatistics(self.query_db, class_name)
        new_class.add_function(mangled_name, function_name)
        self.classes.append(new_class)


    def _add_found(self, mangled_name, class_name):
        for class_obj in self.classes:
            if class_obj.class_name == class_name:
                class_obj.add_found(mangled_name)


    def add_function(self, mangled_name, class_name, function_name):
        if self.query_db.has_function(class_name, function_name):
            self._add_to_class(mangled_name, class_name, function_name)
            return True
        return False


    def add_results(self, result_manager, call_info, binary, dwarf):
        found_str = ""
        matches = []
        for inline_info in call_info.get_inline_info(binary_path=binary):
            for match in result_manager.get_matches(inline_info.class_name, inline_info.function_name):
                if _check_correctness(match, inline_info):
                    self._add_found(inline_info.mangled_name, inline_info.class_name)
                    matches.append(match)
                    result_manager.remove_match(match)
                    inline_info.found = True
                    inline_info.match = deepcopy(match)
                    break
        # At this point some match could have a common part and the dwarf tells us only the remaining part of a function
        # E.g., 2 functions X' and X'' have an intersection. The dwarf describres X' completely and X'' partially. The part that is missing 
        # is the part in common with X'
        for inline_info in call_info.get_inline_info(binary_path=binary, ordering=True):
            if inline_info.found:
                continue
            best_blocks_count = 0
            best_match = None
            for match in result_manager.get_matches(inline_info.class_name, inline_info.function_name):
                m_blocks_count = _check_correctness_partial(match, dwarf, inline_info)
                if m_blocks_count > 0:
                    if m_blocks_count > best_blocks_count:
                        best_blocks_count = m_blocks_count
                        best_match = match
            if best_match is not None:
                self._add_found(inline_info.mangled_name, inline_info.class_name)
                matches.append(best_match)
                result_manager.remove_match(best_match)
                inline_info.found = True
                inline_info.match = deepcopy(best_match)
                break            
        # Preparing output
        for match in matches: 
            found_str += str(match) + "\n\n"
        # Finally false positives
        self._add_false_positives(result_manager, dwarf)
        return found_str


    def merge_statistics(self, stats):
        new_classes = []
        for class_obj_1 in stats.classes:
            found = False
            for class_obj_2 in self.classes:
                if class_obj_1.class_name == class_obj_2.class_name:
                    class_obj_2.merge_statistics(class_obj_1)
                    found = True
                    break
            if not found:
                new_classes.append(class_obj_1)
        if new_classes:
            self.classes += new_classes