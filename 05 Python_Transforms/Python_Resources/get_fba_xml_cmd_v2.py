#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys
# module for working with XML
from lxml import etree
# working with file paths
from os import path

# import datetime
from datetime import date

# import utility functions
try:
    import get_op_utility_functions as op_functions
except ImportError:
    import Python_Resources.get_op_utility_functions as op_functions

fileextension = '-FBA-for-InDesign.xml'


def main():
    if len(sys.argv) != 3:
        print("\nThis script takes 2 arguments.\n",
              "1:\tthe url for the XML you wish to process.\n",
              "3:\tthe effective date after witch items will apear in FBA, e.g.'2016-09-12'\n"
              )
        exit()

    input_xml  = sys.argv[1]
    input_date = sys.argv[2]

    process_xml(input_xml, input_date)


def process_xml(input_xml, input_date):

    laying_minister_lookup = {}
    laying_minister_lookup = op_functions.get_mnis_data(laying_minister_lookup)

    input_root = etree.parse(input_xml).getroot()
    input_date_object = date(int(input_date.split('-')[0]), int(input_date.split('-')[1]), int(input_date.split('-')[2]))
    op_functions.dropns(input_root)
    # get the day we are interested
    day_elements = input_root.xpath('Days/Day')
    date_to_remove = []
    for day_element in day_elements:
        time_stamp_text = day_element.findtext('Date', default='')
        time_stamp_text = time_stamp_text.replace('T00:00:00', '')
        date_timestamp = date(int(time_stamp_text.split('-')[0]), int(time_stamp_text.split('-')[1]), int(time_stamp_text.split('-')[2]))
        if date_timestamp <= input_date_object:
            date_to_remove.append(day_element)
    for day_element in date_to_remove:
        day_elements.remove(day_element)
    if len(day_elements) < 1:
        input('Error:\tCan\'t seem to find the date you are after. Check it appears in the XML, Press any key to exit.')
        exit()


    # build up output tree
    output_root = etree.Element('root')
    # add the FBA title
    op_functions.append_fromstring(output_root, '<OPHeading1>A. Calendar of Business&#8233;</OPHeading1>')


    for day_element in day_elements:
        # get all the sections
        sections = day_element.xpath('Sections/Section')
        sections_in_day_list = []
        for section in sections:
            sections_in_day_list.append(section.findtext('Name', default='').strip().upper())

        # Add the date in a level 2 gray heading
        date_elelemnt = day_element.find('Date')
        if date_elelemnt is not None and ('CHAMBER' in sections_in_day_list or 'WESTMINSTER HALL' in sections_in_day_list):
            formatted_date = op_functions.format_date(date_elelemnt.text)
            if formatted_date is not None:
                op_functions.append_fromstring(
                    output_root,
                    '<OPHeading2>' + formatted_date + '&#8233;</OPHeading2>'
                )

        # create a variable to store a reference to the heading as where a business item falls determins its style
        last_gray_heading_text = ''
        # print(sections)
        for section in sections:
            section_name = section.findtext('Name')
            if section_name is not None:
                section_name = section_name.strip().upper()
            if section_name in ('CHAMBER', 'WESTMINSTER HALL'):
                op_functions.append_fromstring(
                    output_root,
                    '<FbaLocation>' + section_name + '&#8233;</FbaLocation>'
                )
            else:
                continue
            # get all the DayItem in the day
            dayItems = section.xpath('.//DayItem')

            for dayItem in dayItems:
                # get the day item type or None
                day_item_type = dayItem.find('DayItemType')
                # we need the day item type to not be None
                if day_item_type is None:
                    continue
                # check if this item is a child of another day item
                if dayItem.getparent().tag == 'ChildDayItems':
                    day_item_is_child = True
                else:
                    day_item_is_child = False
                # check if this item has children
                if dayItem.find('BusinessItemDetail/ChildDayItems') is not None and len(dayItem.find('BusinessItemDetail/ChildDayItems')) > 0:
                    has_children = True
                else:
                    has_children = False
                # find the title if it exists
                title = ''
                if dayItem.find('Title') is not None and dayItem.find('Title').text is not None:
                    title = dayItem.find('Title').text.strip()

                # first test to see if the day item is a heading and then update the section to append to

                if day_item_type.text == 'SectionDayDivider' and dayItem.find('Title') is not None:
                    last_gray_heading_text = dayItem.findtext('Title', default='').upper()
                    if last_gray_heading_text.upper() not in ('BUSINESS OF THE DAY', 'URGENT QUESTIONS AND STATEMENTS', 'ORDER OF BUSINESS'):
                        # only add Questions and Adjournment debate heading if not followed by another heading
                        if last_gray_heading_text.upper() in ('QUESTIONS', 'ADJOURNMENT DEBATE'):
                            next_day_item = dayItem.getnext()
                            if next_day_item is not None and next_day_item.findtext('DayItemType', default='') != 'SectionDayDivider':
                                op_functions.append_fromstring(output_root, '<BusinessItemHeading>' + title + '&#8233;</BusinessItemHeading>')

                        else:
                            op_functions.append_fromstring(output_root, '<BusinessItemHeading>' + title + '&#8233;</BusinessItemHeading>')

                # Do different things based on what business item type
                business_item_type = dayItem.find('BusinessItemDetail/BusinessItemType')

                # PRIVATE BUSINESS
                if business_item_type is not None and business_item_type.text == 'Private Business':
                    op_functions.append_fromstring(output_root, '<BusinessItemHeadingBulleted>' + title + '&#8233;</BusinessItemHeadingBulleted>')


                # QUESTIONS
                if business_item_type is not None and business_item_type.text == 'Substantive Question':
                    formatted_time = op_functions.format_time(dayItem.find('BusinessItemDetail/Time').text)
                    op_functions.append_fromstring(output_root, '<QuestionTimeing>' + formatted_time + '\t' + title + '&#8233;</QuestionTimeing>')
                    # add the afterwards word
                    # if dayItem.getnext() is not None and dayItem.getnext().findtext('DayItemType') != 'SectionDayDivider':
                    #     next_business_item_type = dayItem.getnext().find('BusinessItemDetail/BusinessItemType')
                    #     if next_business_item_type is None or (next_business_item_type is not None and next_business_item_type.text != 'Substantive Question'):
                    #         op_functions.append_fromstring(output_root, '<MotionText>Afterwards&#8233;</MotionText>')


                if business_item_type is not None and business_item_type.text in ('Motion', 'Legislation'):
                    # legistation and motion types appear differently if they are in business today
                    if last_gray_heading_text == 'BUSINESS OF THE DAY' and day_item_is_child is False:
                        op_functions.append_fromstring(output_root, '<BusinessItemHeading>' + title + '&#8233;</BusinessItemHeading>')
                    else:
                        op_functions.append_fromstring(output_root, '<Bulleted>' + title + '&#8233;</Bulleted>')

                # Adjournment Debate type is displayed differently in the chamber vs westminster hall
                if business_item_type is not None and business_item_type.text == 'Adjournment Debate':
                    # get the sponsor
                    sponsor_name = dayItem.find('BusinessItemDetail/Sponsors/Sponsor/Name')
                    if sponsor_name is None or sponsor_name.text is None:
                        sponsor_name = ''
                    else:
                        sponsor_name = sponsor_name.text
                    sponsor_ele = etree.Element('PresenterSponsor')
                    sponsor_ele.text = sponsor_name
                    sponsor_ele.tail = "\u2029"
                    # title without end punctuation
                    title_no_end_punctuation = title
                    if title[-1] == '.':
                        title_no_end_punctuation = title_no_end_punctuation[:-1]
                    # Adjournment Debate type is displayed differently in the chamber vs westminster hall
                    if section_name == 'CHAMBER':
                        adjourn_ele = etree.Element('BusinessListItem')
                        adjourn_ele.text = title_no_end_punctuation + ': '
                        # op_functions.append_fromstring(output_root, '<BusinessListItem>' + title + ': <PresenterSponsor>' + sponsor_name.text + '</PresenterSponsor>&#8233;</BusinessListItem>')
                    # westminster hall
                    elif section_name == 'WESTMINSTER HALL':
                        adjourn_ele = etree.Element('WHItemTiming')
                        adjourn_ele.text = op_functions.format_time(dayItem.findtext('BusinessItemDetail/Time', default='')) + '\t' + title_no_end_punctuation + ': '
                        # op_functions.append_fromstring(output_root, '<WHItemTiming>' + op_functions.format_time(dayItem.findtext('BusinessItemDetail/Time', default=None)) + '\t' + title_no_end_punctuation + ': <PresenterSponsor>' + sponsor_name.text + '</PresenterSponsor>&#8233;</WHItemTiming>')
                    else: continue
                    adjourn_ele.append(sponsor_ele)
                    output_root.append(adjourn_ele)

                # Petitions
                if business_item_type is not None and business_item_type.text == 'Petition':
                    # get the sponsor
                    sponsor_name = dayItem.find('BusinessItemDetail/Sponsors/Sponsor/Name')
                    if sponsor_name is None or sponsor_name.text is None:
                        sponsor_name = ''
                    else:
                        sponsor_name = sponsor_name.text
                    sponsor_ele = etree.Element('PresenterSponsor')
                    sponsor_ele.text = sponsor_name
                    sponsor_ele.tail = "\u2029"
                    # title without end punctuation
                    title_no_end_punctuation = title
                    if title[-1] == '.':
                        title_no_end_punctuation = title_no_end_punctuation[:-1]
                    petition_ele = etree.Element('BusinessListItem')
                    petition_ele.text = title_no_end_punctuation + ': '
                    petition_ele.append(sponsor_ele)
                    output_root.append(petition_ele)


                # get the sponsor info
                if business_item_type is not None and business_item_type.text not in ('Adjournment Debate', 'Petition'):
                    op_functions.append_motion_sponosrs(dayItem, output_root, laying_minister_lookup)

                # get the motion text and sponsors. Sponsors are included even when there is no text for PMBs
                if dayItem.findtext('BusinessItemDetail/ItemText', default='') != '':

                    # get the main item text
                    motionText = etree.Element('MotionText')
                    motionText.append(op_functions.process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
                    output_root.append(motionText)


                # output_root.append(op_functions.process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))

                # make sure we get any amendments
                op_functions.append_ammendments(dayItem, output_root, laying_minister_lookup)

                # get relevant documents and notes
                op_functions.notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)


    # get the path to input file
    pwd = path.dirname(path.abspath(input_xml))
    # write out the file
    filename = path.basename(input_xml).replace('as-downloaded-', '').split('.')[0]
    filepath = path.join(pwd, filename)

    # write out an xml file
    et = etree.ElementTree(output_root)

    # write out an xml file
    et = etree.ElementTree(output_root)
    try:
        et.write(filepath + fileextension)  # , pretty_print=True
        print('\nOutput file is located at:\n', path.abspath(filepath + fileextension))
    except:
        # make sure it works even if we dont have permision to modify the file
        try:
            et.write(filepath + '2' + fileextension)
            print('\nOutput file is located at:\n', path.abspath(filepath + '2' + fileextension))
        except:
            print('Error:\tThe file ' + path.abspath(filepath + '2' + fileextension) + ' dose not seem to be writable.')


if __name__ == "__main__": main()
