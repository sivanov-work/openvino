import argparse
import os
import re
import subprocess
import sys

from collections import defaultdict
from glob import glob

def convert_to_int_if_possible(s):
    try:
        return int(s)
    except ValueError:
        return s

def package_sort_key(package_and_its_version):
    # transfrom a string specifying a package and its version
    # into a list of strings and numbers allowing
    # to employ the natural sort algo for arrays
    return [convert_to_int_if_possible(part) for part in re.split('([0-9]+)', package_and_its_version) ]

def find_deps(ov_package_path, deps_package_names):
    wheel_deps_list_to_find = deps_package_names.copy()
    wheel_deps_list_to_find.extend([d.replace('-', '_') for d in deps_package_names])
    wheels_dep_paths = defaultdict(list) # the same package may have multiple versions
    for d in wheel_deps_list_to_find:
        search_glob = os.path.join(ov_package_path, "**/" , "*" + d + "*.whl")
        package_version_list = glob(search_glob, recursive=True)
        for filename in sorted(package_version_list, key=package_sort_key):
            wheels_dep_paths[d].append(filename)
    if len(wheels_dep_paths) != len(deps_package_names):
        raise RuntimeError(f"Cannot find all required dependencies {deps_package_names} in '*.whl' from OV package by path: {ov_package_path}, found: {wheels_dep_paths}")
    return wheels_dep_paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("ov_package_path", help="Path to openVINO package")
    args = parser.parse_args()
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(curr_dir_path, "inner_ov_package_requirements.txt"), "r") as inner_req_file:
        found_deps = find_deps(args.ov_package_path, inner_req_file.read().splitlines())
        generated_file_name = os.path.join(curr_dir_path, "generated_gathered_requirements_from_ov_package.txt")
        with open(generated_file_name, "w") as generated_desp_file:
            for versions_of_package in found_deps.values():
                # use a version with the highest number only
                generated_desp_file.write(versions_of_package[-1])
        print(f"Wheels dependencies have been written into: {generated_file_name}")
