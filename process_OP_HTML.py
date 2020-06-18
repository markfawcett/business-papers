#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path
# import re
import sys

from lxml import html  # type: ignore
from lxml.html import Element  # type: ignore

import Python_Transforms.Python_Resources.html_chunk_tool_cmd_with_class_warning as script  # type: ignore

table_markup = """<table class="table table-bordered table-responsive-md">
  <thead class="thead-light"><tr><th scope="col">Date</th><th scope="col">New HTML files</th><th scope="col">Original HTML files</th></tr></thead>
  <tbody></tbody>
</table>"""

dist_folder_path = Path('demo/')
if not dist_folder_path.exists():
    print('Error: No demo folder')
    exit()

path_to_index_template = 'index_template.html'
path_to_index_output_path = dist_folder_path.joinpath('index.html')
path_to_index_output_str = str(dist_folder_path.joinpath('index.html'))

existing_base_url = 'https://publications.parliament.uk/pa/cm5801/cmagenda/'


def main():

    # we can except a list of files
    file_paths = sys.argv[1:]

    # also create a table
    html_table = html.fromstring(table_markup)

    for input_file in file_paths:

        # get the sitting_date from the filename
        file_name = Path(input_file).name

        sitting_date = datetime.strptime(file_name, 'OP%y%m%d.html').strftime('%Y-%m-%d')

        creation_date = datetime.now().strftime('%Y-%m-%d')

        # print(sitting_date, creation_date)


        script.DATES.set_up(creation_date, sitting_date)
        input_root = script.massarge_input_file(input_file)
        script.split_and_output(
            input_root,
            'new_op_template.html',
            input_file,
            output_folder=str(dist_folder_path.resolve())
        )

        ob = file_name.replace('OP', 'ob').replace('.html', '.htm')
        an = file_name.replace('OP', 'an').replace('.html', '.htm')
        fb = file_name.replace('OP', 'fb').replace('.html', '.htm')


        new_ob_filename = f'new_{ob}l'
        new_fb_filename = f'new_{fb}l'

        # new_ob_html_filepath = '/business-papers/newHTML/' + new_ob_filename
        # new_fb_html_filepath = '/business-papers/newHTML/' + new_fb_filename
        new_ob_html_filepath = new_ob_filename
        new_fb_html_filepath = new_fb_filename

        row_markup = ('<tr><td>'
                      + script.DATES.sitting_date_long
                      + '</td><td>'
                      f'<a href="{new_ob_html_filepath}">{new_ob_filename}</a><br/>'
                      f'<a href="{new_fb_html_filepath}">{new_fb_filename}</a><br/>'
                      '</td><td>'
                      f'<a href="{existing_base_url}{ob}">{ob}</a><br/>'
                      f'<a href="{existing_base_url}{an}">{an}</a><br/>'
                      f'<a href="{existing_base_url}{fb}">{fb}</a><br/>'
                      '</td></tr>')

        tbody = html_table.find('tbody')
        tbody.append(html.fromstring(row_markup))


    # put the new table in the write place
    html_tree = html.parse(path_to_index_template)
    html_root = html_tree.getroot()

    div = html_root.xpath('//div[@id="op-before-after"]')[0]
    # remove any existing tables
    for table in div.iterfind('table'):
        div.remove(table)
    div.append(html_table)



    html_tree.write(path_to_index_output_str,
                    doctype='<!DOCTYPE html>',
                    encoding='UTF-8',
                    method="html",
                    xml_declaration=False)



if __name__ == "__main__": main()
