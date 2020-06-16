#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys
# module for dates
from datetime import date
import difflib
# deep copy stuff
from copy import deepcopy
# stuff needed for parsing and manipulating HTML (or XML)
from lxml import html  # type: ignore
from lxml.html import Element  # type: ignore
from lxml.etree import SubElement  # type: ignore
# stuff for file paths
import os
# for regular expresions
import re

# some variables used throughout
doctype = '<!DOCTYPE html>'
xml_declaration        = ''
location_of_button_gif = '/images/OP%20button.gif'
fileextension          = '.html'



class DATES:
    # variables for the dates used

    sitting_date_long          = ""   # in the form, 'Monday 12 September 2016'
    sitting_date_medium        = ""   # e.g. 12 September 2016
    sitting_date_compact       = ""   # 20160912
    sitting_date_super_compact = ""   # 160912
    creation_date_medium       = ""   # 11 September 2016

    @classmethod
    def set_up(cls, creation_date, sitting_date):
        # sitting date in the form 20160912

        cls.sitting_date_compact = sitting_date.replace('-', '')
        cls.sitting_date_super_compact = cls.sitting_date_compact[2:]

        # make a python date new_objects for sitting and creation dates
        sitting_date  = sitting_date.split('-')
        sitting_date  = date(int(sitting_date[0]), int(sitting_date[1]), int(sitting_date[2]))
        creation_date = creation_date.split('-')
        creation_date = date(int(creation_date[0]), int(creation_date[1]), int(creation_date[2]))

        # siting date in the form Monday 12 September 2016
        cls.sitting_date_long    = sitting_date.strftime('%A %d %B %Y')

        # sitting date in the form 12 September 2016
        cls.sitting_date_medium  = sitting_date.strftime('%d %B %Y')

        # creation date in the form 11 September 2016
        cls.creation_date_medium = creation_date.strftime('%d %B %Y')


def main():
    """Usage: inputfile templatefile sittingdate creationdate OPnumber"""
    if len(sys.argv) != 6:
        print("\nThis script takes 5 arguments.",
              " 1:  the path to the file you wish to process.",
              " 2:  the path to the template file.",
              " 3:  the sitting date in the form YYYY-MM-DD, e.g.'2016-09-12'",
              " 4:  the creation date in the form YYYY-MM-DD, e.g.'2016-09-11'",
              " 5:  the Order paper number, e.g. '32'\n",
              "Full example: 'outputFromInDesign.html EBtemplate.html 2016-09-12 2016-09-11 32'\n",
              sep='\n')
        exit()
    input_file_name    = sys.argv[1]
    template_file_name = sys.argv[2]
    sitting_date       = sys.argv[3]
    creation_date      = sys.argv[4]
    op_number          = sys.argv[5]

    DATES.set_up(creation_date, sitting_date)
    input_root = massarge_input_file(input_file_name)
    split_and_output(input_root, template_file_name, input_file_name)

    print('Done!')


# try and find any bad classes
def bad_classes(input_file_name):
    # import allowed classes
    try:
        from classesInOPHtml import ALLOWED_CLASSES as allowed_classes  # type: ignore
    except ModuleNotFoundError:
        try:
            from Python_Resources.classesInOPHtml import ALLOWED_CLASSES as allowed_classes
        except:
            show_error('Can\'t seem to find classesInOPHtml.py'
                       ' html classes will not be checked.')
            return

    input_root = html.parse(input_file_name).getroot()

    classes_list = input_root.xpath('//*/@class')  # should return a list of strings

    # empty set for classes to be put in.
    # class_with_space = set()
    definatly_wrong_class = set()

    for item in classes_list:
        # we are only interested in `class` with spaces
        if ' ' in item:
            # class_with_space.add(item)

            bad_class = ''
            classes = item.split(' ')
            for sub_class in classes:
                if sub_class not in allowed_classes:
                    bad_class += ' ' + sub_class

            # then make the class one again
            bad_class = bad_class.strip()

            if bad_class:
                definatly_wrong_class.add(bad_class)

    if definatly_wrong_class:
        show_error('Looks like there are invalid classes in the HTML. This requires some human wisdom to fix.')

    for item in definatly_wrong_class:
        if item:
            print('  ' + item + ' looks like an invalid class...')

            close_matches = difflib.get_close_matches(item, allowed_classes, n=1)
            if len(close_matches) == 1:
                print('    suggestion  \033[1m' + item + ' -> ' + close_matches[0] + '\033[0m')

    print()



def massarge_input_file(input_file_name):
    # test for bad classes
    try:
        bad_classes(input_file_name)
    except:
        # we dont reall NEED to chaeck for bad classes so wond do anything here
        show_error('There was a prnew_oblem when checking for bad classes.')

    input_root = html.parse(input_file_name).getroot()
    # remove the contents div
    contents_div = input_root.xpath('body/div[@class="Contents-Box"]')
    if len(contents_div) > 0:
        contents_div[0].getparent().remove(contents_div[0])
    # remove all the _idGenParaOverrides
    all_paragraphs = input_root.xpath('//p|//h1|//h2|//h3|//h4|//h5|//h6')
    for paragraph in all_paragraphs:
        if re.search(r' ?_idGenParraOveride\d\d?\d?', paragraph.get('class', default='')) is not None:
            print('override')
            paragraph.set('class', re.sub(r' ?_idGenParraOveride\d\d?\d?', '', paragraph.get('class', default='')))
    # remove filename for internal hyperlinks
    inDesign_file_name = os.path.basename(input_file_name)
    all_links = input_root.xpath('//a')
    for link in all_links:
        if 'href' in link.attrib:
            link.attrib['href'] = link.attrib['href'].replace(inDesign_file_name, '')

    # there are 3 paragraph style with hanging indednts that must be manipulated
    for paragraph in input_root.xpath(
            '//p[@class="paraMotionSub-Paragraph" or '
            '@class="paraMotionSub-Sub-Paragraph" or '
            '@class="paraMotionSub-Sub-Sub-Paragraph"][text()]'):
        try:
            split_on_tab = paragraph.text.split('\u0009', 1)
            span_hanging = Element('span')
            span_hanging.set('class', 'hanging1')
            span_hanging.tail = split_on_tab[1]
            span_hanging.text = split_on_tab[0]
            paragraph.append(span_hanging)
            paragraph.text = ''
        except IndexError:
            # dont do anything if there is no tab
            pass
    # add span to beginning of all business headings
    # dark_gray_headings = input_root.xpath('//*[@class="paraBusinessTodayChamberHeading"]')
    # for gray_heading in dark_gray_headings:
    #     gray_heading.append(html.fromstring('<span style="display : block; float : left; width : 4.7%; height : 1em;">&nbsp;</span>'))
    # light_gray_headings = input_root.xpath('//*[@class="paraBusinessSub-SectionHeading"]')
    # for light_gray_heading in light_gray_headings:
    #     light_gray_heading.append(html.fromstring('<span style="display : block; float : left; width : 1.2%; height : 1em;">&nbsp;</span>'))
    # sort out all the bullets
    bullets = input_root.xpath('//span[@class="pythonFindBullet"]')
    for bullet in bullets:
        bullet.text = ""
        # bullet.attrib['style'] = 'display : block; float : left; width : 2.1em; height : 1em;'
        bullet.attrib.pop('class', None)  # None means dont error if class not there
        # change the alt attrib to "" for accessability (it will be ignored by screen readers if
        # the alt attrib is present but null).
        # Could also use, role="presentation" but not as well supported
        # bullet.append(html.fromstring('<img alt="" src="' + location_of_button_gif + '" style="display : inline; margin : 0;">'))
        # also turn the strong to a span. This is for FBA where there are tabs between the time and the rest.
        next_strong_t = bullet.getnext()
        if next_strong_t is not None and next_strong_t.tag == 'strong':
            # now check that there is a bold class and the next char is a tab
            if next_strong_t.get('class') == 'Bold' and next_strong_t.tail is not None and next_strong_t.tail[0] == '\u0009':
                next_strong_t.tag = 'span'
                # next_strong_t.attrib.pop('class', None)
                # next_strong_t.attrib['style'] = 'display : block; float : left; width : 5.7em; height : 1em;'
    # sort the numbers
    numbers = input_root.xpath('//p[@class="paraQuestion"]/span[1]')
    for number in numbers:
        # cosider changing this in InDesign
        number.attrib['class'] = 'charBallotNumber'
        new_span = Element('span')
        new_span.classes.add('number-span')
        # new_span = html.fromstring('<span style="display : block; float : left; width : 2.1em; height : 1em;"></span>')
        number_parent = number.getparent()
        new_span.append(number)
        number_parent.insert(0, new_span)
    # sort ministerial statements
    statements = input_root.xpath('//p[@class="paraMinisterialStatement"]/span[1]')
    for statement in statements:
        statement.attrib['class'] = 'charItemNumber'
        statement_tail_text = statement.tail
        statement.tail = ''
        new_span = Element('span')
        new_span.classes.add('number-span')
        # new_span = html.fromstring('<span style="display : block; float : left; width : 2.1em; height : 1em;"></span>')
        new_span.tail = statement_tail_text
        number_parent = statement.getparent()
        new_span.append(statement)
        number_parent.insert(0, new_span)
    # sort the front page tables
    front_page_tables = input_root.xpath('//table[@class="Front-Page-Table"]')
    for table in front_page_tables:
        # added as a result of an accessibility audit
        table.set('role', 'presentation')
    front_page_table_colgroups = input_root.xpath('//table[@class="Front-Page-Table"]/colgroup')
    for colgroup in front_page_table_colgroups:
        colgroup[0].attrib.pop("class", None)  # None means dont error if class not there
        colgroup[0].attrib['width'] = '24%'
        colgroup[1].attrib.pop("class", None)
        colgroup[1].attrib['width'] = '76%'

    # sort motion sponsor groups
    sponsor_groups_xpath = '//p[@class="paraMotionSponsorGroup"]' \
                           '|//p[@class="MotionAmmendmentSponsorGroup"]' \
                           '|//p[@class="MotionAmmendmentSponsorGroup"]/span' \
                           '|//p[@class="A2A-SponsorGroup"]'
    sponsor_groups = input_root.xpath(sponsor_groups_xpath)
    for sponsor_group in sponsor_groups:
        # print(html.tostring(sponsor_group))
        if not sponsor_group.text:
            continue
        # split text on the tab character
        sponosr_names = sponsor_group.text.split('\u0009')
        sponsor_group.text = None
        for sponosr_name in sponosr_names:
            sponsor_span = SubElement(sponsor_group, 'span')
            sponsor_span.classes.add('sponsor-span')
            sponsor_span.text = sponosr_name


    # Add IDs and perminant ancors to the html
    # Added at the request of IDMS
    # need to get all the heading elements
    xpath = '//h1|//h2|//h3|//h4|//h5|//h6|//*[@class="paraBusinessItemHeading"]|//*[@class="paraBusinessItemHeading-bulleted"]|//*[@class="FbaLocation"]'
    headings = input_root.xpath(xpath)
    for i, heading in enumerate(headings):
        # generate id text
        id_text = f'{DATES.sitting_date_compact}-{i}'

        if heading.get('id', default=None):
            heading.set('name', heading.get('id'))

        heading.set('id', id_text)
        # parmalink_span = SubElement(heading, 'span')
        # parmalink_span.set('class', 'perma-link')
        # anchor = SubElement(parmalink_span, 'a')
        anchor = SubElement(heading, 'a')
        permalink_for = 'Permalink for ' + heading.text_content()
        anchor.set('href', '#' + id_text)
        anchor.set('aria-label', 'Anchor')
        anchor.set('title', permalink_for)
        anchor.set('data-anchor-icon', '§')
        anchor.set('class', 'anchor-link')
        # SubElement(anchor, 'span').text = '§'


    # return the modified input html root element
    return input_root


def split_and_output(input_root, template_file_name, input_file_name):
    output_root = html.parse(template_file_name).getroot()
    # put element lists in dict with file_lable as the key
    file_lables_element_lists = {'new_ob': [], 'new_fb': [], 'an': []}
    # select all the paragraphs etc within the top levle divs
    paragraph_elements = input_root.xpath('//body/div/*')
    list_to_add_to = file_lables_element_lists['new_ob']
    # look through all the paragraph elemets and find out if any are Annoncements etc
    for paragraph_element in paragraph_elements:
        # if (paragraph_element.get('class') == 'paraBusinessTodayChamberHeading' and
        #    (paragraph_element.text is not None and paragraph_element.text.upper().strip() == 'ANNOUNCEMENTS') or
        #    (len(paragraph_element) != 0 and paragraph_element[0].tail is not None and
        #    paragraph_element[0].tail.upper().strip() == 'ANNOUNCEMENTS')):
        #     # start new list for announcements
        #     list_to_add_to = file_lables_element_lists['an']
        if paragraph_element.get('class') == 'DocumentTitle' and 'PART 2' in html.tostring(paragraph_element).decode(encoding='UTF-8').upper():
            # start new list for future business
            list_to_add_to = file_lables_element_lists['new_fb']
        list_to_add_to.append(paragraph_element)

    # build up output trees
    for file_lable, element_list in file_lables_element_lists.items():
        if len(element_list) != 0:
            # make the filename from the label and the sittig date compact
            filename = file_lable + DATES.sitting_date_super_compact + fileextension
            # copy the template tree and add elements needed for this section
            temp_output_root = deepcopy(output_root)
            # sort out things in the head section
            # temp_output_root.xpath('//head/meta[@name="Date"]')[0].attrib['content'] = DATES.creation_date_medium
            # temp_output_root.xpath('//head/meta[@name="Identifier"]')[0].attrib['content'] = 'Filename: ' + filename
            # change the title
            if file_lable == 'new_ob':
                title_text = 'Order Paper for ' + DATES.sitting_date_medium
                h1_text = 'Order Paper for ' + DATES.sitting_date_long
            elif file_lable == 'new_fb':
                title_text = 'Future Business as of ' + DATES.sitting_date_medium
                h1_text = 'Future Business as of ' + DATES.sitting_date_long
            temp_output_root.xpath('//h1[@id="mainTitle"]')[0].text = h1_text
            temp_output_root.xpath('//head/title')[0].text = title_text
            # get the position (in the template) where we will inject html (from the input)
            code_injection_point = temp_output_root.xpath('//div[@id="content-goes-here"]')[0]
            for element in element_list:
                # remove the docuemnt headings from the html i.e. part 1 head
                if element.get('class', default=None) == 'DocumentTitle':
                    continue
                code_injection_point.append(element)

            # Add IDs to Future business
            # Added at the request of IDMS
            # if file_lable == 'fb':
            #     # get all elements with the class 'paraBusinessItemHeading'
            #     xpath = '*[@class="paraBusinessItemHeading"]/span'
            #     paraBusinessItemHeadings = code_injection_point.xpath(xpath)
            #     for span_element in paraBusinessItemHeadings:
            #         span_text = span_element.text
            #         if span_text:
            #             paragraph_element = span_element.getparent()
            #             number_text = 'FBB-' + span_text.strip().strip('.')
            #             paragraph_element.set('id', number_text)

            # write out the output html files
            outputfile_name = os.path.join(os.path.dirname(input_file_name),
                                           file_lable + DATES.sitting_date_compact[2:] + fileextension)
            outputfile = open(outputfile_name, 'w')
            outputfile.write(xml_declaration + '\n' + doctype + '\n')
            outputfile.write(html.tostring(temp_output_root).decode(encoding='UTF-8'))
            print(file_lable + ' file is at:\t' + outputfile_name)


def show_error(error_text):
    error_text = '\nWARNING: ' + error_text
    print('\033[91m' + error_text + '\033[0m')



if __name__ == "__main__": main()
