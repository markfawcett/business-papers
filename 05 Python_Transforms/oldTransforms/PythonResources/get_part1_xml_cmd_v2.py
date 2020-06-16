#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys
# module for working with XML
from lxml import etree
# working with file paths
from os import path
# regular expresions
import re


# import utility functions
try:
    import get_op_utility_functions as op_functions
except ImportError:
    import Python_Resources.get_op_utility_functions as op_functions


fileextension = '-effectives-for-InDesign.xml'



def main():
    if len(sys.argv) != 3:
        print(
            "\nThis script takes 2 arguments.\n",
            "1:\tthe url for the XML you wish to process.\n",
            "2:\tthe date in the for the OP you want to make in the form YYYY-MM-DD, i.e.'2016-09-12'\n"
        )
        exit()

    input_xml  = sys.argv[1]
    input_date = sys.argv[2]

    process_xml(input_xml, input_date)


def process_xml(input_xml, input_date):

    laying_minister_lookup = {}
    laying_minister_lookup = op_functions.get_mnis_data(laying_minister_lookup)

    # sections included in this script
    section_names = ('Chamber', 'Westminster Hall', 'Written Statements', 'Deferred Divisions')
    input_root = etree.parse(input_xml).getroot()

    op_functions.dropns(input_root)
    print(input_root.tag)
    # get the day we are interested
    date_elements = input_root.xpath('Days/Day/Date[text()[contains(.,"' + input_date + '")]]')
    if len(date_elements) != 1:
        input('Error:\tCan\'t seem to find the date you are after. Check it appears in the XML, Press any key to exit.')
        exit()
    else:
        day_element = date_elements[0].getparent()
        # print(day_element[1].tag)
    # build up output tree
    output_root = etree.Element('root')



    # create a variable to store a reference to the heading as where a business item falls determins its style
    last_gray_heading_text = ''


    # question placeholder added
    questions_done  = False
    # weather or not the no debate and (Standing Order No 57)
    presentation_of_bills_nodebate_so = False


    # get all the sections in this day
    sections = day_element.xpath('./Sections/Section')

    # loop through all the sections
    for section in sections:

        # get the section name from the XML
        section_name = section.findtext('Name', default='')
        # skip any sections that are not in the section names defined above
        if section_name not in section_names:
            continue

        # stuff for the chamber section
        if section_name == 'Chamber':
            # output root Add element for Business Today Chamber
            op_functions.append_fromstring(output_root, '<OPHeading1>Business Today: Chamber&#8233;</OPHeading1>')

            # section.find will return the first match which should be the prayers
            dayItem_prayers = section.find('./DayItems/DayItem')
            # fist check if the first element is Prayers
            if dayItem_prayers is not None and dayItem_prayers.find('Title').text.upper().strip() == 'PRAYERS':
                prayer_time = dayItem_prayers.findtext('BusinessItemDetail/Time')
                prayer_time = op_functions.format_time(prayer_time)
                op_functions.append_fromstring(output_root, '<DebateTimingRubric>' + prayer_time + ' Prayers&#8233;</DebateTimingRubric>')
                op_functions.append_fromstring(output_root, '<DebateTimingRubric>Followed by&#8233;</DebateTimingRubric>')
                # delete the day item
                dayItem_prayers.getparent().remove(dayItem_prayers)
            else:
                op_functions.append_fromstring(output_root, '<DebateTimingRubric><red>4.99am Prayers&#8233;</red></DebateTimingRubric>')
                op_functions.append_fromstring(output_root, '<DebateTimingRubric>Followed by&#8233;</DebateTimingRubric>')

        elif section_name == 'Deferred Divisions':
            # do special stuff for Deferred Divisions
            op_functions.append_fromstring(output_root, '<OPHeading1>Deferred Divisions&#8233;</OPHeading1>')

        elif section_name == 'Westminster Hall':
            op_functions.append_fromstring(output_root, '<OPHeading1>Business Today: Westminster Hall&#8233;</OPHeading1>')
            # do special stuff for westminster hall

        # stuff for the Written Statements section
        elif section_name == 'Written Statements':
            op_functions.append_fromstring(output_root, '<OPHeading1>Written Statements&#8233;</OPHeading1>')

        # get all the DayItem in the section
        dayItem_all = section.xpath('.//DayItem')

        for dayItem in dayItem_all:
            # get the day item type or None
            day_item_type = dayItem.find('DayItemType')
            # we need the day item type to not be None
            # so if it in None we will just skip over
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
            title = dayItem.find('Title')
            # get the title_text if it exists
            day_item_title_text = dayItem.findtext('Title', default='')

            # first test to see if the day item is a heading
            if day_item_type.text == 'SectionDayDivider':
                # Set up the last gray heading verialbe. This is because elements take different styles based on wich section they are in
                last_gray_heading_text = day_item_title_text.upper()


                # now add any section day divider title to the XML for InDesign
                op_functions.append_fromstring(output_root, '<OPHeading2>' + day_item_title_text + '&#8233;</OPHeading2>')
                # also add any notes
                if dayItem.find('Notes') is not None:
                    op_functions.append_fromstring(
                        output_root,
                        '<DebateTimingRubric>' + dayItem.findtext('Notes', default='') +
                        '&#8233;</DebateTimingRubric>'
                    )
                # if urgent questions and statements add time
                if title is not None and day_item_title_text.upper() == 'URGENT QUESTIONS AND STATEMENTS':
                    time_in_op_form = op_functions.format_time(dayItem.getnext().findtext('BusinessItemDetail/Time', default=''))
                    if time_in_op_form is not None:
                        op_functions.append_fromstring(
                            output_root,
                            '<DebateTimingRubric>' + time_in_op_form +
                            '&#8233;</DebateTimingRubric>'
                        )

            # do things relating to the chamber section first
            if section_name == 'Chamber':
                # if this is a business item
                if day_item_type.text == 'BusinessItem':
                    # print(title_above_text(dayItem).upper())
                    if last_gray_heading_text == 'BUSINESS OF THE DAY':
                        if day_item_is_child is False:
                            op_functions.append_fromstring(
                                output_root,
                                '<BusinessItemHeadingNumbered>' +
                                day_item_title_text +
                                '&#8233;</BusinessItemHeadingNumbered>'
                            )
                        else:
                            op_functions.append_fromstring(
                                output_root,
                                '<Bulleted>{}&#8233;</Bulleted>'
                                .format(day_item_title_text)
                            )
                        # next get timing and so reference
                        op_functions.append_timing_so(output_root, dayItem)

                        # get the sponsor info
                        op_functions.append_motion_sponosrs(dayItem, output_root, laying_minister_lookup)

                        # get the main item text
                        motionText = etree.Element('MotionText')
                        motionText.append(op_functions.process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
                        output_root.append(motionText)

                        # make sure we get any amendments
                        op_functions.append_ammendments(dayItem, output_root, laying_minister_lookup)
                        # add Relevant Documents
                        op_functions.notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)

                    # if questions add a place holder xml element to add the xml from the question system
                    elif last_gray_heading_text == 'QUESTIONS':
                        if questions_done is False:
                            questions_elemnt = etree.Element('QUESTIONS')
                            questions_elemnt.tail = '\n'
                            output_root.append(questions_elemnt)
                            questions_done = True
                    elif last_gray_heading_text == 'PRESENTATION OF BILLS':
                        # only add the so and 'No debate (Standing Order No. 57)' once
                        if presentation_of_bills_nodebate_so is False:
                            op_functions.append_timing_so(output_root, dayItem)
                            # check the above line to see if it is (Standing Order No. 57). if it is then add No debate before
                            if output_root[-1].find('SOReference') is not None and output_root[-1].find('SOReference').text == '(Standing Order No. 57)':
                                output_root[-1].text = 'No debate '
                                presentation_of_bills_nodebate_so = True
                        if day_item_title_text.upper().strip() != 'NO TITLE NEEDED':
                            op_functions.append_fromstring(
                                output_root,
                                '<BusinessItemHeadingBulleted>' + day_item_title_text +
                                '&#8233;</BusinessItemHeadingBulleted>'
                            )
                        # make sure we get announcement stuff
                        businessItemType = dayItem.find('BusinessItemDetail/BusinessItemType')
                        # get the sponsor info
                        op_functions.append_motion_sponosrs(dayItem, output_root, laying_minister_lookup)
                        if businessItemType is not None:
                            motionText = etree.Element('MotionText')
                            motionText.append(op_functions.process_CDATA(
                                dayItem.findtext('BusinessItemDetail/ItemText', default=''))
                            )
                            output_root.append(motionText)
                            # add notes
                            # add Relevant Documents
                            op_functions.notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)

                    elif last_gray_heading_text == 'ADJOURNMENT DEBATE' or last_gray_heading_text == 'PRESENTATION OF PUBLIC PETITIONS':
                        op_functions.append_timing_so(output_root, dayItem)
                        # for public petitions add No debate of decision before SO 153.
                        if output_root[-1].find('SOReference') is not None and output_root[-1].find('SOReference').text == '(Standing Order No. 153)':
                            output_root[-1].text = 'No debate or decision '
                        op_functions.append_fromstring(
                            output_root,
                            '<BusinessListItem>' + day_item_title_text + ': </BusinessListItem>'
                        )
                        # also need to append the sponsor
                        op_functions.append_presenter_sponsor(dayItem, output_root)
                    else:
                        if day_item_title_text.upper().strip() != 'NO TITLE NEEDED':
                            op_functions.append_fromstring(
                                output_root,
                                '<BusinessItemHeadingBulleted>' + day_item_title_text +
                                '&#8233;</BusinessItemHeadingBulleted>'
                            )
                        op_functions.append_timing_so(output_root, dayItem)
                        # make sure we get announcement stuff
                        businessItemType = dayItem.find('BusinessItemDetail/BusinessItemType')
                        # get the sponsor info
                        op_functions.append_motion_sponosrs(dayItem, output_root, laying_minister_lookup)
                        if businessItemType is not None:
                            motionText = etree.Element('MotionText')
                            motionText.append(op_functions.process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
                            output_root.append(motionText)
                            # add Relevant Documents
                            op_functions.notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)

            elif section_name == 'Deferred Divisions':
                if day_item_type.text == 'BusinessItem':
                    op_functions.append_fromstring(
                        output_root,
                        '<BusinessItemHeadingBulleted>' + day_item_title_text + '&#8233;</BusinessItemHeadingBulleted>'
                    )
                    op_functions.append_motion_sponosrs(dayItem, output_root, laying_minister_lookup)
                    motionText = etree.SubElement(output_root, 'MotionText')
                    motionText.append(op_functions.process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
                    op_functions.notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)

            # stuff for the westminster hall section
            elif section_name == 'Westminster Hall':

                if day_item_type.text == 'BusinessItem':

                    time_in_op_form = op_functions.format_time(dayItem.findtext('BusinessItemDetail/Time', default=''))
                    if time_in_op_form is not None:
                        op_functions.append_fromstring(
                            output_root,
                            '<DebateTimingRubric>' + time_in_op_form + '&#8233;</DebateTimingRubric>'
                        )
                    # Very annoyingly, some users put westminster hall items in as adjournment
                    # debates while others put them in as motions. Further, when motions are
                    # entered sometimes the title mathces the ItemText ane other times it doesnt.
                    # when the westminster hall item is a motion use the motion text when it is
                    # an adjournment debate use the title
                    if dayItem.findtext('BusinessItemDetail/BusinessItemType', default='') == 'Motion':
                        business_list_item = etree.SubElement(output_root, 'BusinessListItem')
                        business_list_item.append(
                            op_functions.process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
                    # else we probably have an announcememnt section
                    else:
                        op_functions.append_fromstring(
                            output_root,
                            '<BusinessListItem>' + day_item_title_text + ': </BusinessListItem>'
                        )
                    # also need to append the sponsor
                    op_functions.append_presenter_sponsor(dayItem, output_root)

                    # get relevant documents and notes
                    op_functions.notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)

            elif section_name == 'Written Statements':
                if day_item_type.text == 'BusinessItem':
                    op_functions.append_fromstring(
                        output_root,
                        '<MinisterialStatement>' + day_item_title_text + '&#8233;</MinisterialStatement>'
                    )
                    op_functions.notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)


        # remember to add a static note to the bottom on written statements
        if section_name == 'Written Statements':
            op_functions.append_fromstring(output_root, '<NoteHeading>Notes:&#8233;</NoteHeading>')
            op_functions.append_fromstring(
                output_root,
                '<NoteText>Texts of Written Statements are available from the Vote Office and on the internet at ' +
                'http://www.parliament.uk/business/publications/written-questions-answers-statements/written-statements/.&#8233;</NoteText>'
            )

    # loop through output
    # replace any non breaking spaces with ordinary spaces
    # replace single quotes with double quotes
    op_functions.clean_up_text(output_root)

    # get the path to input file
    pwd = path.dirname(path.abspath(input_xml))
    # write out the file
    filename = path.basename(input_xml).replace('as-downloaded-', '').split('.')[0]
    filepath = path.join(pwd, filename)

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
