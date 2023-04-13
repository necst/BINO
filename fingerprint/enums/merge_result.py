from enum import Enum

class MergeResult(Enum):
    MERGED = 0
    NOT_MERGED = -1
    ALREADY_MERGED = -2