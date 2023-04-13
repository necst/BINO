from shutil import rmtree
from os.path import join
from os.path import isfile
from os import listdir
from enum import Enum


_LEFT_ROUND = "(" 
_RIGHT_ROUND = ")" 
_LEFT_SQUARE = "[" 
_RIGHT_SQUARE = "]" 
_LEFT_CURLY = "{" 
_RIGHT_CURLY = "}"
_LEFT_ANGLE = "<" 
_RIGHT_ANGLE = ">"


class ParenthesisType(Enum):
    ROUND_BRACKETS = 0
    SQUARE_BRACKETS = 1
    CURLY_BRACKETS = 2
    ANGLE_BRACKETS = 3


def remove_duplicates(src_list):
    set_list = []
    for obj in src_list:
        if obj not in set_list:
            set_list.append(obj)
    return set_list


def list_difference(list_1, list_2):
    set_list_1 = remove_duplicates(list_1)
    set_list_2 = remove_duplicates(list_2)
    list_diff = []
    for obj in set_list_1:
        if obj not in set_list_2:
            list_diff.append(obj)
    return list_diff


def is_subset(list_1, sublist_1):
    list_cpy = list_1
    for element in sublist_1:
        i = 0
        found = False
        while i < len(list_cpy):
            if element == list_cpy[i]:
                found = True
                i -= 1
                break
            i += 1
        if not found:
            return False
    return True


def clear_directory(path):
    for file in listdir(path):
        if isfile(join(path,file)):
            remove(join(path,file))
        else:
            rmtree(join(path,file))


def index_of(list_in, sublist):
    list_length = len(list_in)
    sublist_length = len(sublist)
    if sublist_length > list_length:
        return -1
    for index in range(list_length):
        if list_in[index:index+sublist_length] == sublist:
            return index
    return -1


def strip_parenthesis(s, parenthesis_type=ParenthesisType.ROUND_BRACKETS):
    if parenthesis_type == ParenthesisType.ROUND_BRACKETS:
        left_par = _LEFT_ROUND
        right_par = _RIGHT_ROUND
    elif parenthesis_type == ParenthesisType.SQUARE_BRACKETS:
        left_par = _LEFT_SQUARE
        right_par = _RIGHT_SQUARE
    elif parenthesis_type == ParenthesisType.CURLY_BRACKETS:
        left_par = _LEFT_CURLY
        right_par = _RIGHT_CURLY
    elif parenthesis_type == ParenthesisType.ANGLE_BRACKETS:
        left_par = _LEFT_ANGLE
        right_par = _RIGHT_ANGLE
    else:
        raise Exception("Unknown parenthesis type!")

    while(True):
        len_s = len(s)
        # Find first parenthesis
        counter = 0
        for i in range(len_s):
            if s[i] == left_par:
                counter = 1
                start = i
                break
        if counter == 0:
            return s
        for i in range(start + 1, len_s):
            if s[i] == left_par:
                counter += 1
            elif s[i] == right_par:
                counter -= 1
            if counter == 0:
                end = i
                break
        if counter != 0:
            raise Exception("Unbalanced parenthesis!")
        s = s[0:start] + s[end + 1:len_s]


def starts_with(s, subs):
    subs_lenght = len(subs)
    if subs_lenght > len(s):
        return False
    if s[:subs_lenght] == subs:
        return True
    return False


def ends_with(s, subs):
    subs_lenght = len(subs)
    if subs_lenght > len(s):
        return False
    if s[-subs_lenght:] == subs:
        return True
    return False


def invert_dictionary(dictionary):
    return {v: k for k, v in dictionary.items()}