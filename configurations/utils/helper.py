from os.path import dirname, abspath, join
import xml.etree.ElementTree as et
from fingerprint.enums.colors import InstructionClass as IC

ignored_colors = None
xml_content = None
cpp_version = None
clang_version = None
configuration_path = None

def _read_configuration_file():
    global xml_content
    global configuration_path

    if configuration_path is None:
        prj_path = dirname(abspath(__file__))
        configuration_path = join(prj_path, "..", "configurations.xml")
    if xml_content is None:
        f = open(configuration_path)
        xml_cont = f.read()
        f.close()
    return xml_cont    


def get_ignored_colors():
    global ignored_colors

    if ignored_colors is None:
        ignored_colors = []
        xml_cont = _read_configuration_file()
        root = et.fromstring(xml_cont)
        ign_el = root.find("ignored_colors")
        for child in ign_el:
            ignored_colors.append(IC[child.text])
    return ignored_colors


def get_cpp_version():
    global cpp_version

    if cpp_version is None:
        xml_cont = _read_configuration_file()
        root = et.fromstring(xml_cont)
        cpp_v_el = root.find("cpp_version")
        cpp_version = cpp_v_el.text
    return cpp_version


def get_clang_version():
    global clang_version

    if clang_version is None:
        xml_cont = _read_configuration_file()
        root = et.fromstring(xml_cont)
        clang_v_el = root.find("clang_version")
        clang_version = clang_v_el.text
    return clang_version