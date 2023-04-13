from os import listdir, mkdir
import logging
from os.path import isdir, join, exists
from fingerprint.classes.fingerprint import load_fingerprint
from fingerprint.classes.fingerprints_collection import FingerprintsCollection
from fingerprint.classes.fingerprints_collection import load_fingerprints_collection
from fingerprint.classes.fingerprints_collection import save_fingerprints_collection
from fingerprint.enums.merge_result import MergeResult

new_fingerprints = 0
merged_fingerprints = 0
not_merged_fingerprints = 0


def _check_new_entry(arch, path_name, entry, db_path):
    entry_path = join(db_path, arch, path_name, entry)
    if exists(entry_path) and isdir(entry_path):
        return False
    # Creating the entry
    step_1_path = join(db_path, arch)
    if exists(step_1_path):
        if not isdir(step_1_path):
            raise Exception("%s is a file!" % step_1_path)
    else:
        mkdir(step_1_path)
    step_2_path = join(db_path, arch, path_name)
    if exists(step_2_path):
        if not isdir(step_2_path):
            raise Exception("%s is a file!" % step_2_path)
    else:
        mkdir(step_2_path)
    if exists(entry_path):
        if not isdir(entry_path):
            raise Exception("%s is a file!" % entry_path)
    else:
        mkdir(entry_path)
    return True


def _create_new_collection(fp, new_collection_path):
    fpsc = FingerprintsCollection(fp)
    new_collection_file_path = join(new_collection_path, "0.p")
    save_fingerprints_collection(fpsc, new_collection_file_path)


def _append_to_collections(fp, collection_path):
    global new_fingerprints
    global merged_fingerprints
    global not_merged_fingerprints

    merged = False
    fpsc_list = listdir(collection_path)
    for file in fpsc_list:
        collection_file_path = join(collection_path, file)
        fpsc = load_fingerprints_collection(collection_file_path)
        result = fpsc.try_merge(fp)
        if result == MergeResult.MERGED:
            merged = True
            merged_fingerprints += 1
            break
        elif result == MergeResult.ALREADY_MERGED:
            merged = True
            not_merged_fingerprints += 1
            break
    if not merged:
        # New Collection
        fpsc = FingerprintsCollection(fp)
        new_collection_file_path = join(collection_path, str(len(fpsc_list)) + ".p")
        save_fingerprints_collection(fpsc, new_collection_file_path)
        new_fingerprints += 1
    else:
        # Update Fingerprints collection
        save_fingerprints_collection(fpsc, collection_file_path)


def _append_method_to_db(fp, db_path):
    global new_fingerprints

    arch = fp.arch
    path_name = fp.path_name
    bbs_count = fp.get_basic_blocks_count()
    edges_count = fp.get_edges_count()
    entry = "%s_%s" % (bbs_count, edges_count)
    collection_path = join(db_path, arch, path_name, entry)
    if _check_new_entry(arch, path_name, entry, db_path):
        # First fp with such features
        _create_new_collection(fp, collection_path)
        new_fingerprints += 1
    else:
        # At least one fp with such features
        _append_to_collections(fp, collection_path)


def _append_methods_to_db(methods_dir_path, db_path):
    for method in listdir(methods_dir_path):
        method_path = join(methods_dir_path, method)
        fp = load_fingerprint(method_path)
        _append_method_to_db(fp, db_path)


def _append_class_to_db(class_path_src, db_path, storer_logger):
    for methods_dir in listdir(class_path_src):
        methods_dir_path = join(class_path_src, methods_dir)
        storer_logger.debug("Joining directory %s" % methods_dir_path)
        _append_methods_to_db(methods_dir_path, db_path)


def storer(src_path, dst_path):
    global new_fingerprints
    global merged_fingerprints
    global not_merged_fingerprints

    storer_logger = logging.getLogger('storer')
    # Checks
    if not isdir(src_path):
        raise Exception(src_path + " is not a directory path")
    if not isdir(dst_path):
        raise Exception(dst_path + " is not a directory path")
    # Iterating over directories
    for class_name in listdir(src_path):
        class_path_src = join(src_path, class_name, "public")
        if not isdir(class_path_src):
            raise Exception(class_path_src + " is not a directory path")
        # Appending new fingerprints to the existing db
        _append_class_to_db(class_path_src, dst_path, storer_logger)
        # Printing info
        storer_logger.info("New unique fingerprints: %d" % new_fingerprints)
        storer_logger.info("Merged fingerprints: %d" % merged_fingerprints)
        storer_logger.info("Not merged fingerprint: %d" % not_merged_fingerprints)