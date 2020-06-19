#! #!/usr/bin/env python

import argparse
from pathlib import Path
import sys
import shutil


def main():
    # get the folder with all the file sin from the user
    parser = argparse.ArgumentParser(description='Batch copy loads of Business Paper HTML files ')

    parser.add_argument('input', metavar='File path', type=dir_path,
                        help='file path to the folder you would like to recursivly search for html files')

    parser.add_argument('output', metavar='File path', type=dir_path,
                        help='file path to the output folder you would like to save files into.')


    args, unknown = parser.parse_known_args(sys.argv[1:])

    input_folder = args.input
    output_folder = args.output

    # search input filder for patter recursivly
    OP_files = Path(input_folder).glob('**/OP*.htm*')
    fb_files = Path(input_folder).glob('**/fb*.htm*')
    an_files = Path(input_folder).glob('**/an*.htm*')
    ob_files = Path(input_folder).glob('**/ob*.htm*')

    for files_gen in OP_files, fb_files, an_files, ob_files:
        for file in files_gen:
            new_path = Path(output_folder).joinpath(file.name)
            if not new_path.exists():
                shutil.copyfile(file, new_path)
                print('Copied:', file.name)


def dir_path(string):
    if Path(string).is_dir():
        return string
    else:
        raise NotADirectoryError(string)


if __name__ == '__main__':
    main()
