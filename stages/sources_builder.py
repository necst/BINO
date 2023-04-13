from os.path import isdir, join, abspath, isfile, exists
from os import listdir, mkdir
import os
import json
from shutil import rmtree
import sys

from numpy import False_
from utils.building_procedure import BuildingProcedure
from parsing.enums.operator_type import OperatorType
import logging
from clang.cindex import AccessSpecifier

def is_proper_substring(substring, string):
    if substring + " " in string:
        return True
    if substring + "," in string:
        return True
    if substring + ">" in string:
        return True
    if substring + ")" in string:
        return True
    if string.endswith(" " + substring):
        return True
    return False

def _load_default_templates():
    file_path = abspath(__file__)
    uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
    for template in listdir(join(uppath(file_path, 2), "data", "templates")):
        template_file_path = join(uppath(file_path, 2), "data", "templates", template)
        f = open(template_file_path, "r")
        building_template = f.read()
        f.close()
        yield building_template

def _create_class_definition_string(class_summary):
    s = class_summary["class_name"] + "<"
    for template in class_summary["template_values"]:
        s += template["name"] + ", "
    s = s[:-2] + ">"
    return s

def _create_class_token_string(class_summary, long=True):
    if not long and "::" in class_summary["class_name"]:
        s = class_summary["class_name"].split("::")[-1] + "<"
    else:
        s = class_summary["class_name"] + "<"
    for template in class_summary["template_values"]:
        if template["type"] == "string":
            s += template["value"] + ", "
    s = s[:-2] + ">"
    return s


def _build_methods_sources(class_name_long,
                           class_name_simple,
                           class_name_token_long,
                           class_name_token_short,
                           building_template_original,
                           method_list,
                           template_list,
                           path,
                           class_path_name,
                           tokens,
                           compiler_options):
    for method in method_list:
        building_template = building_template_original
        # Return type
        r_type = method["return_type"]
        if class_name_long in r_type:
            r_type = r_type.replace(class_name_long, class_name_token_long)
        elif "::" + class_name_simple + "::" in r_type:
            r_type = r_type.replace("::" + class_name_simple + "::", "::" + class_name_token_short + "::")
        for template in template_list:
            if is_proper_substring(template["name"], r_type):
                r_type = r_type.replace(template["name"], template["value"])
        # Parameters list
        index = 1
        list_parameters_call = ""
        list_parameters_function = "" 
        for parameter in method["parameters"]:
            p_type = parameter
            if class_name_long in p_type:
                p_type = p_type.replace(class_name_long, class_name_token_long)
            elif "::" + class_name_simple + "::" in p_type:
                p_type = p_type.replace("::" + class_name_simple + "::", "::" + class_name_token_short + "::")
            for template in template_list:
                if is_proper_substring(template["name"], p_type):
                    p_type = p_type.replace(template["name"], template["value"])
            # Adding parameter to list of the call
            if "&&" in p_type:
                list_parameters_call += "static_cast<" + p_type + ">(p_" + str(index) + "), "
            else:
                list_parameters_call += "p_" + str(index) + ", " 
            list_parameters_function += p_type + " p_" + str(index) + ", " 
            index += 1
        list_parameters_call = list_parameters_call[:-2]
        list_parameters_function = list_parameters_function[:-2]
        # Function call considering return type if const qualified
        return_value_utilization = ""
        variable_str = ""
        if OperatorType(method["operator_type"]) == OperatorType.NONE:
            # Standard parenthesis call
            if r_type != "void":
                return_value_utilization = 'printf("%d\\n", ret_value)'
                function_call_str = r_type + " ret_value = object_variable." + method["method_name"] + "(" + list_parameters_call + ")"
            else:
                function_call_str = "object_variable." + method["method_name"] + "(" + list_parameters_call + ")"
            # Check for const values
            if method["const_qualified"]:
                class_name_token_2 = "const " + class_name_token_long
            else:
                class_name_token_2 = class_name_token_long
            # Finalizing
            if list_parameters_function:
                function_def_str = class_name_token_2 + " object_variable, " + list_parameters_function
            else:
                function_def_str = class_name_token_2 + " object_variable"        
        elif OperatorType(method["operator_type"]) == OperatorType.EQ:
            # Equal assignment
            function_def_str = list_parameters_function
            function_call_str = "const " + r_type + " ret_value = " + list_parameters_call
            if "const " in list_parameters_function:
                variable_str = class_name_token_long + " ret_value"
                function_call_str = "ret_value = " + list_parameters_call
        elif OperatorType(method["operator_type"]) == OperatorType.EQ_EQ:
            # Equal Equal comparator
            # Return value is bool for sure
            function_call_str = "bool ret_value = object_variable == " + list_parameters_call
            function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
            # Return value must be used otherwise optimization can lead
            # to no operations
            return_value_utilization = 'printf("%d\\n", ret_value);'
        elif OperatorType(method["operator_type"]) == OperatorType.SQUARE_BRACKETS:
            # [] operator
            if method["const_qualified"]:
                return_value_utilization = 'printf("%d\\n", ret_value);'
                function_call_str = r_type + " ret_value = object_variable[" + list_parameters_call + "]"
            else:
                function_call_str = "object_variable[" + list_parameters_call + "]"
            function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
        elif OperatorType(method["operator_type"]) == OperatorType.PLUS_EQ:
            # +=
            if len(method["parameters"]) != 1:
                raise Exception("Method \"operator+=\" has more than one parameter.")
            if method["const_qualified"]:
                raise Exception("Method \"operator+=\" is const qualified.")
            function_call_str = "object_variable += " + list_parameters_call
            function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
        elif OperatorType(method["operator_type"]) == OperatorType.MINUS_EQ:
            # -=
            if len(method["parameters"]) != 1:
                raise Exception("Method \"operator-=\" has more than one parameter.")
            if method["const_qualified"]:
                raise Exception("Method \"operator-=\" is const qualified.")
            function_call_str = "object_variable -= " + list_parameters_call
            function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
        elif OperatorType(method["operator_type"]) == OperatorType.MUL_EQ:
            # *=
            if len(method["parameters"]) != 1:
                raise Exception("Method \"operator*=\" has more than one parameter.")
            if method["const_qualified"]:
                raise Exception("Method \"operator*=\" is const qualified.")
            function_call_str = "object_variable *= " + list_parameters_call
            function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
        elif OperatorType(method["operator_type"]) == OperatorType.DIV_EQ:
            # /=
            if len(method["parameters"]) != 1:
                raise Exception("Method \"operator/=\" has more than one parameter.")
            if method["const_qualified"]:
                raise Exception("Method \"operator/=\" is const qualified.")
            function_call_str = "object_variable /= " + list_parameters_call
            function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
        elif OperatorType(method["operator_type"]) == OperatorType.PERC_EQ:
            # %=
            if len(method["parameters"]) != 1:
                raise Exception("Method \"operator%=\" has more than one parameter.")
            if method["const_qualified"]:
                raise Exception("Method \"operator%=\" is const qualified.")
            function_call_str = "object_variable %= " + list_parameters_call
            function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
        elif OperatorType(method["operator_type"]) == OperatorType.LTLT:
            # <<
            if len(method["parameters"]) != 1:
                raise Exception("Method \"operator<<\" has more than one parameter.")
            if method["const_qualified"]:
                return_value_utilization = 'printf("%d\\n", ret_value);'
                function_call_str = r_type + " ret_value = object_variable << " + list_parameters_call
            else:
                function_call_str = "object_variable << " + list_parameters_call
            function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
        elif OperatorType(method["operator_type"]) == OperatorType.ROUND_BRACKETS:
            # ()
            if method["const_qualified"]:
                return_value_utilization = 'printf("%d\\n", ret_value);'
                function_call_str = r_type + " ret_value = object_variable(" + list_parameters_call + ")"
            else:
                function_call_str = "object_variable(" + list_parameters_call + ")"
            function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
        elif OperatorType(method["operator_type"]) == OperatorType.PLUSPLUS:
            # ++
            if method["const_qualified"]:
                return_value_utilization = 'printf("%d\\n", ret_value);'
                function_call_str = r_type + " ret_value = object_variable++"
                if len(method["parameters"]) > 0:
                    function_call_str += "(" + list_parameters_call + ")"
            else:
                function_call_str = "object_variable++"
                if len(method["parameters"]) > 0:
                    function_call_str += "(" + list_parameters_call + ")"
            if len(method["parameters"]) > 0:
                function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
            else:
                function_def_str = class_name_token_long + " object_variable"
        elif OperatorType(method["operator_type"]) == OperatorType.MINUSMINUS:
            # --
            if method["const_qualified"]:
                return_value_utilization = 'printf("%d\\n", ret_value);'
                function_call_str = r_type + " ret_value = object_variable--"
                if len(method["parameters"]) > 0:
                    function_call_str += "(" + list_parameters_call + ")"
            else:
                function_call_str = "object_variable--"
                if len(method["parameters"]) > 0:
                    function_call_str += "(" + list_parameters_call + ")"
            if len(method["parameters"]) > 0:
                function_def_str = class_name_token_long + " object_variable, " + list_parameters_function
            else:
                function_def_str = class_name_token_long + " object_variable"   
        else:
            print(method)
            raise Exception(str(method.operator) + " not implemented.")
        # Substituting everything
        building_template = building_template.replace("$FUNCTION_CALL$", function_call_str)            
        building_template = building_template.replace("$PARAMETER_LIST$", function_def_str)         
        building_template = building_template.replace("$RETURN_UTILIZATION$", return_value_utilization)        
        building_template = building_template.replace("$VARIABLE$", variable_str)        
        # Saving file
        index = 1
        while isfile(join(path, method["method_name"] + "__" + str(index) + ".cpp")):
            index += 1
        simple_dict = {"method_name": method["method_name"],
                       "class_name": class_path_name,
                       "tokens": tokens}
        if compiler_options:
            simple_dict["compiler_options"] = compiler_options
        f = open(join(path, method["method_name"].replace("/", "div") + "__" + str(index) + ".json"), "w")
        f.write(json.dumps(simple_dict, indent=2))
        f.close()
        f = open(join(path, method["method_name"].replace("/", "div") + "__" + str(index) + ".cpp"), "w")
        f.write(building_template)
        f.close()

def sources_builder(class_summary_file_path, sources_destination_path):
    builder_logger = logging.getLogger('sources_builder')
    # Checks
    if not isfile(class_summary_file_path):
        raise Exception(class_summary_file_path + " is not a file path")
    if not isdir(sources_destination_path):
        raise Exception(sources_destination_path + " is not a directory path")
    # Retriving the class summary
    builder_logger.info("[INFO] Working on summary class " + class_summary_file_path)
    f = open(class_summary_file_path)
    content = f.read()
    f.close()
    class_summary = json.loads(content)
    # Creating folder for sources
    class_name = class_summary["class_name"]
    class_sources_path = join(sources_destination_path, class_name)
    if exists(class_sources_path) and isdir(class_sources_path):
        rmtree(class_sources_path)
        builder_logger.debug("[DEBUG] Removed " + class_sources_path + " directory.")
    mkdir(class_sources_path)
    builder_logger.debug("[DEBUG] Created " + class_sources_path + " directory.")
    # Retrieving class default template 
    for building_template in _load_default_templates():
        # Substituting includes
        if "standard_include" in class_summary.keys():
            include_str = "#include <" + class_summary["standard_include"] +">"
        else:
            include_str = '#include "' + class_summary["absolute_include"] + '"'
        building_template = building_template.replace("$CLASS_INCLUDE$", include_str)
        # Substituting optional includes
        if "optional_includes" in class_summary.keys():
            s = ""
            for include in class_summary["optional_includes"]:
                s += "#include " + include + "\n"
            s = s[:-1]
            building_template = building_template.replace("$OPTIONAL_INCLUDES$", s)
        else:
            building_template = building_template.replace("$OPTIONAL_INCLUDES$", "")
        # Substituting optional typedefs
        typedefs_str = ""
        if "optional_typedefs" in class_summary:
            for typedef in class_summary["optional_typedefs"]:
                typedefs_str += typedef + ";\n"
            typedefs_str = typedefs_str[:-1]
        building_template = building_template.replace("$OPTIONAL_TYPEDEFS$", typedefs_str)
        # Substituting namespace
        namespace_str = "using namespace " + class_summary["namespace"] + ";"
        building_template = building_template.replace("$OPTIONAL_NAMESPACE$", namespace_str)
        # From now on there will be a different source file for every method
        class_name_long = _create_class_definition_string(class_summary)
        if "::" in class_summary["class_name"]:
            class_name_simple = class_summary["class_name"].split("::")[-1]
        else:
            class_name_simple = class_summary["class_name"]
        class_name_token_long = _create_class_token_string(class_summary)
        class_name_token_short = _create_class_token_string(class_summary, long=False)
        # Creating sources
        public_methods_path = join(class_sources_path, "public")
        if not exists(public_methods_path):
            mkdir(public_methods_path)
        if "compiler_options" in class_summary.keys():
            compiler_options = class_summary["compiler_options"]
        else:
            compiler_options = []
        _build_methods_sources(class_name_long,
                               class_name_simple,
                               class_name_token_long,
                               class_name_token_short,
                               building_template,
                               class_summary["public"],
                               class_summary["template_values"],
                               public_methods_path,
                               class_summary["class_name"],
                               class_summary["tokens"],
                               compiler_options)
        builder_logger.info("[INFO] Done.")