#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys
# module for dates
from datetime import date
# stuff needed for parsing and manipulating HTML (or XML)
from lxml import html, etree
# work with file paths
from os import path
# regex module
import re

# some variables used throughout
xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
fileextension   = '_ord.xml'


def split_and_output(input_file_name, sitting_date):
    # get the date in the form 30 March
    sitting_date  = sitting_date.split('-')
    sitting_date  = date(int(sitting_date[0]), int(sitting_date[1]), int(sitting_date[2]))
    sitting_date_formatted  = sitting_date.strftime('%d %B')
    input_root = html.parse(input_file_name).getroot()
    output_root = etree.fromstring('<op></op>')
    date_element = etree.Element('Date')
    date_element.text = sitting_date_formatted
    output_root.append(date_element)
    # put element lists in dict with file_lable as the key
    # get the div containing paraBusinessTodayChamberHeading
    paragraph_elements = input_root.xpath('//body/div/*')

    # look through all the paragraphs and put all the paragraphs under business of the day into a new list
    # stop when we get to a new heading 1 gray (aka paraBusinessTodayChamberHeading)
    bus_of_day_paras = []
    in_bus_of_day = False
    for paragraph in paragraph_elements:
        if paragraph.get('class') == 'paraBusinessSub-SectionHeading' and paragraph.text_content().upper().strip() == 'BUSINESS OF THE DAY':
            in_bus_of_day = True
        # break out of the loop after as soon as we get to a heading 1 gray paragraph
        if in_bus_of_day is True and paragraph.get('class') == 'paraBusinessTodayChamberHeading':
            break
        if in_bus_of_day is True:
            bus_of_day_paras.append(paragraph)

    # print(paragraph_elements)

    # look through all the paragraph elemets and find out if any are Annoncements etc
    for i in range(len(bus_of_day_paras)):
        # create Item element
        item = etree.Element('Item')
        if bus_of_day_paras[i].get('class') in ('paraBusinessItemHeading', 'BulletedCaps'):
            # get the text content
            title_text = bus_of_day_paras[i].text_content()
            # remove the number from the begining it it exitsts
            # test if title has number
            if title_text.split('.')[0].isdigit():
                number = etree.Element('Number')
                number.text = title_text.split('.')[0]
                item.append(number)
            # create OrderTitle elements
            order_title_element = etree.fromstring('<OrderTitle>{}</OrderTitle>'.format(
                re.sub(r'^\d+\. ', '', bus_of_day_paras[i].text_content())
            ))
            # append this element
            item.append(order_title_element)
            # find text elements
            number_text = ''
            # how many elements are left in the list
            j = len(bus_of_day_paras) - i
            text = etree.Element('Text')
            for k in range(j - 1):
                current_class = bus_of_day_paras[k + i + 1].get('class')
                #  include ammendment paras (NormalIndented) suspect they might not be needed
                if current_class in ('Normal', 'paraMotionNumberedParagraph', 'paraMotionText', 'SubNumberedPara', 'NumberedParaEmpty', 'NormalIndented'):
                    if current_class != 'NumberedParaEmpty':

                        text.append(etree.fromstring(
                            '<p>{}{}</p>'.format(number_text, bus_of_day_paras[k + i + 1].text_content())
                        ))
                        number_text = ''
                    else:
                        number_text = bus_of_day_paras[k + i + 1].text_content()
                    # print(etree.tostring(text))
                    item.append(text)
                if current_class in ('paraBusinessItemHeading', 'paraBusinessSub-SectionHeading'):
                    break
            # append item to op
            output_root.append(item)

        # Ensure any public petitions are added
        if bus_of_day_paras[i].text_content().upper() in ('PRESENTATION OF PUBLIC PETITIONS', 'PUBLIC PETITIONS'):
            order_title_element = etree.Element('OrderTitle')
            order_title_element.text = bus_of_day_paras[i].text_content()
            item.append(order_title_element)

            if bus_of_day_paras[i + 2].get('class') == 'paraBusinessListItem':
                text = etree.Element('Text')
                p_ele = etree.Element('p')
                p_ele.text = bus_of_day_paras[i + 2].text_content().replace('\u2022', '')
                text.append(p_ele)
                item.append(text)

            output_root.append(item)


        # Now ensure that adjournment debate is added.
        if bus_of_day_paras[i].text_content().upper() in ('ADJOURNMENT DEBATE', 'ADJOURNMENT'):
            # get the text content
            title_text = bus_of_day_paras[i].text_content()
            title_text = title_text.replace('ADJOURNMENT DEBATE', 'ADJOURNMENT')
            order_title_element = etree.Element('OrderTitle')
            order_title_element.text = title_text
            item.append(order_title_element)


            if i + 2 < len(bus_of_day_paras) and bus_of_day_paras[i + 2].get('class') == 'paraBusinessListItem':
                # get the text content of the span. The span is the first child so [0]
                span_tag = bus_of_day_paras[i + 2][0]
                # get the tail text of the span
                tail_text = span_tag.tail
                # print(bus_of_day_paras[k + i + 1].text_content())
                text = etree.Element('DebateTitle')
                if tail_text is not None:
                    text.text = tail_text.replace(': ', '', 1)
                item.append(text)
            output_root.append(item)

    # write out the output xml file
    # file format should look like 20180502_ord.xml
    # get the date in that format
    outputted_formatted_date = sitting_date.strftime('%Y%m%d')
    outputfile_name = path.join(path.dirname(path.abspath(input_file_name)), outputted_formatted_date + fileextension)
    outputfile = open(outputfile_name, 'w')
    outputfile.write(xml_declaration + '\n')
    # pretty print ensures indentation
    outputfile.write(etree.tostring(output_root, pretty_print=True).decode(encoding='UTF-8'))
    print('Output file is at: ' + outputfile_name)


def main():
    """Usage: inputfile templatefile sittingdate creationdate OPnumber"""
    if len(sys.argv) != 3:
        print("\nThis script takes 2 arguments.\n",
              "1:\tthe path to the file you wish to process.\n",
              "2:\tthe sitting date in the form YYYY-MM-DD, i.e.'2017-09-12'\n")
        exit()
    input_file_name    = sys.argv[1]
    sitting_date       = sys.argv[2]

    # set_up_dates(sitting_date)
    split_and_output(input_file_name, sitting_date)

    print('Done!')


if __name__ == "__main__": main()
