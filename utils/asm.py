from tempfile import mkdtemp
from shutil import rmtree
from os.path import join
from elftools.elf.elffile import ELFFile
import subprocess

PREFIX  = ['.section .shellcode,"awx"',
            '.global _start',
            '.global __start',
            '_start:',
            '__start:']

HEADERS = {
'i386'  :   ['.intel_syntax noprefix'],
'amd64' :   ['.intel_syntax noprefix'],
'arm'   :   ['.syntax unified',
            '.arch armv7-a',
            '.arm'],
'thumb' :   ['.syntax unified',
            '.arch armv7-a',
            '.thumb'],
'mips'  :   ['.set mips2',
            '.set noreorder',],
}



def _run(cmd, stdin = None):
    """
    Private function. Executes a bash command.
    """

    try:
        proc = subprocess.Popen(
            cmd,
            stdin  = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines = True
        )
        stdout, stderr = proc.communicate(stdin)
    except OSError as e:
        raise e

    return stdout



def asm(shellcode, arch):
    """
    Returns a string which is the assembly code of the provided shellcode
    for the provided architecture.
    """

    # Preparing directories
    tmpdir = mkdtemp(prefix = 'asm-')
    asm_path = join(tmpdir, 'asm')
    obj_path = join(tmpdir, 'obj')

    # Preparing shellcode
    code = '\n'.join(PREFIX + HEADERS.get(arch, [])) + '\n'
    code += shellcode + '\n'

    # Catch exceptions in order to delete the temp directory
    try:

        # Writing shellcode in a file
        with open(asm_path, 'w') as fd:
            fd.write(code)

        # Assemblying the shellcode
        _run(['as', '-o', obj_path, asm_path])

        # Opening the obj as ELF and retrieving the shellcode section
        elf_fd = open(obj_path, "rb")
        elf_obj = ELFFile(elf_fd)
        shellcode_section = elf_obj.get_section_by_name(".shellcode")
        shellcode_code = shellcode_section.data()
    except Exception as e:
        rmtree(tmpdir)
        raise e

    rmtree(tmpdir)
    return shellcode_code