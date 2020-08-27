#!/usr/local/bin/python3

import datetime  # dates etc.
import sys  # parse command line args
from tkinter import messagebox
import os  # file paths etc.
from pathlib import Path

# stuff needed for parsing and manipulating HTML
from lxml import html  # type: ignore
from lxml.etree import SubElement, iselement  # type: ignore

# output file basename
OUTPUTFILE_BASENAME = 'calllist'
FILE_EXTENSION = '.html'

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main():
    if len(sys.argv) != 4:
        # print out help message if we don't get the arguments we want
        print("\nThis script takes 3 arguments.\n",
              " 1:  the path to the HTML file you wish to process.\n",
              " 2:  the path to the template HTML file.\n",
              " 3:  the sitting date in the form YYYY-MM-DD.\n",)
        exit()
    # get the input and template file paths and the prepared date from the user
    # pass user input to transform_xml function
    transform_html(sys.argv[1], sys.argv[2], sys.argv[3])


def transform_html(input_html_file, template_html_file,
                   sitting_date_iso, output_folder=''):

    # template tree
    output_tree = html.parse(template_html_file)
    output_root = output_tree.getroot()

    # input html (from InDesign)
    input_tree = html.parse(input_html_file)
    # InDesign outputs xhtml5 we can convert to html5
    # html.xhtml_to_html(input_tree)
    input_root = input_tree.getroot()


    # expecting the date to be marked up like the below
    # <div id="_idContainer000">
    #   <h1 class="Title" lang="en-US"><strong class="Bold">Issued on:</strong> 21 April at 7.00pm</h1>
    #  </div>
    issued_date = input_root.xpath('//div[@id="_idContainer000"]/h1')
    if len(issued_date) > 0:
        issued_date = issued_date[0]
    if iselement(issued_date):
        issued_date_text = issued_date.text_content()
        issued_date.getparent().remove(issued_date)
    else:
        issued_date_text =''
        warning('Expected to find issued date in the input HTML file. The issued at time will be missing from the bottom of the output HMTML. Check that the InDesign template has not been tampored with.')

    # should return a formatted string in the form 26th April 2017
    # prepared_date = format_date(prepared_date_iso, strftime='%d %b %Y')
    # also get the date in the form YYMMDD for the output file name


    # clean up the HTML
    # convert bullet to square bullet
    for ele in input_root.xpath('.//span[@class="pythonFindBullet"]'):
        if ele.text == '\u2022':
            ele.text = '\u25A0 '

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
            link.set('href', link_href
                     .replace(iD_file_name, '')
                     .replace(iD_file_title, ''))

    # put all the html from the input file into the proper place in the output file
    # get the location in the output_root we want to append to
    append_point = output_root.xpath('//div[@id="content-goes-here"]')
    if len(append_point) < 1:
        print('ERROR: Script can\'t find <div id="content-goes-here"> in the template.'
              ' This is needed as this is where we are going inject html from the input html')
        exit()
    else:
        append_point = append_point[0]


    # change the title to be like
    # <h1 class="mainTitle" id="MainTitleWithDate">
    h1s = input_root.xpath('//h1')
    if len(h1s) < 1:
        print('WARNING: at least one element with a h1 tag was expected. '
              'The title may not appear in the output')
    else:
        h1 = h1s[0]
        h1.set('class', 'mainTitle')
        h1.set('id', 'MainTitleWithDate')
        br = h1.find('br')
        if iselement(br):
            if br.tail:
                br.tail = ' ' + br.tail  # add space
            br.drop_tag()


    # clean up ToC by removing page numbers
    # for element in input_root.xpath('//p[@class="TableOfContents_Toc2"]/a'):
    #     # remove any <br> as uterwise cant remove page numbers from the end
    #     brs = element.findall('.//br')
    #     for br in brs:
    #         br.drop_tag()
    #     span = element.find('span')
    #     if iselement(span):
    #         if span.text:
    #             span.text += ' '
    #         if span.tail:
    #             span.tail = span.tail.rstrip('1234567890')
    #         elif element.text:
    #             element.text = element.text.rstrip('1234567890')

    # remove Indesign toc
    for element in input_root.xpath('//div[contains(@class,"ToC-Box")]'):
        element.drop_tree()


    # sort the numbers (hanging indents etc)
    numbers = input_root.xpath('//p[@class="paraQuestion"]/span[1]')
    for number in numbers:
        # cosider changing this in InDesign
        number.set('class', 'charBallotNumber')
        new_span = html.fromstring('<span style="display : block; float : left; width : 2.1em; height : 1em;"></span>')
        number_parent = number.getparent()
        new_span.append(number)
        number_parent.insert(0, new_span)


    # get the container divs in the input root that contain the html
    container_divs = input_root.xpath('//div[contains(@id,"_idContainer")]')
    for div in container_divs:
        # this line will put all the child elements of the container div in to the output html
        append_point.append(div)

    # change what is in the <title> element in the output
    title_element = output_root.xpath('//title')

    if len(title_element) and iselement(title_element[0]):
        title_element = title_element[0]
        date_formatted = format_date(sitting_date_iso, strftime="%A %d %B %Y")
        if title_element.text:
            title_element.text += f' for {date_formatted}'
        else:
            title_element.text += f'Call List for {date_formatted}'


    # Add IDs and perminant ancors to the html
    # Added at the request of IDMS
    # need to get all the heading elements
    xpath = '//h3[@class="paraBusinessSub-SectionHeading"]'

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


    # find where to put the Toc
    nav_xpath_results = output_root.xpath('//nav[@id="toc"]')

    # create new toc
    h3s = output_root.xpath('//*[contains(@class, "js-toc-content")]//h3')

    if len(nav_xpath_results):
        toc_injection_point = nav_xpath_results[0]
        ol = SubElement(toc_injection_point, 'ol')
        ol.set('class', 'toc-list')
        for h3 in h3s:
            li = SubElement(ol, 'li')
            li.set('class', 'toc-list-item')

            a = SubElement(li, 'a')
            a.set('href', '#' + h3.get('id', ''))
            a.set('class', 'toc-link')
            a.text = h3.text_content()


    # finally change the prepared date at the bottom of the page
    # footerblock = output_root.xpath('//div[@id="footerBlockDate"]/p')
    # if len(footerblock) < 1:
    #     warning('Can\'t find the footer block to append the prepared date to.')
    # elif footerblock[0].text is None:
    #     footerblock[0].text = issued_date_text
    # else:
    #     footerblock[0].text = '{}{}'.format(footerblock[0].text, issued_date_text)

    # get the output file path
    input_file_base_path = os.path.dirname(input_html_file)

    # date in PPU forn
    date_ppu = format_date(sitting_date_iso, strftime='%y%m%d')
    output_file_name = '{}{}{}'.format(OUTPUTFILE_BASENAME, date_ppu, FILE_EXTENSION)
    if output_folder:
        output_file_path = os.path.join(output_folder, output_file_name)
    else:
        output_file_path = os.path.join(input_file_base_path, output_file_name)

    # output the file for writing bytes
    output_tree.write(output_file_path, encoding='UTF-8', method="html", xml_declaration=False)
    # output_file = open(output_file_path, 'wb')
    # output_file.write(html.tostring(output_tree))
    # output_file.close()
    print('Output file path: ', output_file_path, '\n')

    return Path(output_file_path)


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


def warning(msg):

    print(f'{bcolors.WARNING}WARNING:{bcolors.ENDC}  {msg}')
    messagebox.showwarning("Warning", msg)



if __name__ == "__main__": main()
