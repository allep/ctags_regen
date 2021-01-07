#!/usr/bin/env python3

# Author: Alessandro Paganelli (alessandro.paganelli@gmail.com)

import argparse
import os
import subprocess

def recreate_ctags(path):
    """Re-creates ctags database for a given path"""
    print('Recreating ctags database for path: %s' % path)
    os.chdir(path)
    print("I'm inside: %s" % str(os.getcwd()))
    
    ret_ok = True
    try:
        subprocess.run(['ctags', '-R', '.'], check=True)
    except subprocess.CalledProcessError:
        print('Couldn\'t complete ctags DB on %s' % path)
        ret_ok = False

    return ret_ok

def parse_pathfile(pathfile):
    """Parses pathfile line by line to look for projects where to recreate ctags."""
    print('Processing file: %s' % pathfile)
    paths = []
    with open(pathfile) as f:
        for p in f.readlines():
            # Sanitization
            p = p.strip()

            # Skip commented paths and empty lines
            skip = False
            if p.startswith('#'):
                skip = True
            if not p:
                skip = True

            # actual skip
            if skip:
                continue

            # good line
            paths.append(p)

    print('Processing of input file done.')
    return paths

def main():
    """Main script"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--pathfile', help='Path of the file containing the list of paths to be considered.', 
            required=True)

    args = parser.parse_args()

    # preconditions
    # 1) filepath must be a path
    # 2) it must be a real file
    if not os.path.isabs(args.pathfile):
        print('Pathfile is not a full path.')
        exit(1)
    
    if not os.path.exists(args.pathfile) or not os.path.isfile(args.pathfile):
        print('File %s cannot be accessed' % args.pathfile)
        exit(2)

    # go
    paths = parse_pathfile(args.pathfile)
    all_ok = True
    for p in paths:
        # precondition: make sure the directory exists
        if not os.path.exists(p) or not os.path.isdir(p):
            print('Target path %s does not exist or it is not a directory. Skipping it.' % p)
            continue

        all_ok &= recreate_ctags(p)

    if not all_ok:
        print('Some targets failed.')
        exit(3)

    print('Done!')
    exit(0)

# Entrypoint
if __name__ == '__main__':
    main()

