import subprocess

def file_info(path):
    cmd = ['file', path]
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    file_info = (pipe.stdout.readline()).decode("ascii")
    file_info = file_info.split("\n")[0]
    return file_info
