from elftools.elf.elffile import ELFFile
from os.path import join

class Dwarf(object):
    """ 
    Class for parsing DWARF Debugging Information
    """

    def __init__(self, binary_path):
        self.binary_path = binary_path
        self.cached_tags = []
        with open(binary_path, 'rb') as f:
            elffile = ELFFile(f)
            self.dwarf_info = elffile.get_dwarf_info()
        self.subprogram_dies = []
        self.inlined_subroutine_dies = []
        self.final_inlined_subroutine_dies = []

    def _cache_subprograms_tags(self):
        # Caching 'DW_TAG_subprogram' die
        if not self.subprogram_dies:
            # Retrieving all the inlined functions
            for cu in self.dwarf_info.iter_CUs():
                for die in cu.iter_DIEs():
                    # An function is tagged as 'DW_TAG_subprogram'
                    if die.tag == 'DW_TAG_subprogram':
                        self.subprogram_dies.append(die)


    def _cache_inlined_subroutine_tags(self):
        # Caching 'DW_TAG_inlined_subroutine' die
        if not self.inlined_subroutine_dies:
            # Retrieving all the inlined functions
            for cu in self.dwarf_info.iter_CUs():
                for die in cu.iter_DIEs():
                    # An inlined function is tagged as 'DW_TAG_inlined_subroutine'
                    if die.tag == 'DW_TAG_inlined_subroutine':
                        self.inlined_subroutine_dies.append(die)


    def _cache_final_inlined_subroutine_tags(self):
        self._cache_inlined_subroutine_tags()
        if not self.final_inlined_subroutine_dies:
            for die in self.inlined_subroutine_dies:
                final_die = Dwarf.get_final_inlined_die(die)
                if final_die and final_die not in self.final_inlined_subroutine_dies:
                    self.final_inlined_subroutine_dies.append(final_die)


    def get_subprograms_die_by_addr(self, address):
        self._cache_subprograms_tags()
        for die in self.subprogram_dies:
            ranges = Dwarf.get_die_ranges(die)
            if ranges:
                for range_i in ranges:
                    low_addr = range_i[0]
                    high_addr = range_i[1]
                    if low_addr <= address < high_addr:
                        yield die


    def get_subprograms_mangled_name_by_addr(self, address):
        self._cache_subprograms_tags()
        for die in self.get_subprograms_die_by_addr(address):
            if "DW_AT_abstract_origin" in die.attributes.keys():
                abstract_origin_die = self.get_die_at_offset(die.attributes["DW_AT_abstract_origin"].value, die.cu.cu_offset)
            else:
                continue
            if "DW_AT_specification" in abstract_origin_die.attributes.keys():
                specification_die = self.get_die_at_offset(abstract_origin_die.attributes["DW_AT_specification"].value, abstract_origin_die.cu.cu_offset)
            else:
                continue
            if "DW_AT_linkage_name" in specification_die.attributes.keys():
                mangled_name = specification_die.attributes["DW_AT_linkage_name"].value
                yield mangled_name.decode()


    def get_inlined_subroutines_die_by_addr(self, address):
        self._cache_inlined_subroutine_tags()
        for die in self.inlined_subroutine_dies:
            ranges = Dwarf.get_die_ranges(die)
            for range_i in ranges:
                low_addr = range_i[0]
                high_addr = range_i[1]
                if low_addr <= address < high_addr:
                    yield die


    def get_inlined_subroutines_mangled_name_by_addr(self, address):
        self._cache_inlined_subroutine_tags()
        for die in self.get_inlined_subroutines_die_by_addr(address):
            if "DW_AT_abstract_origin" in die.attributes.keys():
                abstract_origin_die = self.get_die_at_offset(die.attributes["DW_AT_abstract_origin"].value, die.cu.cu_offset)
            else:
                continue
            if "DW_AT_specification" in abstract_origin_die.attributes.keys():
                specification_die = self.get_die_at_offset(abstract_origin_die.attributes["DW_AT_specification"].value, abstract_origin_die.cu.cu_offset)
            else:
                continue
            if "DW_AT_linkage_name" in specification_die.attributes.keys():
                mangled_name = specification_die.attributes["DW_AT_linkage_name"].value
                yield mangled_name.decode()


    def get_final_inlined_subroutine_die_by_addr(self, address):
        self._cache_final_inlined_subroutine_tags()
        for die in self.final_inlined_subroutine_dies:
            ranges = Dwarf.get_die_ranges(die)
            for range_i in ranges:
                low_addr = range_i[0]
                high_addr = range_i[1]
                if low_addr <= address < high_addr:
                    return Dwarf.get_final_inlined_die(die)               
        return None


    def get_final_inlined_subroutine_file_line_by_addr(self, address):
        die = self.get_final_inlined_subroutine_die_by_addr(address)
        if die:
            return Dwarf.get_inlined_die_file_line(die)


    def get_final_inlined_subroutines_file_line(self, exclude_library=True):
        self._cache_final_inlined_subroutine_tags()
        for die in self.final_inlined_subroutine_dies:
            # Retriving line of the source code
            line = die.attributes["DW_AT_call_line"].value
            # Retriving file of the source code
            file_index = die.attributes["DW_AT_call_file"].value
            lp = die.dwarfinfo.line_program_for_CU(die.cu)
            lp_header = lp.header
            files = lp_header["file_entry"]
            includes = lp_header["include_directory"]
            file_info = files[file_index - 1]
            filename = file_info.name.decode("utf-8")
            if exclude_library:
                if file_info.dir_index != 0:
                    continue
            if (file_info.dir_index == 0):
                # File path of the source code
                file_path = join(".", filename)
            else:
                # File path of the library
                file_dir = includes[file_info.dir_index - 1].decode("utf-8")
                file_path = join(file_dir, filename)            
            yield file_path, line


    def get_die_at_offset(self, offset, cu_offset=0):
        return self.dwarf_info.get_DIE_from_refaddr(offset + cu_offset)


    def get_final_inlined_subroutines_mangled_name(self, exclude_library=True):
        self._cache_final_inlined_subroutine_tags()
        for die in self.final_inlined_subroutine_dies:
            # Retriving line of the source code
            line = die.attributes["DW_AT_call_line"].value
            # Retriving file of the source code
            file_index = die.attributes["DW_AT_call_file"].value
            lp = die.dwarfinfo.line_program_for_CU(die.cu)
            lp_header = lp.header
            files = lp_header["file_entry"]
            file_info = files[file_index - 1]
            if exclude_library:
                if file_info.dir_index != 0:
                    continue
            if "DW_AT_abstract_origin" in die.attributes.keys():
                abstract_origin_die = self.get_die_at_offset(die.attributes["DW_AT_abstract_origin"].value, die.cu.cu_offset)
            else:
                continue
            if "DW_AT_specification" in abstract_origin_die.attributes.keys():
                specification_die = self.get_die_at_offset(abstract_origin_die.attributes["DW_AT_specification"].value, abstract_origin_die.cu.cu_offset)
            else:
                continue
            if "DW_AT_linkage_name" in specification_die.attributes.keys():
                mangled_name = specification_die.attributes["DW_AT_linkage_name"].value
                yield mangled_name.decode()
            else:
                continue


    def get_inlined_subroutines_info(self):
        self._cache_inlined_subroutine_tags()
        for die in self.inlined_subroutine_dies:
            # Retriving file of the source code
            if "DW_AT_abstract_origin" in die.attributes.keys():
                abstract_origin_die = self.get_die_at_offset(die.attributes["DW_AT_abstract_origin"].value, die.cu.cu_offset)
            else:
                continue
            if "DW_AT_specification" in abstract_origin_die.attributes.keys():
                specification_die = self.get_die_at_offset(abstract_origin_die.attributes["DW_AT_specification"].value, abstract_origin_die.cu.cu_offset)
            else:
                continue
            if "DW_AT_linkage_name" in specification_die.attributes.keys():
                mangled_name = specification_die.attributes["DW_AT_linkage_name"].value
                yield mangled_name.decode(), Dwarf.get_die_ranges(die)
            else:
                continue


    def get_final_inlined_subroutines_info(self, exclude_library=True):
        self._cache_final_inlined_subroutine_tags()
        for die in self.final_inlined_subroutine_dies:
            # Retriving line of the source code
            line = die.attributes["DW_AT_call_line"].value
            # Retriving file of the source code
            file_index = die.attributes["DW_AT_call_file"].value
            lp = die.dwarfinfo.line_program_for_CU(die.cu)
            lp_header = lp.header
            files = lp_header["file_entry"]
            includes = lp_header["include_directory"]
            file_info = files[file_index - 1]
            filename = file_info.name.decode()
            if exclude_library:
                if file_info.dir_index != 0:
                    continue
            if "DW_AT_abstract_origin" in die.attributes.keys():
                abstract_origin_die = self.get_die_at_offset(die.attributes["DW_AT_abstract_origin"].value, die.cu.cu_offset)
            else:
                raise Exception("No abstract origin for the die!")
            if "DW_AT_specification" in abstract_origin_die.attributes.keys():
                specification_die = self.get_die_at_offset(abstract_origin_die.attributes["DW_AT_specification"].value, abstract_origin_die.cu.cu_offset)
            else:
                continue
            if "DW_AT_linkage_name" in specification_die.attributes.keys():
                mangled_name = specification_die.attributes["DW_AT_linkage_name"].value
                yield mangled_name.decode(), Dwarf.get_die_ranges(die)
            else:
                continue


    def get_file_index_by_addr(self, address):
        # Go over all the line programs in the DWARF information, looking for
        # one that describes the given address.
        for CU in self.dwarf_info.iter_CUs():
            # First, look at line programs to find the file/line for the address
            lineprog = self.dwarf_info.line_program_for_CU(CU)
            prevstate = None
            for entry in lineprog.get_entries():
                # We're interested in those entries where a new state is assigned
                if entry.state is None:
                    continue
                if entry.state.end_sequence:
                    # if the line number sequence ends, clear prevstate.
                    prevstate = None
                    continue
                # Looking for a range of addresses in two consecutive states that
                # contain the required address.
                if prevstate and prevstate.address <= address < entry.state.address:
                    file_index = lineprog['file_entry'][prevstate.file - 1]["dir_index"]
                    return file_index
                prevstate = entry.state
        raise Exception("Not a valid address!")


    ##### Static Methods #####


    @staticmethod
    def get_final_inlined_die(die):
        parent = die.get_parent()
        if parent.tag == 'DW_TAG_inlined_subroutine':
            return Dwarf.get_final_inlined_die(parent)
        elif parent.tag == 'DW_TAG_lexical_block':
            # Moving towards parents until we find subprogram or another inlined subroutin
            while parent.tag == 'DW_TAG_lexical_block':
                parent = parent.get_parent()
                if parent.tag == "DW_TAG_lexical_block":
                    # Very good
                    continue
                elif parent.tag == 'DW_TAG_subprogram':
                    return die
                elif parent.tag == 'DW_TAG_inlined_subroutine':
                    return Dwarf.get_final_inlined_die(parent)
                else:
                    raise Exception("Unexpected tag: " + parent.tag)
        elif parent.tag == 'DW_TAG_subprogram':
            return die
        else:
            raise Exception("Unexpected tag: " + parent.tag)


    @staticmethod
    def get_die_ranges(die):
        # It can have contiguos memory addresses, so a low_pc and an high_pc
        if "DW_AT_low_pc" in die.attributes.keys():
            low_addr = die.attributes["DW_AT_low_pc"].value
            high_addr = die.attributes["DW_AT_high_pc"].value
            if die.attributes["DW_AT_high_pc"].form == "DW_FORM_data8":
                high_addr += low_addr
            return [[low_addr, high_addr]]
        # or ranges
        elif "DW_AT_ranges" in die.attributes.keys():
            range_value = die.attributes["DW_AT_ranges"].value
            ranges = die.dwarfinfo.range_lists().get_range_list_at_offset(range_value)
            addresses = []
            for range_i in ranges:
                low_addr = range_i.begin_offset
                high_addr = range_i.end_offset
                addresses.append([low_addr, high_addr])
            return addresses
        return None



    @staticmethod
    def get_inlined_die_file_line(die):
        # Retriving line of the source code
        line = die.attributes["DW_AT_call_line"].value
        # Retriving file of the source code
        file_index = die.attributes["DW_AT_call_file"].value
        lp = die.dwarfinfo.line_program_for_CU(die.cu)
        lp_header = lp.header
        files = lp_header["file_entry"]
        includes = lp_header["include_directory"]
        file_info = files[file_index - 1]
        filename = file_info.name.decode("utf-8")
        # If the file has 'dir_index' equal to 0 it means that it is in the same directory of the compilation directory
        if (file_info.dir_index == 0):
            # File path of the source code
            file_path = join(".", filename)
        else:
            # File path of the library
            file_dir = includes[file_info.dir_index - 1].decode("utf-8")
            file_path = join(file_dir, filename)
        return file_path, line


if __name__=="__main__":
    dobject = Dwarf("/home/law/Downloads/qualiaa___cnns/cnet")
    for mangled_name, ranges in dobject.get_inlined_subroutines_info():
        print(mangled_name)
        print(ranges)
    #print(list(dobject.get_inlined_subroutines_mangled_name_by_addr(0x1A7CD)))