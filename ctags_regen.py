#!/usr/bin/env python3

# Author: Alessandro Paganelli (alessandro.paganelli@gmail.com)

import argparse
import os
import subprocess
from datetime import datetime

TAG_FILE_NAME = 'tags'

def write_output_tags_file_for_vim(output_file, recreated_paths):
    """Writes an output file containing the tags recreated by this script."""
    print('------------------------------------------------')
    print('Writing output file: %s' % output_file)
    with open(output_file, 'w') as f:
        header = "\"Generated on {curtime} by ctags_regen\n".format(curtime = datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        tags = 'set tags='
        first = True
        for p in recreated_paths:
            pf = os.path.join(p, TAG_FILE_NAME)
            if first:
                tags += pf
                first = False
            else:
                tags += ','
                tags += pf
            
        tags += '\n'
        f.write(header)
        f.write(tags)

def recreate_ctags(path):
    """Re-creates ctags database for a given path"""
    print('------------------------------------------------')
    print('Recreating ctags database for path: %s' % path)
    os.chdir(path)
    
    ret_ok = True
    try:
        subprocess.run(['ctags', '-R', '-f', TAG_FILE_NAME, '.'], check=True)
    except subprocess.CalledProcessError:
        print('Error: couldn\'t complete ctags DB on %s' % path)
        ret_ok = False

    return ret_ok

def parse_pathfile(pathfile):
    """Parses pathfile line by line to look for projects where to recreate ctags."""
    print('------------------------------------------------')
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
    parser.add_argument('-t', '--tagvimrc', help='Path of the output file that will include the tag file list.',
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

    if not os.path.isabs(args.tagvimrc):
        print('Tagfile is not a full path.')
        exit(3)

    if os.path.exists(args.tagvimrc):
        print('Warining: target file %s will be overwritten' % args.tagvimrc)

    # go
    paths = parse_pathfile(args.pathfile)
    recreated_paths = []
    all_ok = True
    for p in paths:
        # precondition: make sure the directory exists
        if not os.path.exists(p) or not os.path.isdir(p):
            print('Target path %s does not exist or it is not a directory. Skipping it.' % p)
            continue
        
        current_ok = recreate_ctags(p)
        if current_ok:
            recreated_paths.append(p)
        all_ok &= current_ok
    
    # update output tag file
    write_output_tags_file_for_vim(args.tagvimrc, recreated_paths)

    if not all_ok:
        print('Some targets failed.')
        exit(3)

    print('Done!')
    exit(0)

# Entrypoint
if __name__ == '__main__':
    main()

