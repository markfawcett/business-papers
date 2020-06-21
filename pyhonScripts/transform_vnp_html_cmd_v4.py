#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys
# for parsing and sorting XML
from lxml import html  # type: ignore
from lxml.etree import SubElement, iselement  # type: ignore
# stuff needed for working with file paths
# from os import path
from pathlib import Path
# regular expresions
import re
# for getting todays date
from datetime import date

# golbal variables you may want to change
file_extension = '.html'  # this is added to with the date in a particular form


def main():
    if len(sys.argv) != 4:
        print("\nThis script takes 3 arguments:\n1.\tThe path to the file you want to porces.\n2.\tthe template file name.\n3.\tThe VnP date in the form YYMMDD")
        exit()
    input_file_name    = sys.argv[1]
    template_file_name = sys.argv[2]
    today_string       = sys.argv[3]
    fix_VnP_HTML(input_file_name, template_file_name, today_string=today_string)


def fix_VnP_HTML(input_file_name: str, template_file_name: str,
                 today_string: str='',  output_folder: str='') -> Path:

    # fisrt print the full location of the input file
    print('Input file is at:  {}'.format(Path(input_file_name).resolve()))

    input_root = html.parse(input_file_name).getroot()

    output_tree = html.parse(template_file_name)
    output_root = output_tree.getroot()

    # first get the VnP number from the input
    vnP_number_element = input_root.find('.//div[@class="VnPNumberBox"]/p')
    if iselement(vnP_number_element) and vnP_number_element.text:
        vnP_number = vnP_number_element.text
    else:
        vnP_number = ''
    # print(vnP_number)
    # add this to the ouput
    meta_source = output_root.find('head/meta[@name="Source"]')
    if iselement(meta_source) and 'content' in meta_source.attrib:
        meta_source.attrib['content'] += ' ' + vnP_number
    title_element = output_root.find('head/title')
    if iselement(title_element) and title_element.text:
        title_element.text += ' ' + vnP_number + ')'
    issueNumberParra = output_root.find('.//p[@class="VPIssueNumber"]')
    if iselement(issueNumberParra):
        issueNumberParra.text = vnP_number

    # now get the date from the input
    date_element = input_root.find('.//*[@class="DateTitle"]')
    if date_element is not None and date_element.text:
        vnP_day_of_week = date_element.text.split(' ', 1)[0]
        vnP_date = date_element.text.split(' ', 1)[1]
    else:
        vnP_day_of_week = 'Noday'
        vnP_date = 'Num Month Year'
    # add this to the output
    h1_title = output_root.find('.//h1[@id="MainTitleWithDate"]')
    if h1_title is not None:
        h1_title.text = 'Votes and Proceedings'
        SubElement(h1_title, 'br').tail = f'{vnP_day_of_week} {vnP_date}'
    # also add the date to the botttom of the page
    prepared_date_element = output_root.find('.//div[@id="footerBlockDate"]/p')
    if prepared_date_element is not None and prepared_date_element.text:
        prepared_date_element.text += vnP_date

    # change the input root so that all the paragraphs with numbered spans have another span
    spans = input_root.findall('.//p[@class="numbered InDesignBold"]/span[last()]')
    # print(spans)
    for span in spans:
        if span.tail:
            temp_text = span.tail
        else:
            temp_text = ''
        span.tail = None
        span_parent_para = span.getparent()
        span_parent_para.append(html.fromstring('<span class="text">' + temp_text + '</span>'))

    # Add IDs and perminant ancors to the html
    # Added at the request of IDMS
    # need to get all the heading elements
    xpath = '//*[@class="numbered InDesignBold"]/span[@class="text"]|//h2[@class="underline"]'
    linkables = input_root.xpath(xpath)
    # print(len(linkables))
    for i, heading in enumerate(linkables):
        # generate id text
        id_text = f'anchor-{i}'

        if heading.get('id', default=None):
            heading.set('name', heading.get('id'))

        heading.set('id', id_text)

        # adding this will add the anchor to the last span
        spans = heading.xpath('./span[normalize-space(text())]|./strong[normalize-space(text())]')
        if len(spans) > 1:
            heading = spans[-1]

        anchor = SubElement(heading, 'a')
        permalink_for = 'Permalink for ' + heading.text_content()
        anchor.set('href', '#' + id_text)
        anchor.set('aria-label', 'Anchor')
        anchor.set('title', permalink_for)
        anchor.set('data-anchor-icon', '§')
        anchor.set('class', 'anchor-link')

    # get a handle in the output root for appending stuff from the input
    append_point = output_root.find('.//div[@id="mainTextBlock"]')
    # append_point.append(html.fromstring('<p class="VPIssueNumber">' + vnP_number + '</p>'))
    if append_point is None:
        input('Error: The template root does not have a div with an id of "mainTextBlock" '
              'so the script does not know where to put the elements from the input')
        exit()

    # put the main text flow into the output
    main_text_flow_element = input_root.find('.//div[@class="MainTextFlow"]')
    append_point.extend(main_text_flow_element)

    if today_string is None:
        output_file_name = get_date_short() + file_extension
    else:
        output_file_name = today_string + file_extension
    output_file_name = f'vnp{output_file_name}'

    if output_folder:
        output_file_path = Path(output_folder).joinpath(output_file_name)
    else:
        # output_file_path = path.join(base_path, output_file_name)
        output_file_path = Path(input_file_name).parent.joinpath(output_file_name)

    output_tree.write(str(output_file_path), encoding='UTF-8', method="html", xml_declaration=False)
    print(f'Output file is at: {output_file_path.resolve()}')
    return output_file_path


def do_find_n_replaces(string):
    string = re.sub(r'>  +', '>', string)
    string = re.sub(r'  +<', '<', string)
    string = string.replace('&amp;amp;nbsp;', ' ')
    return string


def delete_element(element):
    if iselement(element):
        element.getparent().remove(element)


def get_date_short():
    # get a date object for today
    today = date.today()
    # date string in the form 170627
    today_string = today.strftime('%y%m%d')
    return today_string


if __name__ == "__main__": main()
