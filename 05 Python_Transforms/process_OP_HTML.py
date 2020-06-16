#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path
# import re
import sys

# from lxml import html  # type: ignore

import Python_Resources.html_chunk_tool_cmd_with_class_warning as script


def main():

    # we can except a list of files
    file_paths = sys.argv[1:]

    for input_file in file_paths:

        # input_html_tree = html.parse(input_file)
        # input_html = input_html_tree.getroot()

        # title = input_html.xpath('//p[@class="DocumentTitle"]')[0]
        # title_text = title.text_content()

        # match = re.search(r'(?<=Order Paper No.) ?\d\d?\d?', title_text)

        # if match:
        #     print(match.group(0))

        # get the sitting_date from the filename
        file_name = Path(input_file).name

        sitting_date = datetime.strptime(file_name, 'OP%y%m%d.html').strftime('%Y-%m-%d')

        creation_date = datetime.now().strftime('%Y-%m-%d')

        # print(sitting_date, creation_date)


        script.DATES.set_up(creation_date, sitting_date)
        input_root = script.massarge_input_file(input_file)
        script.split_and_output(input_root, '/Users/mark/projects/business-papers/new_op_template.html', input_file)


if __name__ == "__main__": main()
