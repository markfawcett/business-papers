#!/usr/bin/env python3
from shutil import copyfile
from pathlib import Path


def main():

    # where do we want to copy files to
    existing_html_Path = Path(r'C:\Users\fawcettm\projects\business-papers\existingHTML')
    # i gress find a bunch of files that follow a pattern
    for file_Path in Path('.').glob('./200*/200*e01.html'):
        copy_to_Path = existing_html_Path.joinpath(file_Path.name)

        # print(file_Path.resolve())
        # print(file_Path.name)
        print(f'copying: {str(file_Path)} to {str(copy_to_Path)}')

        copyfile(file_Path, copy_to_Path)

if __name__ == '__main__':
    main()
