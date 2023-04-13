from os.path import isdir, join, abspath, isfile, exists
from os import listdir, mkdir
import os
import json
from shutil import rmtree
import sys
from utils.building_procedure import BuildingProcedure
from parsing.classes.cpp_parser import CppParser
from parsing.enums.operator_type import OperatorType
import logging
from clang.cindex import AccessSpecifier
from configurations.utils.helper import get_cpp_version


def _load_default_template():
    file_path = abspath(__file__)
    uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
    template_file_path = join(uppath(file_path, 2), "data", "templates", "main_template.cpp")
    f = open(template_file_path, "r")
    building_template = f.read()
    f.close()
    return building_template

def _build_methods_summary(class_definition,
                            method_list,
                            summary_logger,
                            access_specifier):
    class_name_ns = class_definition.get_name(templates=False)
    class_name_ts = class_definition.get_name(namespace=False)
    class_name_long = class_definition.get_name()
    method_list = []
    for method in class_definition.get_methods_definitions(access_specifier):
        if method.is_function_template():
            continue
        method_dict = {}
        # Method name
        summary_logger.debug("          - Method name: " + method.name)
        method_dict["method_name"] = method.name
        # Method return type
        return_type = method.get_return_type()
        r_type = str(return_type)
        if class_name_ts in r_type:
            r_type = r_type.replace(class_name_ts, class_name_long) 
        if class_name_ns + "::" in r_type:
            r_type = r_type.replace(class_name_ns + "::", class_name_long + "::")
        method_dict["return_type"] = r_type
        summary_logger.debug("          - Method return type: " + r_type)
        # Method const qualifier
        summary_logger.debug("          - Method const qualified: " + str(method.is_const_qualified()))
        method_dict["const_qualified"] = method.is_const_qualified()
        method_dict["operator_type"] = str(method.operator)
        # Method parameters
        parameters_types = method.get_parameters_types()
        summary_logger.debug("          - Method parameters:")
        parameters_list = []
        next_method = False
        for parameter_type in parameters_types:
            p_type = str(parameter_type)
            if class_name_ts in p_type:
                p_type = p_type.replace(class_name_ts, class_name_long) 
            if class_name_ns + "::" in p_type:
                p_type = p_type.replace(class_name_ns + "::", class_name_long + "::")
            # Check for Rvalues, they must be put inside std::move
            summary_logger.debug("             - " + p_type)
            parameters_list.append(p_type)
        summary_logger.debug("")
        method_dict["parameters"] = parameters_list
        # Appending to the parameters list
        method_list.append(method_dict)
    return method_list


def summary_builder(building_procedures_file_path, summaries_destination_path):
    summary_logger = logging.getLogger('summary_builder')
    # Checks
    if not isfile(building_procedures_file_path):
        raise Exception(building_procedures_file_path + " is not a file path")
    if not isdir(summaries_destination_path):
        raise Exception(summaries_destination_path + " is not a directory path")
    # Retriving all the building procedures
    bp = BuildingProcedure(building_procedures_file_path)
    summary_logger.info("[INFO] Working on building procedure " + building_procedures_file_path)
    # Loading cpp version from configuration file
    cpp_version = get_cpp_version()
    # Working on the building procedeure
    cpp_obj = CppParser(bp.source_path, std=cpp_version)
    # Retrieving class definition
    if "class_name" not in bp.json_dict.keys():
        raise Exception("No class specified!")
    class_name = bp.json_dict["class_name"]
    class_definition = cpp_obj.get_class_definition(class_name)
    class_namespace = class_definition.get_namespace()
    # Retrieving class json
    class_summary = bp.json_dict
    class_summary["namespace"] = class_namespace
    templates_names = class_definition.get_templates(optional=True)
    if len(templates_names) != len(class_summary["template_values"]):
        raise Exception("Different number of templates between class and building procedure.")
    for i in range(len(templates_names)):
        class_summary["template_values"][i]["name"] = templates_names[i] 
    summary_logger.debug("[DEBUG] Class: " + class_name)
    summary_logger.debug("[DEBUG] Public methods: ")
    # Public methods
    if "public" in class_summary.keys():
        public_method_list = class_summary["public"]
    else:
        public_method_list = []
    public_method_list += _build_methods_summary(class_definition,
                           public_method_list,
                           summary_logger,
                           AccessSpecifier.PUBLIC)
    class_summary["public"] = public_method_list
    class_summary["cpp_version"] = cpp_version
    # Exporting JSON
    dest_path = join(summaries_destination_path, class_name + ".json")
    f = open(dest_path, "w")
    f.write(json.dumps(class_summary, indent=2))
    f.close()