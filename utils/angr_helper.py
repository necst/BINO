from utils.name_mangling import is_cold_symbol

#### CONSTANT ####

_JUMPS = ["jmp", "bnd jmp"]


#### PRIVATE FUNCTIONS ####


def _get_constant_ijk(jump_dict):
    jump_dict_tmp = jump_dict.copy()
    while True:
        removed = False
        for key, value in jump_dict_tmp.items():
            if (value != "Ijk_Boring" and 
                value != "Ijk_Call"):
                del jump_dict_tmp[key]
                removed = True
                break
        if not removed:
            break
    return jump_dict_tmp


def _get_constant_exit_statements(exit_stmts):
    exit_stmts_tmp = list(exit_stmts)
    while True:
        removed = False
        i = 0
        for _, _, statement in exit_stmts_tmp:
            if ("Ijk_Boring" not in str(statement) and
                "Ijk_Call" not in str(statement)):
                exit_stmts_tmp.pop(i)
                removed = True
                break
            i += 1
        if not removed:
            break 
    return exit_stmts_tmp


#### PUBLIC FUNCTIONS ####


def print_block_instructions(angr_block):
    for ins in angr_block.capstone.insns:
        print(ins)

def get_main_function_cfg(angr_project):
    # Retrieve the main angr function

    if hasattr(angr_project.loader.main_object, 'symbols'):
        # If it is not stripped
        main_symbol = angr_project.loader.find_symbol('main')
        main_address = main_symbol.rebased_addr
    else:
        # If it is not stripped
        raise Exception("TODO: unstripped version")

    cfg = angr_project.analyses.CFGFast(normalize=True)
    return cfg.kb.functions[main_address], cfg


def get_function_by_address(cfg, address):
    # Retrieve the function cfg by its address
    return cfg.kb.functions[address]

def get_function_by_name(angr_project, cfg, name):
    # Retrieve the function cfg by its name
    if hasattr(angr_project.loader.main_object, 'symbols'):
        # If it is not stripped
        symbol_name = ""
        for symbol in angr_project.loader.symbols:
            if name in symbol.name:
                if is_cold_symbol(symbol.name):
                    continue
                symbol_name = symbol.name
                break
        function_symbol = angr_project.loader.find_symbol(symbol_name)
        main_address = function_symbol.rebased_addr
    else:
        # If it is not stripped
        raise Exception('Symbol "' + name + '" doesn not exist.')

    return cfg.kb.functions[main_address]

def get_function_initial_block(angr_function):
    # Retrieve the initial block of an angr function

    return next(angr_function.blocks)



def get_jump_blocks(angr_block, angr_function):
    # Retrieve the blocks in which a block will jump

    landing_blocks = []
    constant_jump_targets = []
    constant_jump_targets_dict = angr_block.vex.constant_jump_targets_and_jumpkinds
    for jump_key in constant_jump_targets_dict.keys():
        if constant_jump_targets_dict[jump_key] == "Ijk_Call":
            return_address = angr_function.get_call_return(angr_block.addr)
            constant_jump_targets.append(return_address)
        else:
            constant_jump_targets.append(jump_key)
    for block in angr_function.blocks:
        if block.addr in constant_jump_targets:
            landing_blocks.append(block)
    return landing_blocks



def get_block_from_to(angr_function, angr_initial_block, angr_final_blocks,
                      include_ini_fins=True):
    returning_blocks = []
    to_be_visited = []
    if angr_initial_block in angr_final_blocks:
        if include_ini_fins:
            return [angr_initial_block]
        else:
            return []
    to_be_visited = [angr_initial_block]
    while len(to_be_visited) != 0:
        current_block = to_be_visited[0]
        if not current_block in returning_blocks:
            returning_blocks.append(current_block)
        if not current_block in angr_final_blocks:
            for next_block in get_jump_blocks(current_block, angr_function):
                if not next_block in returning_blocks:
                    to_be_visited.append(next_block)
        to_be_visited.remove(current_block)
    if include_ini_fins == False:
        returning_blocks.remove(angr_initial_block)
        for to_be_removed in angr_final_blocks:
            returning_blocks.remove(to_be_removed)
    return returning_blocks 


def get_block_function_call_offset(angr_function, angr_block):
    if angr_block not in angr_function.blocks:
        raise Exception("Block not in function.")
    # Special call sites.
    jumpout_sites = []
    for jumpout_site in angr_function.jumpout_sites:
        jumpout_sites.append(jumpout_site.addr)
    call_sites = angr_function.get_call_sites()
    if (angr_block.addr in call_sites or 
        angr_block.addr in jumpout_sites):
        constant_jump_targets_dict = _get_constant_ijk(angr_block.vex.constant_jump_targets_and_jumpkinds)
        if len(constant_jump_targets_dict) == 1:
            call_ijk = list(constant_jump_targets_dict.values())[0]
            if call_ijk == "Ijk_Call":
                offset = list(constant_jump_targets_dict.keys())[0]
                return True, offset
            else:
                return False, 0
        else:
            if angr_block.vex.jumpkind == "Ijk_Sys_syscall":
                return True, -2
            else:
                return True, -1
    return False, 0


def get_jumps_addresses(angr_block):
    """
    Given a basic block, this function returns the addresses of the basic blocks reached by the given basic block.
    """
    # There might be SigSEGV, Syscall, etc
    constant_jump_targets_dict = _get_constant_ijk(angr_block.vex.constant_jump_targets_and_jumpkinds)
    n_jumps = len(constant_jump_targets_dict)
    if n_jumps == 0:
        # Might be a syscall
        if (angr_block.vex.jumpkind == "Ijk_Sys_syscall" or 
            angr_block.vex.jumpkind == "Ijk_Call"):
            addr = angr_block.addr + angr_block.size
            yield addr    
    elif n_jumps == 1:
        kind = list(constant_jump_targets_dict.values())[0]
        if kind == "Ijk_Call":
            addr = angr_block.addr + angr_block.size
        else:
            addr = list(constant_jump_targets_dict.keys())[0]
            # Checking whether there's an unconditional jump or not
            cap_insns = angr_block.capstone.insns
            last_ins = cap_insns[-1]
            if last_ins.mnemonic not in _JUMPS:
                if "jmp" in last_ins.mnemonic:
                    raise Exception("Hey you, check this jmp -> %s" % last_ins.mnemonic)
        yield addr
    elif n_jumps == 2:
        exit_statements = _get_constant_exit_statements(angr_block.vex.exit_statements)
        if len(exit_statements) != 1:
            # Can be an instruction like repne: two conditions can be true
            if len(exit_statements) == 2:
                for jump_key in constant_jump_targets_dict.keys():
                    yield jump_key
            else:
                raise Exception("Basic block with two branches but with %d exit statement(s)." % len(exit_statements))
        true_addr = int(str(exit_statements[0][2].dst), 16)
        check_bits = 0
        for jump_key in constant_jump_targets_dict.keys():
            if jump_key == true_addr:
                check_bits |= 1
            else:
                check_bits |= 2
            yield jump_key
        if check_bits != 3:
            raise Exception("Homogeneous branches in a 2-way branch.")
    elif n_jumps > 2:
        # Here things become tricky, there are instructions like lock that loops on theirself inside a $
        # First we identify block range
        start_addr = angr_block.addr
        end_addr = angr_block.addr + angr_block.size
        exit_statements = _get_constant_exit_statements(angr_block.vex.exit_statements)
        true_addr = -1
        for exit_stat in exit_statements:
            true_addr = int(str(exit_stat[2].dst), 16)
            if start_addr <= true_addr < end_addr:
                true_addr = -1
                continue
            break
        if true_addr == -1:
            raise Exception("Couldn't return proper edges for block:\n%s" % angr_block.pp())
        yield true_addr
        found = False
        for jump_key in constant_jump_targets_dict.keys():
            if jump_key == end_addr:
                found = True
                yield jump_key
        if not found:
            raise Exception("Couldn't return proper edges for block:\n%s" % angr_block.pp())



def function_has_return(angr_cfg, enriched_block):
    function = None
    if enriched_block.has_function_call() and not enriched_block.is_library_call():
        addr = enriched_block.function_call_address
        function = angr_cfg.kb.functions[addr]
    if function is not None:
        return function.has_return
    return False


def is_stripped(angr_project):
    if hasattr(angr_project.loader.main_object, 'symbols'):
        return False
    else:
        return True


def get_arch_name(arch_name):
    if arch_name == "AMD64":
        return "amd64"
    else:
        raise Exception("Not supported architecture.")


def get_angr_offset_name(val):
    s = "sub_" + hex(val)[2:]
    return s