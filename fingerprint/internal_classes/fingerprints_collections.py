from os import listdir
from os.path import join, split
from fingerprint.classes.fingerprints_collection import load_fingerprints_collection

class FingerprintsCollections(object):

    def __init__(self, fingerprints_class_path, class_name=None):
        if class_name is None:
            class_name = split(fingerprints_class_path)[1]
        self.class_name = class_name
        self.fingerprints_class_path = fingerprints_class_path
        self.fps_collections = []
        self._load_fingerprints()


    def _load_fingerprints(self):
        for fp_dir in listdir(self.fingerprints_class_path):
            fp_dir_path = join(self.fingerprints_class_path, fp_dir)
            for fp_file in listdir(fp_dir_path):
                fp_file_path = join(fp_dir_path, fp_file)
                self.fps_collections.append(load_fingerprints_collection(fp_file_path))


    def get_fingerprints_collections(self):
        for fpsc in self.fps_collections:
            yield fpsc
