#!/usr/local/bin/python3

import datetime  # dates etc.
from tkinter import messagebox
import sys  # parse command line args
import os  # file paths etc.
from pathlib import Path

# stuff needed for parsing and manipulating HTML
from lxml import html  # type: ignore
from lxml.etree import SubElement  # type: ignore

# output file basename
# outputfile_basename = 'edm_daily_'
file_extension = '.htm'


def main():
    # Fixes for Windows
    if os.name == "nt":
        from ctypes import windll
        try:
            # add ASCII color support to cmd prompt
            kernel32 = windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except: pass

    if len(sys.argv) != 4:
        # print out help message if we don't get the arguments we want
        print("\nThis script takes 3 arguments.",
              " 1:  the path to the HTML file you wish to process.",
              " 2:  the path to the template HTML file.",
              " 3:  the prepared date in the form YYYY-MM-DD.", sep='\n')
        exit()
    # get the input and template file paths and the prepared date from the user
    # pass user input to transform_xml function
    transform_xml(sys.argv[1], sys.argv[2], sys.argv[3])


def transform_xml(input_html_file, template_html_file,
                  prepared_date_iso: str, output_folder: str = '') -> Path:

    # should return a formatted string in the form 26th April 2017
    prepared_date = format_date(prepared_date_iso, strftime='%d %b %Y')
    # also get the date in the form YYMMDD for the output file name

    # template tree
    output_tree = html.parse(template_html_file)
    output_root = output_tree.getroot()

    # input html (from InDesign)
    input_tree = html.parse(input_html_file)
    # InDesign outputs xhtml5 we can convert to html5
    # html.xhtml_to_html(input_tree)
    input_root = input_tree.getroot()

    # clean up the HTML
    # convert bullet to square bullet
    # for ele in input_root.xpath('.//span[@class="pythonFindBullet"]'):
    #     if ele.text:
    #         ele.text = ele.text.replace('\u2022', '\u25A0 ')

    # remove filename for internal hyperlinks
    # e.g. href="cmsilist2.html#_idTextAnchor000" -> href="#_idTextAnchor000"
    # usualy filename before #
    iD_file_name = os.path.basename(input_html_file)
    # but sometimes people change the filename but the original filename is in the <title>
    iD_file_title = input_root.findtext('head/title', default='')
    if iD_file_title != '':
        iD_file_title = '{}.html'.format(iD_file_title)

    all_links = input_root.xpath('//a')
    for link in all_links:
        link_href = link.get('href', default=None)
        if link_href:
            link.set(
                'href',
                link_href
                .replace(iD_file_name, '')
                .replace(iD_file_title, '')
            )
    # eddit the class on the main title
    main_heading = input_root.xpath('//h1[@class="Heading1"][1]')
    if len(main_heading) > 0:
        main_heading[0].set('class', 'mainTitle')
        # main_heading_strong = main_heading[0].find('strong')
        # if main_heading_strong is not None:
        #     if main_heading_strong.get('class', default=None) == 'Bold':
        #         main_heading_strong.pop('class')
        #     if main_heading_strong.tail:
        #         span_published = SubElement(main_heading[0], 'span')
        #         span_published.set('id', 'publishedDate')
        #         span_published.text = main_heading_strong.tail
        #         main_heading_strong.tail = ''

    # change p.Half-line-after to hr.Half-line-after
    for half_line in input_root.xpath('//p[@class="Half-line-after"]'):
        half_line.text = None
        half_line.tag = 'hr'

    # remove full line after
    for full_line in input_root.xpath('//p[@class="Line-After-Full-Longer"]'):
        full_line.getparent().remove(full_line)

    # sort motion sponsor groups
    sponsor_groups_xpath = '//p[@class="Motion-Sponsor-Group"]' \
                           '|//p[@class="Motion-Sponsor-Group-Indent1"]'
    sponsor_groups = input_root.xpath(sponsor_groups_xpath)
    for sponsor_group in sponsor_groups:
        if not sponsor_group.text:
            continue
        sponsor_group.classes.add('row')
        # split text on the tab character (InDesign puts in)
        sponsor_group.text = sponsor_group.text.replace('\u0009', '\t')
        sponosr_names = sponsor_group.text.split('\t')
        # print('sponosr_names len: ', len(sponosr_names))
        sponsor_group.text = None
        for sponosr_name in sponosr_names:
            sponsor_span = SubElement(sponsor_group, 'span')
            sponsor_span.classes.update(('col-12', 'col-sm-6', 'col-lg-4'))
            sponsor_span.text = sponosr_name
        # if sponsor_group.text:
        #     # split text on the tab character
        #     sponosr_names = sponsor_group.text.split('\t')
        #     sponsor_group.text = None
        #     for sponosr_name in sponosr_names:
        #         if sponosr_name == '':
        #             continue
        #         sponsor_span = SubElement(sponsor_group, 'span')
        #         sponsor_span.set('class', 'signatory')
        #         sponsor_span.text = sponosr_name
        #         sponsor_group.append(sponsor_span)

    # remove unnessesary UIN elements
    xpath = '//*[@class="UIN"]'
    for uin_span in input_root.xpath(xpath):
        if not uin_span.text_content() or uin_span.text.isspace():
            uin_span.drop_tree()

    # collapse roman and uin spans
    xpath = '//span[@class="Roman"]/span[@class="UIN"]'
    for span in input_root.xpath(xpath):
        span.getparent().classes.add('UIN')
        span.drop_tag()

    # put all the html from the input file into the proper place in the output file
    # get the location in the output_root we want to append to
    append_point = output_root.xpath('//div[@id="content-goes-here"]')
    if len(append_point) < 1:
        show_error('Script can\'t find <div id="content-goes-here"> in the template.'
                   ' This is needed as this is where we are going inject html from the input html')
        exit()
    else:
        append_point = append_point[0]

    # get the container divs in the input root that contain the html
    container_divs = input_root.xpath('//div[contains(@id,"_idContainer")]')
    for div in container_divs:
        # this line will put all the child elements of the container div into the output html
        append_point.append(div)


    # Add IDs and perminant ancors to the html
    # Added at the request of IDMS
    # need to get all the heading elements
    xpath = '//h2[@class="underline"]|' \
            '//h3[@class="EDMTitle"]'

    headings = output_root.xpath(xpath)
    for i, heading in enumerate(headings):
        # generate id text
        id_text = f'anchor-{i}'

        if heading.get('id', default=None):
            heading.set('name', heading.get('id'))

        heading.set('id', id_text)

        anchor = SubElement(heading, 'a')
        permalink_for = 'Permalink for ' + heading.text_content()
        anchor.set('href', '#' + id_text)
        anchor.set('aria-label', 'Anchor')
        anchor.set('title', permalink_for)
        anchor.set('data-anchor-icon', '§')
        anchor.set('class', 'anchor-link')


    # create the tables of contents
    # This will be overridden by tocbot.
    # We still want a ToC even if JavaScript is dissabled...

    # find where to put the Toc
    nav_xpath_results = output_root.xpath('//nav[@id="toc"]')


    # look for all the h2's
    # // Where to grab the headings to build the table of contents.
    # contentSelector: '.js-toc-content'
    h2s = output_root.xpath('//h2[@class="underline"]')

    if len(nav_xpath_results):
        toc_injection_point = nav_xpath_results[0]
        ol = SubElement(toc_injection_point, 'ol')
        ol.set('class', 'toc-list')
        for h2 in h2s:
            li = SubElement(ol, 'li')
            li.set('class', 'toc-list-item')

            a = SubElement(li, 'a')
            a.set('href', '#' + h2.get('id', ''))
            a.set('class', 'toc-link')
            a.text = h2.text_content()
    else:
        print('no element')

    # finally change the prepared date at the bottom of the page
    footerblock = output_root.xpath('//div[@id="footerBlockDate"]/p')
    if len(footerblock) < 1:
        print('WARNING:  Can\'t find the footer block to append the prepared date to.')
    elif footerblock[0].text is None:
        footerblock[0].text = prepared_date
    else:
        footerblock[0].text = '{}{}'.format(footerblock[0].text, prepared_date)

    # get the output file path
    # input_file_base_path = os.path.dirname(input_html_file)
    # output_file_path = os.path.join(
    #     input_file_base_path,
    #     '{}{}'.format(outputfile_basename, file_extension)
    # )

    # overwrite the input html file

    output_file_name = datetime.datetime.strptime(prepared_date_iso, '%Y-%m-%d').strftime('%y%m%d')

    output_file_name = 'edm' + output_file_name + '.html'

    if output_folder:
        output_file_Path = Path(output_folder).joinpath(output_file_name)
    else:
        # output_file_Path = path.join(base_path, output_file_name)
        output_file_Path = Path(input_html_file).parent.joinpath(output_file_name)

    output_tree.write(str(output_file_Path.resolve()),
                      doctype='<!DOCTYPE html>',
                      encoding='UTF-8',
                      method="html",
                      xml_declaration=False)

    print('Output file path: ', output_file_Path.resolve(), '\n')

    return output_file_Path


def to_date_obj(date_time_string, current_format='%Y-%m-%d', default=''):
    """
    Takes a string representing a datetime in MNIS data and returns it
    as a datetime.date.
    """
    if date_time_string == '':
        print('Problem with Date')
        return default
    else:
        convertedDate = datetime.datetime.strptime(date_time_string, current_format).date()
        # print('convertMnisDatetime', convertedDate)
        return convertedDate


def format_date(date_time_string, strftime='%d %b %Y', current_format='%Y-%m-%d', default=''):
    date = to_date_obj(date_time_string, current_format=current_format, default=default)
    try:
        return date.strftime(strftime)
    except AttributeError:
        print('Problem with Date')
        return default


def show_error(error_text):
    error_text = 'ERROR: ' + error_text
    print('\033[91m' + error_text + '\033[0m')
    # messagebox.showerror('ERROR', error_text)


if __name__ == "__main__": main()
