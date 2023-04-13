from enum import Enum

class NodeType(Enum):
    INTERMEDIATE    = 1
    INITIAL         = 2
    FINAL           = 3
    NORETURN        = 4
    SINGULAR        = 5