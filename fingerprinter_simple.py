#!/usr/bin/python3

import angr
import sys
from utils.angr_helper import get_function_by_name
from fingerprint.classes.fingerprint import Fingerprint
from fingerprint.utils.helper import plot_fingerprint
from fingerprint.delimiters.helper import get_delimiters 

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception("No binary specified!")
    project = angr.Project(sys.argv[1], load_options={'auto_load_libs': False})
    cfg = project.analyses.CFGFast(normalize=True)
    func_cfg = get_function_by_name(project, cfg, "wrapper")
    fp = Fingerprint(func_cfg, cfg)
    print(str(fp))
    plot_fingerprint(fp)
    # Retrieving the initial and final delimiters
    init, fini = get_delimiters(project.arch.name)
    fp.reduce_between(init, fini)
    print(str(fp))
    plot_fingerprint(fp)
    print("Is empty? %s" % str(fp.is_empty()))
    print("Reducing the fingeprint...")
    optimized_fp = fp.get_optimized_fingerprint()
    print(str(optimized_fp))
    plot_fingerprint(optimized_fp)