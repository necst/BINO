from enum import IntEnum, Enum, auto


class InstructionClass(IntEnum):
    """
    Class for amd64 colors.
    """
    def _generate_next_value_(name, start, count, last_values):
        if count == 0:
            return 0
        else:
            return 2 ** (count - 1)

    # Empty
    EMPTY = auto()
    # Classes
    ARITHMETIC = auto()
    BRANCH = auto()
    CALL = auto()
    COND_MOVE = auto()
    DATA_TRANSFER = auto()
    FLAGS = auto()
    FLOAT = auto()
    FLOAT_COND_MOVE = auto()
    HALT = auto()
    INTERLEAVING = auto()
    JUMP = auto()
    LEA = auto()
    LOGIC = auto()
    MISC = auto()
    RETURN = auto()
    SIGN = auto()
    STACK = auto()
    STRING = auto()
    SYSCALL = auto()
    TEST = auto()
    INVALID = auto()
    # TODO classes
    NO_CLASS = auto()


# Rename to save space
IC = InstructionClass
# Colors list
Colors = {
    # EMPTY
    "nop":          IC.EMPTY,           # IC.EMPTY
    "endbr64":      IC.EMPTY,           # IC.EMPTY
    # ARITHMETIC
    "aaa":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "aad":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "aam":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "aas":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "adc":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "add":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "daa":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "das":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "dec":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "div":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "idiv":         IC.ARITHMETIC,      # IC.ARITHMETIC
    "imul":         IC.ARITHMETIC,      # IC.ARITHMETIC
    "inc":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "lock aaa":     IC.ARITHMETIC,      # IC.ARITHMETIC
    "lock aad":     IC.ARITHMETIC,      # IC.ARITHMETIC
    "lock aam":     IC.ARITHMETIC,      # IC.ARITHMETIC
    "lock aas":     IC.ARITHMETIC,      # IC.ARITHMETIC
    "lock adc":     IC.ARITHMETIC,      # IC.ARITHMETIC
    "lock add":     IC.ARITHMETIC,      # IC.ARITHMETIC
    "lock sub":     IC.ARITHMETIC,      # IC.ARITHMETIC
    "lock and":     IC.ARITHMETIC,      # IC.ARITHMETIC
    "mul":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "rcl":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "rcr":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "rol":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "ror":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "sal":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "sar":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "sbb":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "shl":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "shr":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "sub":          IC.ARITHMETIC,      # IC.ARITHMETIC
    "vcvtdq2ps":    IC.ARITHMETIC,      # IC.ARITHMETIC
    "vpaddd":       IC.ARITHMETIC,      # IC.ARITHMETIC
    "vpsrld":       IC.ARITHMETIC,      # IC.ARITHMETIC
    "vpslld":       IC.ARITHMETIC,      # IC.ARITHMETIC

    "paddq": IC.ARITHMETIC,
    "psubq": IC.ARITHMETIC,
    "lock xadd": IC.ARITHMETIC,
    "paddd": IC.ARITHMETIC,
    "lock dec": IC.ARITHMETIC,
    "vpsubd": IC.ARITHMETIC,
    "vpaddq": IC.ARITHMETIC,
    "fdivrp": IC.ARITHMETIC,
    "psubd": IC.ARITHMETIC,
    "lock inc": IC.ARITHMETIC,
    "pmuludq": IC.ARITHMETIC,
    # BRANCH
    "bnd jo":       IC.BRANCH,          # IC.BRANCH
    "bnd jno":      IC.BRANCH,          # IC.BRANCH
    "bnd js":       IC.BRANCH,          # IC.BRANCH
    "bnd jns":      IC.BRANCH,          # IC.BRANCH
    "bnd je":       IC.BRANCH,          # IC.BRANCH
    "bnd jz":       IC.BRANCH,          # IC.BRANCH
    "bnd jne":      IC.BRANCH,          # IC.BRANCH
    "bnd jnz":      IC.BRANCH,          # IC.BRANCH
    "bnd jb":       IC.BRANCH,          # IC.BRANCH
    "bnd jnae":     IC.BRANCH,          # IC.BRANCH
    "bnd jc":       IC.BRANCH,          # IC.BRANCH
    "bnd jnb":      IC.BRANCH,          # IC.BRANCH
    "bnd jae":      IC.BRANCH,          # IC.BRANCH
    "bnd jnc":      IC.BRANCH,          # IC.BRANCH
    "bnd jbe":      IC.BRANCH,          # IC.BRANCH
    "bnd jna":      IC.BRANCH,          # IC.BRANCH
    "bnd ja":       IC.BRANCH,          # IC.BRANCH
    "bnd jnbe":     IC.BRANCH,          # IC.BRANCH
    "bnd jl":       IC.BRANCH,          # IC.BRANCH
    "bnd jnge":     IC.BRANCH,          # IC.BRANCH
    "bnd jge":      IC.BRANCH,          # IC.BRANCH
    "bnd jnl":      IC.BRANCH,          # IC.BRANCH
    "bnd jle":      IC.BRANCH,          # IC.BRANCH
    "bnd jng":      IC.BRANCH,          # IC.BRANCH
    "bnd jg":       IC.BRANCH,          # IC.BRANCH
    "bnd jnle":     IC.BRANCH,          # IC.BRANCH
    "bnd jp":       IC.BRANCH,          # IC.BRANCH
    "bnd jpe":      IC.BRANCH,          # IC.BRANCH
    "bnd jnp":      IC.BRANCH,          # IC.BRANCH
    "bnd jpo":      IC.BRANCH,          # IC.BRANCH
    "bnd jcxz":     IC.BRANCH,          # IC.BRANCH
    "bnd jecxz":    IC.BRANCH,          # IC.BRANCH
    "bnd jrcxz":    IC.BRANCH,          # IC.BRANCH
    "bnd loop":     IC.BRANCH,          # IC.BRANCH
    "bnd loopcc":   IC.BRANCH,          # IC.BRANCH
    "bnd loope":    IC.BRANCH,          # IC.BRANCH
    "bnd loopne":   IC.BRANCH,          # IC.BRANCH
    "bnd loopnz":   IC.BRANCH,          # IC.BRANCH
    "bnd loopz":    IC.BRANCH,          # IC.BRANCH
    "ja":           IC.BRANCH,          # IC.BRANCH
    "jae":          IC.BRANCH,          # IC.BRANCH
    "jb":           IC.BRANCH,          # IC.BRANCH
    "jbe":          IC.BRANCH,          # IC.BRANCH
    "jc":           IC.BRANCH,          # IC.BRANCH
    "jcxz":         IC.BRANCH,          # IC.BRANCH
    "je":           IC.BRANCH,          # IC.BRANCH
    "jecxz":        IC.BRANCH,          # IC.BRANCH
    "jg":           IC.BRANCH,          # IC.BRANCH
    "jge":          IC.BRANCH,          # IC.BRANCH
    "jl":           IC.BRANCH,          # IC.BRANCH
    "jle":          IC.BRANCH,          # IC.BRANCH
    "jna":          IC.BRANCH,          # IC.BRANCH
    "jnae":         IC.BRANCH,          # IC.BRANCH
    "jnc":          IC.BRANCH,          # IC.BRANCH
    "jnb":          IC.BRANCH,          # IC.BRANCH
    "jnbe":         IC.BRANCH,          # IC.BRANCH
    "jne":          IC.BRANCH,          # IC.BRANCH
    "jng":          IC.BRANCH,          # IC.BRANCH
    "jnge":         IC.BRANCH,          # IC.BRANCH
    "jnl":          IC.BRANCH,          # IC.BRANCH
    "jnle":         IC.BRANCH,          # IC.BRANCH
    "jno":          IC.BRANCH,          # IC.BRANCH
    "jnp":          IC.BRANCH,          # IC.BRANCH
    "jns":          IC.BRANCH,          # IC.BRANCH
    "jnz":          IC.BRANCH,          # IC.BRANCH
    "jo":           IC.BRANCH,          # IC.BRANCH
    "jp":           IC.BRANCH,          # IC.BRANCH
    "jpe":          IC.BRANCH,          # IC.BRANCH
    "jpo":          IC.BRANCH,          # IC.BRANCH
    "jrcxz":        IC.BRANCH,          # IC.BRANCH
    "js":           IC.BRANCH,          # IC.BRANCH
    "jz":           IC.BRANCH,          # IC.BRANCH
    "loop":         IC.BRANCH,          # IC.BRANCH
    "loope":        IC.BRANCH,          # IC.BRANCH
    "loopne":       IC.BRANCH,          # IC.BRANCH
    "loopz":        IC.BRANCH,          # IC.BRANCH
    # CALL
    "bnd call":     IC.CALL,            # IC.CALL
    "bnd lcall":    IC.CALL,            # IC.CALL
    "call":         IC.CALL,            # IC.CALL
    "lcall":        IC.CALL,            # IC.CALL
    # COND_MOVE
    "cmova":        IC.COND_MOVE,       # IC.COND_MOVE
    "cmovae":       IC.COND_MOVE,       # IC.COND_MOVE
    "cmovb":        IC.COND_MOVE,       # IC.COND_MOVE
    "cmovbe":       IC.COND_MOVE,       # IC.COND_MOVE
    "cmove":        IC.COND_MOVE,       # IC.COND_MOVE
    "cmovg":        IC.COND_MOVE,       # IC.COND_MOVE
    "cmovge":       IC.COND_MOVE,       # IC.COND_MOVE
    "cmovl":        IC.COND_MOVE,       # IC.COND_MOVE
    "cmovle":       IC.COND_MOVE,       # IC.COND_MOVE
    "cmovne":       IC.COND_MOVE,       # IC.COND_MOVE
    "cmovno":       IC.COND_MOVE,       # IC.COND_MOVE
    "cmovns":       IC.COND_MOVE,       # IC.COND_MOVE
    "cmovs":        IC.COND_MOVE,       # IC.COND_MOVE
    # DATA TRANSFER
    "mov":          IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movs":         IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movsb":        IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movsxd":       IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movabs":       IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movzx":        IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movsd":        IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "vmovsd":       IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "vmovss":       IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "vmovaps":      IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "vmovdqa":      IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "vpmovmskb":    IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movsx":        IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movd":         IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movdqa":       IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movdqu":       IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movups":       IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movss":        IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movapd":       IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movaps":       IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "movq":         IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "xchg":         IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "vmovapd":      IC.DATA_TRANSFER,   # IC.DATA_TRANSFER
    "vpgatherdd":   IC.DATA_TRANSFER,   # IC.DATA_TRANSFER

    "vmovd": IC.DATA_TRANSFER,
    "vpinsrq": IC.DATA_TRANSFER,
    "vmovq": IC.DATA_TRANSFER,
    # FLAGS
    "bt":           IC.FLAGS,           # IC.FLAGS
    "bts":          IC.FLAGS,           # IC.FLAGS
    "btr":          IC.FLAGS,           # IC.FLAGS
    "btc":          IC.FLAGS,           # IC.FLAGS
    "clc":          IC.FLAGS,           # IC.FLAGS
    "cld":          IC.FLAGS,           # IC.FLAGS
    "cli":          IC.FLAGS,           # IC.FLAGS
    "cmc":          IC.FLAGS,           # IC.FLAGS
    "lahf":         IC.FLAGS,           # IC.FLAGS
    "ldmxcsr":      IC.FLAGS,           # IC.FLAGS
    "popf":         IC.FLAGS,           # IC.FLAGS
    "popfd":        IC.FLAGS,           # IC.FLAGS
    "popfq":        IC.FLAGS,           # IC.FLAGS
    "pushf":        IC.FLAGS,           # IC.FLAGS
    "pushfd":       IC.FLAGS,           # IC.FLAGS
    "pushfq":       IC.FLAGS,           # IC.FLAGS
    "sahf":         IC.FLAGS,           # IC.FLAGS
    "stc":          IC.FLAGS,           # IC.FLAGS
    "std":          IC.FLAGS,           # IC.FLAGS
    "sti":          IC.FLAGS,           # IC.FLAGS

    "stmxcsr": IC.FLAGS,
    "setp": IC.FLAGS,
    # FLOAT
    "addsd":        IC.FLOAT,           # IC.FLOAT
    "addss":        IC.FLOAT,           # IC.FLOAT
    "cmpnlesd":     IC.FLOAT,           # IC.FLOAT
    "cvtsi2sd":     IC.FLOAT,           # IC.FLOAT
    "cvtss2sd":     IC.FLOAT,           # IC.FLOAT
    "cvtsi2ss":     IC.FLOAT,           # IC.FLOAT
    "cvtsi2ss":     IC.FLOAT,           # IC.FLOAT  
    "cvtsd2ss":     IC.FLOAT,           # IC.FLOAT
    "cvttss2si":    IC.FLOAT,           # IC.FLOAT
    "cvttsd2si":    IC.FLOAT,           # IC.FLOAT
    "divsd":        IC.FLOAT,           # IC.FLOAT
    "divss":        IC.FLOAT,           # IC.FLOAT
    "fNsave":       IC.FLOAT,           # IC.FLOAT
    "fNstcw":       IC.FLOAT,           # IC.FLOAT
    "fNstenv":      IC.FLOAT,           # IC.FLOAT
    "fNstsw":       IC.FLOAT,           # IC.FLOAT
    "faddl":        IC.FLOAT,           # IC.FLOAT
    "fadds":        IC.FLOAT,           # IC.FLOAT
    "faddp":        IC.FLOAT,           # IC.FLOAT
    "fbld":         IC.FLOAT,           # IC.FLOAT
    "fbstp":        IC.FLOAT,           # IC.FLOAT
    "fchs":         IC.FLOAT,           # IC.FLOAT
    "fcom":         IC.FLOAT,           # IC.FLOAT
    "fcoml":        IC.FLOAT,           # IC.FLOAT
    "fcomp":        IC.FLOAT,           # IC.FLOAT
    "fcompl":       IC.FLOAT,           # IC.FLOAT
    "fcomps":       IC.FLOAT,           # IC.FLOAT
    "fcompp":       IC.FLOAT,           # IC.FLOAT
    "fcoms":        IC.FLOAT,           # IC.FLOAT
    "fcos":         IC.FLOAT,           # IC.FLOAT
    "fdiv":         IC.FLOAT,           # IC.FLOAT
    "fdivl":        IC.FLOAT,           # IC.FLOAT
    "fdivrl":       IC.FLOAT,           # IC.FLOAT
    "fdivrs":       IC.FLOAT,           # IC.FLOAT
    "fdivs":        IC.FLOAT,           # IC.FLOAT
    "fiadd":        IC.FLOAT,           # IC.FLOAT
    "fiaddl":       IC.FLOAT,           # IC.FLOAT
    "ficom":        IC.FLOAT,           # IC.FLOAT
    "ficoml":       IC.FLOAT,           # IC.FLOAT
    "ficomp":       IC.FLOAT,           # IC.FLOAT
    "ficompl":      IC.FLOAT,           # IC.FLOAT
    "fidiv":        IC.FLOAT,           # IC.FLOAT
    "fidivl":       IC.FLOAT,           # IC.FLOAT
    "fidivr":       IC.FLOAT,           # IC.FLOAT
    "fidivrl":      IC.FLOAT,           # IC.FLOAT
    "fild":         IC.FLOAT,           # IC.FLOAT
    "fildl":        IC.FLOAT,           # IC.FLOAT
    "fildll":       IC.FLOAT,           # IC.FLOAT
    "fimul":        IC.FLOAT,           # IC.FLOAT
    "fimull":       IC.FLOAT,           # IC.FLOAT
    "fist":         IC.FLOAT,           # IC.FLOAT
    "fistl":        IC.FLOAT,           # IC.FLOAT
    "fistp":        IC.FLOAT,           # IC.FLOAT
    "fistpl":       IC.FLOAT,           # IC.FLOAT
    "fistpll":      IC.FLOAT,           # IC.FLOAT
    "fisub":        IC.FLOAT,           # IC.FLOAT
    "fisubl":       IC.FLOAT,           # IC.FLOAT
    "fisubr":       IC.FLOAT,           # IC.FLOAT
    "fisubrl":      IC.FLOAT,           # IC.FLOAT
    "fldcw":        IC.FLOAT,           # IC.FLOAT
    "fldenv":       IC.FLOAT,           # IC.FLOAT
    "fldl":         IC.FLOAT,           # IC.FLOAT
    "flds":         IC.FLOAT,           # IC.FLOAT
    "fldt":         IC.FLOAT,           # IC.FLOAT
    "fldz":         IC.FLOAT,           # IC.FLOAT
    "fld1":         IC.FLOAT,           # IC.FLOAT
    "fmull":        IC.FLOAT,           # IC.FLOAT
    "fmuls":        IC.FLOAT,           # IC.FLOAT
    "frstor":       IC.FLOAT,           # IC.FLOAT
    "fsin":         IC.FLOAT,           # IC.FLOAT
    "fstl":         IC.FLOAT,           # IC.FLOAT
    "fstpl":        IC.FLOAT,           # IC.FLOAT
    "fstps":        IC.FLOAT,           # IC.FLOAT
    "fstpt":        IC.FLOAT,           # IC.FLOAT
    "fsts":         IC.FLOAT,           # IC.FLOAT
    "fsub":         IC.FLOAT,           # IC.FLOAT
    "fsubp":        IC.FLOAT,           # IC.FLOAT
    "fsubl":        IC.FLOAT,           # IC.FLOAT
    "fsubrl":       IC.FLOAT,           # IC.FLOAT
    "fsubrs":       IC.FLOAT,           # IC.FLOAT
    "fsubrp":       IC.FLOAT,           # IC.FLOAT
    "fsubs":        IC.FLOAT,           # IC.FLOAT
    "fstp":         IC.FLOAT,           # IC.FLOAT
    "fnstcw":       IC.FLOAT,           # IC.FLOAT
    "fadd":         IC.FLOAT,           # IC.FLOAT
    "fxch":         IC.FLOAT,           # IC.FLOAT
    "fucomip":      IC.FLOAT,           # IC.FLOAT
    "fdivp":        IC.FLOAT,           # IC.FLOAT
    "fld":          IC.FLOAT,           # IC.FLOAT
    "fmul":         IC.FLOAT,           # IC.FLOAT
    "fsubr":        IC.FLOAT,           # IC.FLOAT
    "fdivr":        IC.FLOAT,           # IC.FLOAT
    "movhps":       IC.FLOAT,           # IC.FLOAT
    "mulsd":        IC.FLOAT,           # IC.FLOAT
    "mulss":        IC.FLOAT,           # IC.FLOAT
    "subsd":        IC.FLOAT,           # IC.FLOAT
    "subss":        IC.FLOAT,           # IC.FLOAT
    "ucomisd":      IC.FLOAT,           # IC.FLOAT
    "ucomiss":      IC.FLOAT,           # IC.FLOAT
    "unpcklps":     IC.FLOAT,           # IC.FLOAT
    "xorps":        IC.FLOAT,           # IC.FLOAT
    "vaddps":       IC.FLOAT,           # IC.FLOAT
    "vmulps":       IC.FLOAT,           # IC.FLOAT
    "vfmadd132pd":  IC.FLOAT,           # IC.FLOAT
    "vfmadd132ps":  IC.FLOAT,           # IC.FLOAT
    "vfmadd132sd":  IC.FLOAT,           # IC.FLOAT
    "vfmadd132ss":  IC.FLOAT,           # IC.FLOAT
    "vfmadd213pd":  IC.FLOAT,           # IC.FLOAT
    "vfmadd213sd":  IC.FLOAT,           # IC.FLOAT
    "vfmadd213ss":  IC.FLOAT,           # IC.FLOAT
    "vfmadd231ps":  IC.FLOAT,           # IC.FLOAT
    "vfmadd231sd":  IC.FLOAT,           # IC.FLOAT
    "vfmadd231ss":  IC.FLOAT,           # IC.FLOAT
    "vfmsub132pd":  IC.FLOAT,           # IC.FLOAT
    "vfmsub132sd":  IC.FLOAT,           # IC.FLOAT
    "vfmsub231sd":  IC.FLOAT,           # IC.FLOAT
    "vfnmadd132pd": IC.FLOAT,           # IC.FLOAT
    "vfnmadd132ps": IC.FLOAT,           # IC.FLOAT
    "vfnmadd132sd": IC.FLOAT,           # IC.FLOAT
    "vfnmadd132ss": IC.FLOAT,           # IC.FLOAT
    "vfnmadd231pd": IC.FLOAT,           # IC.FLOAT
    "vfnmadd231ps": IC.FLOAT,           # IC.FLOAT
    "vfnmadd231sd": IC.FLOAT,           # IC.FLOAT
    "vfnmadd231ss": IC.FLOAT,           # IC.FLOAT
    "vcvtps2dq":    IC.FLOAT,           # IC.FLOAT
    "vcvtss2sd":    IC.FLOAT,           # IC.FLOAT
    "vmaxps":       IC.FLOAT,           # IC.FLOAT
    "vminps":       IC.FLOAT,           # IC.FLOAT
    "vorps":        IC.FLOAT,           # IC.FLOAT
    "vsqrtsd":      IC.FLOAT,           # IC.FLOAT
    "vxorps":       IC.FLOAT,           # IC.FLOAT

    "vcvtsd2ss": IC.FLOAT,
    "movlhps": IC.FLOAT,
    "subps": IC.FLOAT,
    "cvttpd2dq": IC.FLOAT,
    "vaddpd": IC.FLOAT,
    "vbroadcastsd": IC.FLOAT,
    "vmaxss": IC.FLOAT,
    "vcvttpd2dq": IC.FLOAT,
    "cmpltpd": IC.FLOAT,
    "vmulpd": IC.FLOAT,
    "vucomiss": IC.FLOAT,
    "movhpd": IC.FLOAT,
    "fmulp": IC.FLOAT,
    "vmulss": IC.FLOAT,
    "vcmpltpd": IC.FLOAT,
    "cmplesd": IC.FLOAT,
    "vsubsd": IC.FLOAT,
    "vcvttsd2si": IC.FLOAT,
    "orpd": IC.FLOAT,
    "mulpd": IC.FLOAT,
    "vaddsd": IC.FLOAT,
    "cvtdq2pd": IC.FLOAT,
    "vsubss": IC.FLOAT,
    "pcmpeqd": IC.FLOAT,
    "andnps": IC.FLOAT,
    "movupd": IC.FLOAT,
    "maxsd": IC.FLOAT,
    "vmovlhps": IC.FLOAT,
    "vcvtsi2sd": IC.FLOAT,
    "vaddss": IC.FLOAT,
    "cvtdq2ps": IC.FLOAT,
    "maxss": IC.FLOAT,
    "cmpnless": IC.FLOAT,
    "movhlps": IC.FLOAT,
    "addps": IC.FLOAT,
    "vucomisd": IC.FLOAT,
    "cmpltsd": IC.FLOAT,
    "divpd": IC.FLOAT,
    "andps": IC.FLOAT,
    "vcvtss2si": IC.FLOAT,
    "cvtps2pd": IC.FLOAT,
    "vcvtsd2ss": IC.FLOAT,
    "movlhps": IC.FLOAT,
    "subps": IC.FLOAT,
    "cvttpd2dq": IC.FLOAT,
    "vaddpd": IC.FLOAT,
    "vbroadcastsd": IC.FLOAT,
    "vmaxss": IC.FLOAT,
    "vcvttpd2dq": IC.FLOAT,
    "cmpltpd": IC.FLOAT,
    "vmulpd": IC.FLOAT,
    "vucomiss": IC.FLOAT,
    "movhpd": IC.FLOAT,
    "fmulp": IC.FLOAT,
    "vmulss": IC.FLOAT,
    "vcmpltpd": IC.FLOAT,
    "cmplesd": IC.FLOAT,
    "vsubsd": IC.FLOAT,
    "vcvttsd2si": IC.FLOAT,
    "orpd": IC.FLOAT,
    "mulpd": IC.FLOAT,
    "vaddsd": IC.FLOAT,
    "cvtdq2pd": IC.FLOAT,
    "vsubss": IC.FLOAT,
    "pcmpeqd": IC.FLOAT,
    "andnps": IC.FLOAT,
    "movupd": IC.FLOAT,
    "maxsd": IC.FLOAT,
    "vmovlhps": IC.FLOAT,
    "vcvtsi2sd": IC.FLOAT,
    "vaddss": IC.FLOAT,
    "cvtdq2ps": IC.FLOAT,
    "maxss": IC.FLOAT,
    "cmpnless": IC.FLOAT,
    "movhlps": IC.FLOAT,
    "addps": IC.FLOAT,
    "vucomisd": IC.FLOAT,
    "cmpltsd": IC.FLOAT,
    "divpd": IC.FLOAT,
    "andps": IC.FLOAT,
    "vcvtss2si": IC.FLOAT,
    "cvtps2pd": IC.FLOAT,
    "vsubpd": IC.FLOAT,
    "cvtpd2ps": IC.FLOAT,
    "minss": IC.FLOAT,
    "vcvtsi2ss": IC.FLOAT,
    "mulps": IC.FLOAT,
    "vmaxpd": IC.FLOAT,
    "subpd": IC.FLOAT,
    "vbroadcastss": IC.FLOAT,
    "vmulsd": IC.FLOAT,
    "vcvtdq2pd": IC.FLOAT,
    "vminpd": IC.FLOAT,
    "vpextrw": IC.FLOAT,
    "vdivss": IC.FLOAT,
    "vandpd": IC.FLOAT,
    "sqrtss": IC.FLOAT,
    "andnpd": IC.FLOAT,
    "addpd": IC.FLOAT,
    "movlpd": IC.FLOAT,
    "orps": IC.FLOAT,
    "vdivsd": IC.FLOAT,
    "cmpltss": IC.FLOAT,
    "vminss": IC.FLOAT,
    "minsd": IC.FLOAT,
    "sqrtsd": IC.FLOAT,
    "vinsertps": IC.FLOAT,
    "fucomi": IC.FLOAT,
    "vsubpd": IC.FLOAT,
    "cvtpd2ps": IC.FLOAT,
    "minss": IC.FLOAT,
    "vcvtsi2ss": IC.FLOAT,
    "mulps": IC.FLOAT,
    "vmaxpd": IC.FLOAT,
    "subpd": IC.FLOAT,
    "vbroadcastss": IC.FLOAT,
    "vmulsd": IC.FLOAT,
    "vcvtdq2pd": IC.FLOAT,
    "vminpd": IC.FLOAT,
    "vpextrw": IC.FLOAT,
    "vdivss": IC.FLOAT,
    "vandpd": IC.FLOAT,
    "sqrtss": IC.FLOAT,
    "andnpd": IC.FLOAT,
    "addpd": IC.FLOAT,
    "movlpd": IC.FLOAT,
    "orps": IC.FLOAT,
    "vdivsd": IC.FLOAT,
    "cmpltss": IC.FLOAT,
    "vminss": IC.FLOAT,
    "minsd": IC.FLOAT,
    "sqrtsd": IC.FLOAT,
    "vinsertps": IC.FLOAT,
    "fucomi": IC.FLOAT,
    # FLOATING POINT CONDITIONAL MOVE
    "fcmovbe":      IC.FLOAT_COND_MOVE, # IC.FLOAT_COND_MOVE
    # HALT
    "hlt":          IC.HALT,            # IC.HALT
    # INTERLEAVING
    "shufps":       IC.INTERLEAVING,    # IC.INTERLEAVING
    "pshufd":       IC.INTERLEAVING,    # IC.INTERLEAVING
    "punpcklqdq":   IC.INTERLEAVING,    # IC.INTERLEAVING
    "punpcklwd":    IC.INTERLEAVING,    # IC.INTERLEAVING
    "unpcklpd":     IC.INTERLEAVING,    # IC.INTERLEAVING
    "vshufps":      IC.INTERLEAVING,    # IC.INTERLEAVING
    "vunpckhps":    IC.INTERLEAVING,    # IC.INTERLEAVING

    "vpshufd": IC.INTERLEAVING,
    "punpckhbw": IC.INTERLEAVING,
    "punpckhwd": IC.INTERLEAVING,
    "punpckldq": IC.INTERLEAVING,
    "vpgatherqq": IC.INTERLEAVING,
    "punpcklbw": IC.INTERLEAVING,
    "punpckhdq": IC.INTERLEAVING,
    "vunpcklps": IC.INTERLEAVING,
    "unpckhpd": IC.INTERLEAVING,
    # JUMP
    "bnd jmp":      IC.JUMP,            # IC.JUMP
    "jmp":          IC.JUMP,            # IC.JUMP
    "ljmp":         IC.JUMP,            # IC.JUMP
    # LEA
    "lea":          IC.LEA,             # IC.LEA
    # LOGIC
    "and":          IC.LOGIC,           # IC.LOGIC
    "andpd":        IC.LOGIC,           # IC.LOGIC
    "vandps":       IC.LOGIC,           # IC.LOGIC
    "vpand":        IC.LOGIC,           # IC.LOGIC
    "neg":          IC.LOGIC,           # IC.LOGIC
    "not":          IC.LOGIC,           # IC.LOGIC
    "or":           IC.LOGIC,           # IC.LOGIC
    "pxor":         IC.LOGIC,           # IC.LOGIC
    "seta":         IC.LOGIC,           # IC.LOGIC
    "setae":        IC.LOGIC,           # IC.LOGIC
    "setb":         IC.LOGIC,           # IC.LOGIC
    "setbe":        IC.LOGIC,           # IC.LOGIC
    "sete":         IC.LOGIC,           # IC.LOGIC
    "setne":        IC.LOGIC,           # IC.LOGIC
    "setnz":        IC.LOGIC,           # IC.LOGIC
    "seto":         IC.LOGIC,           # IC.LOGIC
    "setz":         IC.LOGIC,           # IC.LOGIC
    "setl":         IC.LOGIC,           # IC.LOGIC
    "setle":        IC.LOGIC,           # IC.LOGIC
    "setg":         IC.LOGIC,           # IC.LOGIC
    "setge":        IC.LOGIC,           # IC.LOGIC
    "setnp":        IC.LOGIC,           # IC.LOGIC
    "xor":          IC.LOGIC,           # IC.LOGIC
    "xorpd":        IC.LOGIC,           # IC.LOGIC
    "vxorpd":       IC.LOGIC,           # IC.LOGIC
    "bsr":          IC.LOGIC,           # IC.LOGIC
    "bsf":          IC.LOGIC,           # IC.LOGIC
    "vzeroupper":   IC.LOGIC,           # IC.LOGIC

    "psllq": IC.LOGIC,
    "psrldq": IC.LOGIC,
    "lock or": IC.LOGIC,
    "pand": IC.LOGIC,
    "vpxor": IC.LOGIC,
    "pslld": IC.LOGIC,
    "psrlq": IC.LOGIC,
    "vpor": IC.LOGIC,
    "por": IC.LOGIC,
    "vpsllq": IC.LOGIC,
    "vpsrlq": IC.LOGIC,
    "pandn": IC.LOGIC,
    "psrad": IC.LOGIC,
    # MISC
    "bound":        IC.MISC,            # IC.MISC
    "cRtd":         IC.MISC,            # IC.MISC
    "enter":        IC.MISC,            # IC.MISC
    "icebp":        IC.MISC,            # IC.MISC
    "in":           IC.MISC,            # IC.MISC
    "ins":          IC.MISC,            # IC.MISC
    "insb":         IC.MISC,            # IC.MISC
    "insd":         IC.MISC,            # IC.MISC
    "int1":         IC.MISC,            # IC.MISC
    "int3":         IC.MISC,            # IC.MISC
    "into":         IC.MISC,            # IC.MISC
    "lds":          IC.MISC,            # IC.MISC
    "leave":        IC.MISC,            # IC.MISC
    "les":          IC.MISC,            # IC.MISC
    "out":          IC.MISC,            # IC.MISC
    "outs":         IC.MISC,            # IC.MISC
    "outsd":        IC.MISC,            # IC.MISC
    "outsb":        IC.MISC,            # IC.MISC
    "outsw":        IC.MISC,            # IC.MISC
    "xlat":         IC.MISC,            # IC.MISC
    "xlatb":        IC.MISC,            # IC.MISC

    "mfence": IC.MISC,
    "pause": IC.MISC,
    "prefetcht0": IC.MISC,
    "rdtsc": IC.MISC,
    # TO BE CHECKED
    "crc32":        IC.MISC,            # IC.MISC
    "cpuid":        IC.MISC,            # IC.MISC
    "bswap":        IC.MISC,            # IC.MISC
    # RETURN
    "bnd ret":      IC.RETURN,          # IC.RETURN
    "bnd retf":     IC.RETURN,          # IC.RETURN
    "bnd retn":     IC.RETURN,          # IC.RETURN
    "bnd lret":     IC.RETURN,          # IC.RETURN
    "iret":         IC.RETURN,          # IC.RETURN
    "iretd":        IC.RETURN,          # IC.RETURN
    "iretq":        IC.RETURN,          # IC.RETURN
    "lret":         IC.RETURN,          # IC.RETURN
    "ret":          IC.RETURN,          # IC.RETURN
    "retf":         IC.RETURN,          # IC.RETURN
    "retl":         IC.RETURN,          # IC.RETURN
    # SIGN
    "cbw":          IC.SIGN,            # IC.SIGN
    "cdq":          IC.SIGN,            # IC.SIGN
    "cdqe":         IC.SIGN,            # IC.SIGN
    "cwde":         IC.SIGN,            # IC.SIGN
    "cwd":          IC.SIGN,            # IC.SIGN
    "cqo":          IC.SIGN,            # IC.SIGN
    # STACK
    "pop":          IC.STACK,           # IC.STACK
    "popa":         IC.STACK,           # IC.STACK
    "push":         IC.STACK,           # IC.STACK
    "pusha":        IC.STACK,           # IC.STACK
    # STRING
    "cmpsb":        IC.STRING,          # IC.STRING
    "cmpsd":        IC.STRING,          # IC.STRING
    "lods":         IC.STRING,          # IC.STRING
    "lodsb":        IC.STRING,          # IC.STRING
    "lodsd":        IC.STRING,          # IC.STRING
    "lodsw":        IC.STRING,          # IC.STRING
    "rep movsb":    IC.STRING,          # IC.STRING
    "rep movsd":    IC.STRING,          # IC.STRING
    "rep movsq":    IC.STRING,          # IC.STRING
    "rep stosb":    IC.STRING,          # IC.STRING
    "rep stosd":    IC.STRING,          # IC.STRING
    "rep stosq":    IC.STRING,          # IC.STRING
    "rep stoss":    IC.STRING,          # IC.STRING
    "repe cmps":    IC.STRING,          # IC.STRING
    "repe cmpsb":   IC.STRING,          # IC.STRING
    "repe scasb":   IC.STRING,          # IC.STRING
    "repe scasd":   IC.STRING,          # IC.STRING
    "repne cmps":   IC.STRING,          # IC.STRING
    "repne cmpsb":  IC.STRING,          # IC.STRING
    "repne scasb":  IC.STRING,          # IC.STRING
    "repne scasd":  IC.STRING,          # IC.STRING
    "scas":         IC.STRING,          # IC.STRING
    "scasb":        IC.STRING,          # IC.STRING
    "scasd":        IC.STRING,          # IC.STRING
    "stos":         IC.STRING,          # IC.STRING
    "stosb":        IC.STRING,          # IC.STRING
    "stosd":        IC.STRING,          # IC.STRING
    "stosq":        IC.STRING,          # IC.STRING
    "stoss":        IC.STRING,          # IC.STRING
    # SYSCALL
    "int":          IC.SYSCALL,         # IC.SYSCALL
    "syscall":      IC.SYSCALL,         # IC.SYSCALL
    # TEST
    "cmp":          IC.TEST,            # IC.TEST
    "test":         IC.TEST,            # IC.TEST
    "vpcmpgtd":     IC.TEST,            # IC.TEST
    "vpcmpeqd":     IC.TEST,            # IC.TEST
    "comisd":       IC.TEST,            # IC.TEST
    "comiss":       IC.TEST,            # IC.TEST

    "pcmpgtb": IC.TEST,
    "pcmpgtd": IC.TEST,
    "pcmpgtw": IC.TEST,
    "pcmpeqb": IC.TEST,
    "lock cmpxchg": IC.TEST,
    # INVALID
    "ud2":          IC.INVALID         # IC.INVALID
}
# TODO: ADD PACKED COLORS AND OPERATION, ADD MULTIPLE COLORS FOR INSTRUCTIONS