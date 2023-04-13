from utils.asm import asm
from capstone import Cs
# Architecture related imports
# amd64
from fingerprint.delimiters.x64_delimiters import INITIAL_DELIMITERS as INITIAL_DELIMITERS_x64
from fingerprint.delimiters.x64_delimiters import FINAL_DELIMITERS as FINAL_DELIMITERS_x64
from capstone import CS_ARCH_X86, CS_MODE_64

delimiters = {}

#### PRIVATE FUNCTIONS ####


def _get_capstone_delimiters(arch="AMD64"):
    if arch == "AMD64":
        md = Cs(CS_ARCH_X86, CS_MODE_64)
        sc_init = asm(INITIAL_DELIMITERS_x64, "amd64")
        sc_fini = asm(FINAL_DELIMITERS_x64, "amd64")
        return sc_init, sc_fini
    else:
        raise Exception("Not supported architecture.")


#### PUBLIC FUNCTIONS ####


def get_delimiters(arch="AMD64"):
    global delimiters

    if arch == "AMD64":
        key = "initial_delimeters_x64"
    else:
        raise Exception("Not supported architecture.")
    # If such key doesn't exist add it
    if key not in delimiters.keys():
        delimiters["initial_delimeters_x64"], delimiters["final_delimeters_x64"] = _get_capstone_delimiters(arch)
    return delimiters["initial_delimeters_x64"], delimiters["final_delimeters_x64"]