#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path
# import re
import sys

from lxml import html  # type: ignore
from lxml.etree import SubElement  # type: ignore
# from lxml.html import Element  # type: ignore

# Order Paper
import html_chunk_tool_cmd_with_class_warning as op  # type: ignore
# Votes and Proceedings
import transform_vnp_html_cmd_v4 as vnp
import transfrom_EDMs_HTML_cmd as edm
import transform_FDO_HTML_cmd as fdo
import CallList_Transform_HTML_cmd as call
from html_table_template import new_table, table_row


dist_folder_path = Path('demo/')
if not dist_folder_path.exists():
    print('Error: No demo folder')
    exit()

path_to_index_template = 'index_template.html'
path_to_index_output_str = str(dist_folder_path.joinpath('index.html'))

# existing base urls for the files as current on publications.parliament
op_base_url = 'https://publications.parliament.uk/pa/cm5801/cmagenda/'
vnp_base_url = 'https://publications.parliament.uk/pa/cm5801/cmvote/'
edm_base_url = 'https://publications.parliament.uk/pa/cm/cmedm/'
fdo_base_url = 'https://publications.parliament.uk/pa/cm/cmfutoral/'
call_base_url = 'https://publications.parliament.uk/pa/cm5801/cmagenda/'


def main():

    # we can accept a list of files
    file_path_strs = sys.argv[1:]

    # create path objects from each of the file path strings passed in
    file_paths = [Path(path_str) for path_str in file_path_strs]

    # need to sort the files into inverse chronological order (date is in filename)
    file_paths.sort(key=lambda x: x.name, reverse=True)

    # need to separate the files into OP and VnP
    vnp_files = []
    op_files = []
    edm_files = []
    fdo_files = []
    call_files = []

    for file_path in file_paths:
        if 'OP' in file_path.name:
            op_files.append(file_path)
        elif 'futoral_' in file_path.name:
            fdo_files.append(file_path)
        elif 'edm' in file_path.name:
            edm_files.append(file_path)
        elif 'calllist' in file_path.name:
            call_files.append(file_path)
        else:
            vnp_files.append(file_path)

    # vnp_table(vnp_files)
    op_table = make_op_table(op_files)
    vnp_table = make_vnp_table(vnp_files)
    call_table = make_call_table(call_files)
    edm_table = make_edm_table(edm_files)
    fdo_table = make_fdo_table(fdo_files)

    # put the new table in the right place
    output_html_tree = html.parse(path_to_index_template)
    output_html_root = output_html_tree.getroot()

    contents_div = output_html_root.find('.//div[@id="contents"]')
    op_div  = output_html_root.find('.//div[@id="op"]')
    vnp_div = output_html_root.find('.//div[@id="vnp"]')
    call_div = output_html_root.find('.//div[@id="calllist"]')
    edm_div = output_html_root.find('.//div[@id="edm"]')
    fdo_div = output_html_root.find('.//div[@id="fdo"]')
    # remove any existing tables
    for div in op_div, vnp_div, edm_table:
        for table in div.iterfind('table'):
            div.remove(table)

    op_div.append(op_table)
    vnp_div.append(vnp_table)
    call_div.append(call_table)
    edm_div.append(edm_table)
    fdo_div.append(fdo_table)

    # put contents in
    ul = SubElement(contents_div, 'ul')
    headings = output_html_root.xpath('//h2')
    for i, heading in enumerate(headings, start=1):
        id_val = f'heading-{i}'
        heading.set('id', id_val)
        li = SubElement(ul, 'li')
        a = SubElement(li, 'a')
        a.set('href', f'#{id_val}')
        a.text = heading.text

    output_html_tree.write(path_to_index_output_str,
                           doctype='<!DOCTYPE html>',
                           encoding='UTF-8',
                           method="html",
                           xml_declaration=False)


def make_call_table(file_paths):
    html_table = new_table()

    for i, input_file in enumerate(file_paths):
        file_name = input_file.name

        'calllist200716'
        date_str = file_name[8:14]

        on_web_file = f'calllist{date_str}v01.html'

        sitting_date = datetime.strptime(date_str, '%y%m%d').strftime('%Y-%m-%d')

        date_long = datetime.strptime(date_str, '%y%m%d').strftime('%A %d %B %Y')

        output_Path = call.transform_html(
            str(input_file), 'pyhonScripts/CallList_template.html',
            sitting_date_iso=sitting_date,
            output_folder=str(dist_folder_path.resolve()))

        row_markup = ('<tr><td>'
                      + date_long
                      + '</td><td>'
                      f'<a href="{output_Path.name}">{output_Path.name}</a><br/>'
                      '</td><td>'
                      f'<a href="{call_base_url}{on_web_file}">{on_web_file}</a><br/>'
                      '</td></tr>')

        tbody = html_table.find('tbody')
        tbody.append(html.fromstring(row_markup))

    return html_table


def make_fdo_table(fdo_file_paths):
    html_table = new_table()

    for i, input_file in enumerate(fdo_file_paths):
        file_name = input_file.name

        if i == 0:
            on_web_file = 'futoral.htm'
        else:
            on_web_file = ''

        sitting_date = datetime.strptime(file_name[8:14], '%y%m%d').strftime('%Y-%m-%d')

        date_long = datetime.strptime(file_name[8:14], '%y%m%d').strftime('%A %d %B %Y')

        output_Path = fdo.html_transform(
            str(input_file), 'pyhonScripts/FDO_template.html',
            published_date=sitting_date,
            prepared_date=sitting_date,
            output_folder=str(dist_folder_path.resolve()))

        row_markup = ('<tr><td>'
                      + date_long
                      + '</td><td>'
                      f'<a href="{output_Path.name}">{output_Path.name}</a><br/>'
                      '</td><td>'
                      f'<a href="{edm_base_url}{on_web_file}">{on_web_file}</a><br/>'
                      '</td></tr>')

        tbody = html_table.find('tbody')
        tbody.append(html.fromstring(row_markup))

    return html_table



def make_edm_table(edm_file_paths):
    # create html table element
    html_table = new_table()

    for input_file in edm_file_paths:
        file_name = input_file.name

        on_web_file = Path(input_file).name[:6] + 'e01.html'

        sitting_date = datetime.strptime(file_name[:6], '%y%m%d').strftime('%Y-%m-%d')

        date_long = datetime.strptime(file_name[:6], '%y%m%d').strftime('%A %d %B %Y')

        output_Path = edm.transform_xml(str(input_file), 'pyhonScripts/EDMs_template.html',
                                        prepared_date_iso=sitting_date,
                                        output_folder=str(dist_folder_path.resolve()))

        row_markup = ('<tr><td>'
                      + date_long
                      + '</td><td>'
                      f'<a href="{output_Path.name}">{output_Path.name}</a><br/>'
                      '</td><td>'
                      f'<a href="{edm_base_url}{on_web_file}">{on_web_file}</a><br/>'
                      '</td></tr>')

        tbody = html_table.find('tbody')
        tbody.append(html.fromstring(row_markup))

    return html_table

def make_vnp_table(vnp_file_paths):

    # create html table element
    html_table = new_table()

    for input_file in vnp_file_paths:
        input_path_str = str(input_file)
        date_str = input_file.name.replace('.html', '')

        # the file name should include the date in the form YYMMDD but lets test that
        try:
            vnp_datetime = datetime.strptime(date_str, '%y%m%d')
        except ValueError:
            print('Error: expected filename to be of the form YYMMDD.html\n  ',
                  '  Instead got:  ', str(input_file),
                  '  skipping...')
            continue

        vnp_template_Path = Path('pyhonScripts/new_VnP_tempate.html').resolve()

        output_Path = vnp.fix_VnP_HTML(input_path_str,
                                       str(vnp_template_Path),
                                       date_str,
                                       output_folder=dist_folder_path.resolve())
        print()

        date_long = vnp_datetime.strftime('%A %d %B %Y')

        on_web_file = input_file.name.replace('.html', 'v01.html')

        row_markup = ('<tr><td>'
                      + date_long
                      + '</td><td>'
                      f'<a href="{output_Path.name}">{output_Path.name}</a><br/>'
                      '</td><td>'
                      f'<a href="{vnp_base_url}{on_web_file}">{on_web_file}</a><br/>'
                      '</td></tr>')

        tbody = html_table.find('tbody')
        tbody.append(html.fromstring(row_markup))

    return html_table


def make_op_table(op_file_paths):

    # also create a table
    html_table = new_table()

    for input_file in op_file_paths:

        # get the sitting_date from the filename
        file_name = input_file.name
        input_file_path_str = str(input_file)

        sitting_date = datetime.strptime(file_name, 'OP%y%m%d.html').strftime('%Y-%m-%d')
        creation_date = datetime.now().strftime('%Y-%m-%d')

        op.DATES.set_up(creation_date, sitting_date)
        input_root = op.massarge_input_file(input_file_path_str)
        op.split_and_output(
            input_root,
            'new_op_template.html',
            input_file_path_str,
            output_folder=str(dist_folder_path.resolve())
        )
        print()

        ob = file_name.replace('OP', 'ob').replace('.html', '.htm')
        an = file_name.replace('OP', 'an').replace('.html', '.htm')
        fb = file_name.replace('OP', 'fb').replace('.html', '.htm')


        new_ob_filename = file_name.replace('OP', 'op')
        # new_fb_filename = f'new_{fb}l'


        new_ob_html_filepath = new_ob_filename
        # new_fb_html_filepath = new_fb_filename


        # row = table_row(
        #     op.DATES.sitting_date_long,
        #     a_element('a', href=new_ob_html_filepath, text=new_ob_filename),
        #     a_element('a', href=new_fb_html_filepath, text=new_fb_filename),
        #     a_element('a', href=op_base_url+ob, text=ob),
        #     a_element('a', href=op_base_url+an, text=an),
        #     a_element('a', href=op_base_url+fb, text=fb)
        # )

        row_markup = ('<tr><td>'
                      + op.DATES.sitting_date_long
                      + '</td><td>'
                      f'<a href="{new_ob_html_filepath}">{new_ob_filename}</a><br/>'
                      '</td><td>'
                      f'<a href="{op_base_url}{ob}">{ob}</a><br/>'
                      f'<a href="{op_base_url}{an}">{an}</a><br/>'
                      f'<a href="{op_base_url}{fb}">{fb}</a><br/>'
                      '</td></tr>')

        tbody = html_table.find('tbody')
        # tbody.append(html.fromstring(row))
        tbody.append(html.fromstring(row_markup))

    return html_table


# def a_element(tag, text=None, href=None, br=False, **kwargs) -> html.Element:
#     a = html.Element(tag, **kwargs)
#     if text:
#         a.text = text
#     if br:
#         a.tail = tail
#     if href:
#         a.set('href', href)
#     return a


if __name__ == "__main__": main()
