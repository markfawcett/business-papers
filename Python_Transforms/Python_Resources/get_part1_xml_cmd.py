#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys
# module for working with XML
from lxml import etree
import lxml.html as lhtml
# # module for arguments
# module to sort out html entities
import html
# working with file paths
from os import path
# work with times
from datetime import time

# module for regex
import re
# import argparse

fileextension = '-part1-for-InDesign.xml'

def main():
    if len(sys.argv) != 3:
        print("\nThis script takes 2 arguments.\n",
              "1:\tthe url for the XML you wish to process.\n",
              "3:\tthe date in the for the OP you want to make in the form YYYY-MM-DD, i.e.'2016-09-12'\n"
              )
        exit()

    input_xml  = sys.argv[1]
    input_date = sys.argv[2]

    process_xml(input_xml, input_date)


def process_xml(input_xml, input_date):

    input_root = etree.parse(input_xml).getroot()

    dropns(input_root)
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
    # output root Add element for Business Today Chamber
    append_fromstring(output_root, '<OPHeading1>Business Today: Chamber&#8233;</OPHeading1>')

    # headings that can apear in the Announcement section
    ann_headings  = [
                    'FORTHCOMING END OF DAY ADJOURNMENT DEBATES',
                    'FORTHCOMING WESTMINSTER HALL DEBATES',
                    'FUTURE DEPARTMENTS ANSWERING IN WESTMINSTER HALL',
                    'PRIVATE MEMBERS\' BILLS'
                    ]  # end of list


    # create a variable to store a reference to the heading as where a business item falls determins its style
    last_gray_heading_text = ''

    # create a boolian variable for weather the announcement heading has been added yet
    ann_heading_done = False
    # and written statement heading
    ws_heading_done = False
    # and heading for westminster hall
    wh_heading_done = False
    # question placeholder added
    questions_done  = False
    # weather or not the no debate and (Standing Order No 57)
    presentation_of_bills_nodebate_so = False

    # get all the DayItem in the day
    dayItem_prayers = day_element.find('.//DayItem')
    # fist check if the first element is Prays
    if dayItem_prayers is not None and dayItem_prayers.find('Title').text.upper().strip() == 'PRAYERS':
        prayer_time = dayItem_prayers.findtext('BusinessItemDetail/Time')
        prayer_time = format_time(prayer_time)
        append_fromstring(output_root, '<DebateTimingRubric>' + prayer_time + ' Prayers&#8233;</DebateTimingRubric>')
        append_fromstring(output_root, '<DebateTimingRubric>Followed by&#8233;</DebateTimingRubric>')
        # delete the day item
        dayItem_prayers.getparent().remove(dayItem_prayers)
    else:
        append_fromstring(output_root, '<DebateTimingRubric>4.99am Prayers&#8233;</DebateTimingRubric>')
        append_fromstring(output_root, '<DebateTimingRubric>Followed by&#8233;</DebateTimingRubric>')

    # get all the DayItem in the day
    dayItem_all = day_element.xpath('.//DayItem')

    for dayItem in dayItem_all:
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
        # find the title if it exists
        title = dayItem.find('Title')

        # first test to see if the day item is a heading and then update the section to append to

        if day_item_type.text == 'SectionDayDivider':
            # add static note to the end of written statements
            if last_gray_heading_text == 'STATEMENTS TO BE MADE TODAY':
                append_fromstring(output_root, '<NoteHeading>Notes:&#8233;</NoteHeading>')
                append_fromstring(output_root, '<NoteText>Texts of Written Statements are available from the Vote Office and on the internet at http://www.parliament.uk/business/publications/written-questions-answers-statements/written-statements/.&#8233;</NoteText>')

            # Set up the last gray heading verialbe. This is because elements take different styles based on wich section they are in
            last_gray_heading_text = title.text.upper()

            # make heading for the announcements
            if ann_heading_done is False and title.text.upper() in ann_headings:
                append_fromstring(output_root, '<OPHeading1>Announcements&#8233;</OPHeading1>')
                ann_heading_done = True

            # make heading for the Written Statements
            if ws_heading_done is False and title.text.upper() == 'STATEMENTS TO BE MADE TODAY':
                append_fromstring(output_root, '<OPHeading1>Written Statements&#8233;</OPHeading1>')
                ws_heading_done = True

            # make heading for the Westminster Hall
            if wh_heading_done is False and title.text.upper() == 'ORDER OF BUSINESS':
                append_fromstring(output_root, '<OPHeading1>Business Today: Westminster Hall&#8233;</OPHeading1>')
                wh_heading_done = True

            # now add any section day divider title to the XML for InDesign
            append_fromstring(output_root, '<OPHeading2>' + dayItem.findtext('Title', default='') + '&#8233;</OPHeading2>')
            # also add any notes
            if dayItem.find('Notes') is not None:
                append_fromstring(output_root, '<DebateTimingRubric>' + dayItem.findtext('Notes', default='') + '&#8233;</DebateTimingRubric>')
            # if urgent questions and statements add time
            if title is not None and title.text.upper() == 'URGENT QUESTIONS AND STATEMENTS':
                time_in_op_form = format_time(dayItem.getnext().findtext('BusinessItemDetail/Time', default=''))
                if time_in_op_form is not None:
                    append_fromstring(output_root,
                                      '<DebateTimingRubric>' +
                                      time_in_op_form +
                                      '&#8233;</DebateTimingRubric>')
        # if this is a business item
        elif day_item_type.text == 'BusinessItem':
            # print(title_above_text(dayItem).upper())
            if last_gray_heading_text == 'BUSINESS OF THE DAY':
                if day_item_is_child is False:
                    append_fromstring(output_root,
                                      '<BusinessItemHeadingNumbered>' +
                                      dayItem.findtext('Title', default='') +
                                      '&#8233;</BusinessItemHeadingNumbered>')
                else:
                    append_fromstring(output_root,
                                      '<Bulleted>{}&#8233;</Bulleted>'
                                      .format(dayItem.findtext('Title', default=''))
                                      )
                # next get timing and so reference
                append_timing_so(output_root, dayItem)

                # get the sponsor info
                append_motion_sponosrs(dayItem, output_root)

                # get the main item text
                motionText = etree.Element('MotionText')
                motionText.append(process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
                output_root.append(motionText)

                # make sure we get any amendments
                amendments = dayItem.findall('BusinessItemDetail/Amendments/Amendment')
                previous_amendment_letter = ''
                for amendment in amendments:
                    # add the amendment leter text e.g. Amednment (a)
                    amendment_letter = next_letter(previous_amendment_letter)
                    append_fromstring(output_root, '<MotionAmmendmentSponsor>Amendment(' + amendment_letter + ')&#8233;</MotionAmmendmentSponsor>')
                    previous_amendment_letter = amendment_letter
                    # print(amendment[0].text)
                    sponsors = amendment.find('Sponsors')
                    # first 6 sponsors are in bold and each on one line
                    if len(sponsors) > 0:
                        for sponsor in sponsors[:6]:
                            append_fromstring(output_root, '<MotionAmmendmentSponsor>' +
                                              sponsor.findtext('Name', default='').strip() +
                                              '&#8233;</MotionAmmendmentSponsor>')
                    # after the first 6 sponsors are not in bold and 3 per line
                    if len(sponsors) > 6:
                        m_a_s_g = etree.Element('MotionAmmendmentSponsorGroup')
                        m_a_s_g.text = ''
                        for next_sponsor in sponsors[6:]:
                            m_a_s_g.text += next_sponsor.findtext('Name', default='') + '\t'
                        m_a_s_g.text += '\n'
                        output_root.append(m_a_s_g)
                    append_fromstring(output_root, '<MotionAmmendmentText>' +
                                      amendment.findtext('FriendlyDescription', default='').strip() +
                                      '&#8233;</MotionAmmendmentText>')
                # end of ammenments section
                # add Relevant Documents
                notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)

                # if dayItem.findtext('BusinessItemDetail/RelevantDocuments') is not None:
                #     note_heading = etree.fromstring('<NoteHeading>Relevant Documents:&#8233;</NoteHeading>')
                #     note_text    = etree.Element('NoteText')
                #     note_text.text = dayItem.findtext('BusinessItemDetail/RelevantDocuments', default='') + '\n'
                #     output_root.append(note_heading)
                #     output_root.append(note_text)
                # if dayItem.findtext('BusinessItemDetail/Notes') is not None:
                #     note_heading = etree.fromstring('<NoteHeading>Notes:&#8233;</NoteHeading>')
                #     note_text    = etree.Element('NoteText')
                #     note_text.text = dayItem.findtext('BusinessItemDetail/Notes', default='') + '\n'
                #     output_root.append(note_heading)
                #     output_root.append(note_text)

            # if questions add a place holder xml element to add the xml from the question system
            elif last_gray_heading_text == 'QUESTIONS':
                if questions_done == False:
                    questions_elemnt = etree.Element('QUESTIONS')
                    questions_elemnt.tail = '\n'
                    output_root.append(questions_elemnt)
                    questions_done = True

            # elif last_gray_heading_text == 'ADJOURNMENT DEBATE':
            #     append_timing_so(output_root, dayItem)
            #     append_fromstring(output_root, '<BusinessListItem>' + dayItem.findtext('Title', default='') + ': </BusinessListItem>')
            #     # also need to append the sponsor
            #     for sponsor in dayItem.find('BusinessItemDetail/Sponsors'):
            #         append_fromstring(output_root,
            #                           '<PresenterSponsor>' +
            #                           sponsor.findtext('Name', default='') +
            #                           '&#8233;</PresenterSponsor>'
            #                           )

            elif last_gray_heading_text == 'STATEMENTS TO BE MADE TODAY':
                append_fromstring(output_root,
                                  '<MinisterialStatement>' +
                                  dayItem.findtext('Title', default='') +
                                  '&#8233;</MinisterialStatement>')


            elif last_gray_heading_text == 'PRESENTATION OF BILLS':
                # only add the so and 'No debate (Standing Order No. 57)' once
                if presentation_of_bills_nodebate_so == False:
                    append_timing_so(output_root, dayItem)
                    # check the above line to see if it is (Standing Order No. 57). if it is then add No debate before
                    if output_root[-1].find('SOReference') is not None and output_root[-1].find('SOReference').text == '(Standing Order No. 57)':
                        output_root[-1].text = 'No debate '
                        presentation_of_bills_nodebate_so = True
                if dayItem.findtext('Title', default='').upper().strip() != 'NO TITLE NEEDED':
                    append_fromstring(output_root, '<BusinessItemHeadingBulleted>' + dayItem.findtext('Title', default='') + '&#8233;</BusinessItemHeadingBulleted>')
                # make sure we get announcement stuff
                businessItemType = dayItem.find('BusinessItemDetail/BusinessItemType')
                # get the sponsor info
                append_motion_sponosrs(dayItem, output_root)
                if businessItemType is not None:
                    motionText = etree.Element('MotionText')
                    motionText.append(process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
                    output_root.append(motionText)
                    # add notes
                    # add Relevant Documents
                    notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)

                    # if dayItem.findtext('BusinessItemDetail/RelevantDocuments') is not None:
                    #     note_heading = etree.fromstring('<NoteHeading>Relevant Documents:&#8233;</NoteHeading>')
                    #     note_text    = etree.Element('NoteText')
                    #     note_text.text = dayItem.findtext('BusinessItemDetail/RelevantDocuments', default='') + '\n'
                    #     output_root.append(note_heading)
                    #     output_root.append(note_text)
                    # if dayItem.findtext('BusinessItemDetail/Notes') is not None:
                    #     note_heading = etree.fromstring('<NoteHeading>Notes:&#8233;</NoteHeading>')
                    #     note_text    = etree.Element('NoteText')
                    #     note_text.text = dayItem.findtext('BusinessItemDetail/Notes', default='') + '\n'
                    #     output_root.append(note_heading)
                    #     output_root.append(note_text)


            elif last_gray_heading_text == 'ADJOURNMENT DEBATE' or last_gray_heading_text == 'PRESENTATION OF PUBLIC PETITIONS':
                append_timing_so(output_root, dayItem)
                # for public petitions add No debate of decision before SO 153.
                if output_root[-1].find('SOReference') is not None and output_root[-1].find('SOReference').text == '(Standing Order No. 153)':
                    output_root[-1].text = 'No debate or decision '
                append_fromstring(output_root, '<BusinessListItem>' + dayItem.findtext('Title', default='') + ': </BusinessListItem>')
                # also need to append the sponsor
                for sponsor in dayItem.find('BusinessItemDetail/Sponsors'):
                    append_fromstring(output_root,
                                      '<PresenterSponsor>' +
                                      sponsor.findtext('Name', default='') +
                                      '&#8233;</PresenterSponsor>'
                                      )
            # do special stuff for westminster hall
            elif last_gray_heading_text == 'ORDER OF BUSINESS':
                # get the time
                time_in_op_form = format_time(dayItem.findtext('BusinessItemDetail/Time', default=''))
                if time_in_op_form is not None:
                    append_fromstring(output_root, '<DebateTimingRubric>' + time_in_op_form + '&#8233;</DebateTimingRubric>')
                append_fromstring(output_root, '<BusinessListItem>' + dayItem.findtext('Title', default='') + ': </BusinessListItem>')
                # also need to append the sponsor
                for sponsor in dayItem.find('BusinessItemDetail/Sponsors'):
                    presentor_sponsor_str = '<PresenterSponsor>{}{}&#8233;</PresenterSponsor>'
                    relavant_interest = ''
                    if sponsor.findtext('HasRelevantInterest') == 'true':
                        relavant_interest = ' [R]'
                    presentor_sponsor_str.format(sponsor.findtext('Name', default=''), relavant_interest)
                    append_fromstring(output_root,
                                      '<PresenterSponsor>' +
                                      sponsor.findtext('Name', default='') +
                                      '&#8233;</PresenterSponsor>'
                                      )
                # get relevant documents and notes
                if has_children is False:
                    # get any notes
                    notes = dayItem.findtext('BusinessItemDetail/Notes')
                    if notes is not None and notes.strip() != '':
                        append_fromstring(output_root, '<NoteHeading>Notes:&#8233;</NoteHeading>')
                        append_fromstring(output_root, '<NoteText>' + notes + '&#8233;</NoteText>')
                    relevant_documents = dayItem.findtext('BusinessItemDetail/RelevantDocuments')
                    if relevant_documents is not None and relevant_documents.strip() != '':
                        append_fromstring(output_root, '<NoteHeading>Relevant Documents:&#8233;</NoteHeading>')
                        append_fromstring(output_root, '<NoteText>' + relevant_documents + '&#8233;</NoteText>')
                # get notes and Relavant documents for parent item if last child
                if dayItem.getnext() is None and day_item_is_child is True:
                    # get any notes
                    notes = dayItem.getparent().getparent().findtext('Notes')
                    if notes is not None and notes.strip() != '':
                        append_fromstring(output_root, '<NoteHeading>Notes:&#8233;</NoteHeading>')
                        append_fromstring(output_root, '<NoteText>' + notes + '&#8233;</NoteText>')
                    relevant_documents = dayItem.getparent().getparent().findtext('RelevantDocuments')
                    if relevant_documents is not None and relevant_documents.strip() != '':
                        append_fromstring(output_root, '<NoteHeading>Relevant Documents:&#8233;</NoteHeading>')
                        append_fromstring(output_root, '<NoteText>' + relevant_documents + '&#8233;</NoteText>')

                # if dayItem.findtext('BusinessItemDetail/RelevantDocuments') is not None:
                #     note_heading = etree.fromstring('<NoteHeading>Relevant Documents:&#8233;</NoteHeading>')
                #     note_text    = etree.Element('NoteText')
                #     note_text.text = dayItem.findtext('BusinessItemDetail/RelevantDocuments', default='') + '\n'
                #     output_root.append(note_heading)
                #     output_root.append(note_text)
                # if dayItem.findtext('BusinessItemDetail/Notes') is not None:
                #     note_heading = etree.fromstring('<NoteHeading>Notes:&#8233;</NoteHeading>')
                #     note_text    = etree.Element('NoteText')
                #     note_text.text = dayItem.findtext('BusinessItemDetail/Notes', default='') + '\n'
                #     output_root.append(note_heading)
                #     output_root.append(note_text)

            # elif last_gray_heading_text == 'PRESENTATION OF BILLS':
            #     append_timing_so(output_root, dayItem)
            #     append_fromstring(output_root,
            #                       '<BusinessItemHeadingBulleted>' +
            #                       dayItem.findtext('Title', default='') +
            #                       '&#8233;</BusinessItemHeadingBulleted>')
            #     # get the sponsor info
            #     for sponsor in dayItem.find('BusinessItemDetail/Sponsors'):
            #         append_fromstring(output_root,
            #                           '<MotionSponsor>' +
            #                           sponsor.findtext('Name', default='') +
            #                           '&#8233;</MotionSponsor>'
            #                           )
            #     # get the main item text
            #     motionText = etree.Element('MotionText')
            #     motionText.append(process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
            #     output_root.append(motionText)

            else:
                if dayItem.findtext('Title', default='').upper().strip() != 'NO TITLE NEEDED':
                    append_fromstring(output_root, '<BusinessItemHeadingBulleted>' + dayItem.findtext('Title', default='') + '&#8233;</BusinessItemHeadingBulleted>')
                append_timing_so(output_root, dayItem)
                # make sure we get announcement stuff
                businessItemType = dayItem.find('BusinessItemDetail/BusinessItemType')
                # get the sponsor info
                append_motion_sponosrs(dayItem, output_root)
                if businessItemType is not None:
                    motionText = etree.Element('MotionText')
                    motionText.append(process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
                    output_root.append(motionText)
                    # add Relevant Documents
                    notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child)
                    # if dayItem.findtext('BusinessItemDetail/RelevantDocuments') is not None:
                    #     note_heading = etree.fromstring('<NoteHeading>Relevant Documents:&#8233;</NoteHeading>')
                    #     note_text    = etree.Element('NoteText')
                    #     note_text.text = dayItem.findtext('BusinessItemDetail/RelevantDocuments', default='') + '\n'
                    #     output_root.append(note_heading)
                    #     output_root.append(note_text)
                    # # add notes
                    # if dayItem.findtext('BusinessItemDetail/Notes') is not None:
                    #     note_heading = etree.fromstring('<NoteHeading>Notes:&#8233;</NoteHeading>')
                    #     note_text    = etree.Element('NoteText')
                    #     note_text.text = dayItem.findtext('BusinessItemDetail/Notes', default='') + '\n'
                    #     output_root.append(note_heading)
                    #     output_root.append(note_text)

    # get the path to input file
    pwd = path.dirname(path.abspath(input_xml))
    # write out the file
    filename = path.basename(input_xml).replace('as-downloaded-', '').split('.')[0]
    filepath = path.join(pwd, filename)
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


def notes_relevant_docs(dayItem, output_root, has_children, day_item_is_child):
    if has_children is False:
        # get any notes
        notes = dayItem.findtext('BusinessItemDetail/Notes')
        if notes is not None and notes.strip() != '':
            append_fromstring(output_root, '<NoteHeading>Notes:&#8233;</NoteHeading>')
            append_fromstring(output_root, '<NoteText>' + notes + '&#8233;</NoteText>')
        relevant_documents = dayItem.findtext('BusinessItemDetail/RelevantDocuments')
        if relevant_documents is not None and relevant_documents.strip() != '':
            append_fromstring(output_root, '<NoteHeading>Relevant Documents:&#8233;</NoteHeading>')
            append_fromstring(output_root, '<NoteText>' + relevant_documents + '&#8233;</NoteText>')
    # get notes and Relavant documents for parent item if last child
    if dayItem.getnext() is None and day_item_is_child is True:
        # get any notes
        notes = dayItem.getparent().getparent().findtext('Notes')
        if notes is not None and notes.strip() != '':
            append_fromstring(output_root, '<NoteHeading>Notes:&#8233;</NoteHeading>')
            append_fromstring(output_root, '<NoteText>' + notes + '&#8233;</NoteText>')
        relevant_documents = dayItem.getparent().getparent().findtext('RelevantDocuments')
        if relevant_documents is not None and relevant_documents.strip() != '':
            append_fromstring(output_root, '<NoteHeading>Relevant Documents:&#8233;</NoteHeading>')
            append_fromstring(output_root, '<NoteText>' + relevant_documents + '&#8233;</NoteText>')



def append_timing_so(output_root, current_element):
    if (current_element.findtext('BusinessItemDetail/Duration', default=None) is not None and
        current_element.findtext('BusinessItemDetail/StandingOrders/StandingOrder/Text', default=None) is not None):
        append_fromstring(output_root,
                          '<DebateTimingRubric>' +
                          current_element.findtext('BusinessItemDetail/Duration', default='') +
                          ' ' +
                          '<SOReference>(' +
                          current_element.findtext('BusinessItemDetail/StandingOrders/StandingOrder/Text', default='') +
                          ')</SOReference>' +
                          '&#8233;</DebateTimingRubric>')
    elif current_element.findtext('BusinessItemDetail/Duration', default=None) is not None:
        append_fromstring(output_root,
                          '<DebateTimingRubric>' +
                          current_element.findtext('BusinessItemDetail/Duration', default='') +
                          '&#8233;</DebateTimingRubric>')
    elif current_element.findtext('BusinessItemDetail/StandingOrders/StandingOrder/Text', default=None) is not None:
        append_fromstring(output_root,
                          '<DebateTimingRubric><SOReference>(' +
                          current_element.findtext('BusinessItemDetail/StandingOrders/StandingOrder/Text', default='') +
                          ')</SOReference>&#8233;</DebateTimingRubric>')


def append_motion_sponosrs(dayItem, append_to):
    sponsors = dayItem.find('BusinessItemDetail/Sponsors')
    m_a_s_g = etree.Element('MotionSponsorGroup')
    m_a_s_g.text = ''
    for i, sponsor in enumerate(sponsors):
        sponsor_notes = dayItem.findtext('BusinessItemDetail/SponsorNotes')
        if i == 0 and (sponsor_notes is not None and sponsor_notes.strip() != ''):
            sponosr_note_xml = ', <SponsorNotes>{}</SponsorNotes>'.format(sponsor_notes)
        else:
            sponosr_note_xml = ''

        # first 6 sponsors are in bold and each on one line
        if i == 0:
            append_fromstring(append_to,
                              '<MotionSponsor>{}{}&#8233;</MotionSponsor>'
                              .format(sponsor.findtext('Name', default=''), sponosr_note_xml)
                              )
        elif i > 0 and i < 6:
            append_fromstring(append_to, '<MotionSponsor>' +
                              sponsor.findtext('Name', default='').strip() +
                              '&#8233;</MotionSponsor>')
        # after the first 6 sponsors are not in bold and 3 per line
        else:
            m_a_s_g.text += sponsor.findtext('Name', default='') + '\t'
    if len(sponsors) > 6:
            m_a_s_g.tail = '\u2029'  # will map to &#8233; paragraph sep
            append_to.append(m_a_s_g)


def append_fromstring(parent, xml_string):
    xml_string = html.unescape(xml_string).encode('ascii', 'xmlcharrefreplace').decode('utf-8')
    xml_string = re.sub(r'&([^#])', '&amp; ', xml_string)
    # print(html.unescape(xml_string).encode('ascii', 'xmlcharrefreplace').decode('utf-8'))
    parent.append(etree.fromstring(xml_string))


def process_CDATA(text_from_xml):
    unescaped = html.unescape(text_from_xml).strip()
    # need to remove unnessesary line breaks and non breaking spaces
    unescaped = re.sub(r'\n\n+', '\n', unescaped)
    # remove some of the non breaking spaces followed by line break
    unescaped = re.sub(r'\u00A0\n\u00A0\n+', '\u00A0\n', unescaped)
    # remove some of the non breaking spaces
    unescaped = re.sub(r'\u00A0\u00A0+', ' ', unescaped)
    cdata_element_string = '<from_cdata>' + unescaped + '</from_cdata>'
    # create an lxml html element
    cdata_element = lhtml.fromstring(cdata_element_string)

    # ---- TABLES -----------------

    # create a number for the max width of the table
    max_table_width = 466  # this is measured in points

    # get all the table elements
    tables = cdata_element.xpath('//table')
    # go through the tables backwards because there could be tables in tables...
    for table in reversed(tables):
        table_rows = table.xpath('tbody/tr|thead/tr|tfoot/tr|tr')
        # number of table rows
        table_rows_number = len(table_rows)
        # now find out the maximum number of cells in each row
        max_cells = 0
        for row in table_rows:
            table_cells = row.xpath('td')
            number_of_cells = len(table_cells)
            if number_of_cells > max_cells:
                max_cells = number_of_cells
        # create InDesign table element
        inDesign_tabel = etree.fromstring('<Table xmlns:aid="http://ns.adobe.com/AdobeInDesign/4.0/" xmlns:aid5="http://ns.adobe.com/AdobeInDesign/5.0/" aid:table="table" aid:tcols="1" aid:trows="1" aid5:tablestyle="StandardTable"></Table>')
        # fix rows and colls attributes
        inDesign_tabel.attrib['{http://ns.adobe.com/AdobeInDesign/4.0/}tcols'] = str(max_cells)
        inDesign_tabel.attrib['{http://ns.adobe.com/AdobeInDesign/4.0/}trows'] = str(table_rows_number)
        # now actually add the cells to the InDesign table
        for counter in range(max_cells * table_rows_number):
            temp_cell = etree.fromstring('<Cell></Cell>')
            inDesign_tabel.append(temp_cell)
            temp_cell.set('{http://ns.adobe.com/AdobeInDesign/4.0/}ccols', '1')
            # need to adjust the coll width depending on the numebr of columns
            temp_cell.set('{http://ns.adobe.com/AdobeInDesign/4.0/}ccolwidth', str(max_table_width / max_cells))
            temp_cell.set('{http://ns.adobe.com/AdobeInDesign/4.0/}crows', '1')
            temp_cell.set('{http://ns.adobe.com/AdobeInDesign/4.0/}table', 'cell')


        # now run through the InDesign table and add text
        InDesign_cell_counter = 0
        for row_counter in range(len(table_rows)):
            table_cells = table_rows[row_counter].xpath('td')
            for cell_counter in range(max_cells):
                if cell_counter < len(table_rows[row_counter]):
                    if row_counter == 0:
                        bold_para_heading = etree.Element('DebateTimingRubric')
                        bold_para_heading.text = table_cells[cell_counter].text
                        # remove extra new line from the end
                        if bold_para_heading.text is not None and bold_para_heading.text[-1] == '\n':
                            bold_para_heading.text = bold_para_heading.text[:-1]
                        inDesign_tabel[InDesign_cell_counter].append(bold_para_heading)
                        # inDesign_tabel[InDesign_cell_counter].set('{http://ns.adobe.com/AdobeInDesign/4.0/}theader', '')
                    else:
                        inDesign_tabel[InDesign_cell_counter].text = table_cells[cell_counter].text
                        # remove extra new line from the end
                        if inDesign_tabel[InDesign_cell_counter].text is not None and inDesign_tabel[InDesign_cell_counter].text[-1] == '\n':
                            inDesign_tabel[InDesign_cell_counter].text = inDesign_tabel[InDesign_cell_counter].text[:-1]
                InDesign_cell_counter += 1
        # make top cells headers

        # if there is any tail text on the html, add it to the tail text of the InDesign table
        if table.tail is not None:
            inDesign_tabel.tail = table.tail

        # raplece the html table with an InDesign table
        table.getparent().replace(table, inDesign_tabel)
    if len(cdata_element) > 0 and cdata_element[-1].tail is None:
        cdata_element[-1].tail = '\n'
    elif len(cdata_element) > 0 and cdata_element[-1].tail is not None:
        cdata_element[-1].tail += '\n'
    elif cdata_element.text is not None:
        cdata_element.text += '\n'
    # return etree.tostring(cdata_element)
    return cdata_element


# return times in OP format
def format_time(time_string):
    if isinstance(time_string, str) and len(time_string.split(':')) >= 2:
        split_time = time_string.split(':')
        try:
            output_time = time(hour=int(split_time[0]), minute=int(split_time[1]))
        except:
            return None
        output_time = output_time.strftime('%I.%M%p')
        output_time = output_time.replace('AM', 'am').replace('PM', 'pm').replace('12.00pm', '12 noon')
        if output_time[0] == '0': output_time = output_time[1:]
        return output_time
    else:
        return None


def next_letter(old_letter):
    letters = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
    if old_letter == '':
        return letters[0]
    else:
        if letters.index(old_letter[-1]) == 25:
            return old_letter + letters[0]
        else:
            return letters[letters.index(old_letter[-1]) + 1]


def dropns(root):
    """Remove all namespaces as we wont need them and they get in the way."""
    for elem in root.iter():
        parts = elem.tag.split(':')
        if len(parts) > 1:
            elem.tag = parts[-1]
        entries = []
        for attrib in elem.attrib:
            if attrib.find(':') > -1:
                entries.append(attrib)
        for entry in entries:
            del elem.attrib[entry]



if __name__ == "__main__": main()
