from subprocess import Popen, PIPE
from utils.helper import strip_parenthesis, ParenthesisType


gpp_version = None

def _invoke_gpp():
    cmd = ["g++", "--version"]
    pipe = Popen(cmd, stdout=PIPE)
    output = (pipe.stdout.readline()).decode("ascii")
    return output


def _get_cpp_version():
    output = _invoke_gpp().split("\n")[0]
    version = strip_parenthesis(output)
    while " " in version:
        version = version.replace(" ", "")
    version = version.replace("g++", "")
    return version
    

def get_gpp_version():
    global gpp_version

    if gpp_version is None:
        gpp_version = _get_cpp_version()
    return gpp_version