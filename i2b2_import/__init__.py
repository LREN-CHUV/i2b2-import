import sys
import glob
import fnmatch
import os


def recurse_in_dir_and_apply_fn(folder, file_pattern, process_file_fn):
    if sys.version_info.major == 3 and sys.version_info.minor < 5:
        matches = []
        for root, dirnames, filenames in os.walk(folder):
            for filename in fnmatch.filter(filenames, file_pattern):
                matches.append(os.path.join(root, filename))
        for file_path in matches:
            process_file_fn(file_path)
    else:
        for file_path in glob.iglob(os.path.join(folder, "**/" + file_pattern), recursive=True):
            process_file_fn(file_path)
