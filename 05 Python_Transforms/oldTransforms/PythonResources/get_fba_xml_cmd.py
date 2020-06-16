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
# import datetime
from datetime import time, date
# module for regex
import re

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

    input_root = etree.parse(input_xml).getroot()
    input_date_object = date(int(input_date.split('-')[0]), int(input_date.split('-')[1]), int(input_date.split('-')[2]))
    dropns(input_root)
    # print(input_root.tag)
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
    append_fromstring(output_root, '<OPHeading1>A. Calendar of Business&#8233;</OPHeading1>')


    for day_element in day_elements:
        # get all the sections
        sections = day_element.xpath('Sections/Section')
        sections_in_day_list = []
        for section in sections:
            sections_in_day_list.append(section.findtext('Name', default='').strip().upper())

        # Add the date in a level 2 gray heading
        date_elelemnt = day_element.find('Date')
        if date_elelemnt is not None and ('CHAMBER' in sections_in_day_list or 'WESTMINSTER HALL' in sections_in_day_list):
            formatted_date = format_date(date_elelemnt.text)
            if formatted_date is not None:
                append_fromstring(output_root, '<OPHeading2>' + formatted_date + '&#8233;</OPHeading2>')

        # create a variable to store a reference to the heading as where a business item falls determins its style
        last_gray_heading_text = ''
        # print(sections)
        for section in sections:
            section_name = section.findtext('Name')
            if section_name is not None:
                section_name = section_name.strip().upper()
            if section_name in ('CHAMBER', 'WESTMINSTER HALL'):
                append_fromstring(output_root, '<FutureBusinessLocationHeading>' + section_name + '&#8233;</FutureBusinessLocationHeading>')
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
                                append_fromstring(output_root, '<BusinessItemHeading>' + title + '&#8233;</BusinessItemHeading>')
                                # print(dayItem.findtext('Title', default='').upper(), dayItem.findtext('DayItemId', default=''))
                                # if next_day_item is None:
                                #     print('here None')
                                # else:
                                #     print('here', next_day_item.findtext('Title', default=''))
                                # continue
                        else:
                            append_fromstring(output_root, '<BusinessItemHeading>' + title + '&#8233;</BusinessItemHeading>')

                # Do different things based on what business item type
                business_item_type = dayItem.find('BusinessItemDetail/BusinessItemType')

                # PRIVATE BUSINESS
                if business_item_type is not None and business_item_type.text == 'Private Business':
                    append_fromstring(output_root, '<BusinessItemHeadingBulleted>' + title + '&#8233;</BusinessItemHeadingBulleted>')


                # QUESTIONS
                if business_item_type is not None and business_item_type.text == 'Substantive Question':
                    formatted_time = format_time(dayItem.find('BusinessItemDetail/Time').text)
                    append_fromstring(output_root, '<QuestionTimeing>' + formatted_time + '\t' + title + '&#8233;</QuestionTimeing>')
                    # add the afterwards word
                    # if dayItem.getnext() is not None and dayItem.getnext().findtext('DayItemType') != 'SectionDayDivider':
                    #     next_business_item_type = dayItem.getnext().find('BusinessItemDetail/BusinessItemType')
                    #     if next_business_item_type is None or (next_business_item_type is not None and next_business_item_type.text != 'Substantive Question'):
                    #         append_fromstring(output_root, '<MotionText>Afterwards&#8233;</MotionText>')


                if business_item_type is not None and business_item_type.text in ('Motion', 'Legislation'):
                    # legistation and motion types appear differently if they are in business today
                    if last_gray_heading_text == 'BUSINESS OF THE DAY' and day_item_is_child is False:
                        append_fromstring(output_root, '<BusinessItemHeading>' + title + '&#8233;</BusinessItemHeading>')
                    else:
                        append_fromstring(output_root, '<Bulleted>' + title + '&#8233;</Bulleted>')

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
                    sponsor_ele.tail = u"\u2029"
                    # title without end punctuation
                    title_no_end_punctuation = title
                    if title[-1] == '.':
                        title_no_end_punctuation = title_no_end_punctuation[:-1]
                    # Adjournment Debate type is displayed differently in the chamber vs westminster hall
                    if section_name == 'CHAMBER':
                        adjourn_ele = etree.Element('BusinessListItem')
                        adjourn_ele.text = title_no_end_punctuation + ': '
                        # append_fromstring(output_root, '<BusinessListItem>' + title + ': <PresenterSponsor>' + sponsor_name.text + '</PresenterSponsor>&#8233;</BusinessListItem>')
                    # westminster hall
                    elif section_name == 'WESTMINSTER HALL':
                        adjourn_ele = etree.Element('WHItemTiming')
                        adjourn_ele.text = format_time(dayItem.findtext('BusinessItemDetail/Time', default='')) + '\t' + title_no_end_punctuation + ': '
                        # append_fromstring(output_root, '<WHItemTiming>' + format_time(dayItem.findtext('BusinessItemDetail/Time', default=None)) + '\t' + title_no_end_punctuation + ': <PresenterSponsor>' + sponsor_name.text + '</PresenterSponsor>&#8233;</WHItemTiming>')
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
                    sponsor_ele.tail = u"\u2029"
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
                    append_motion_sponosrs(dayItem, output_root)

                # get the motion text and sponsors. Sponsors are included even when there is no text for PMBs
                if dayItem.findtext('BusinessItemDetail/ItemText', default='') != '':

                    # get the main item text
                    motionText = etree.Element('MotionText')
                    motionText.append(process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))
                    output_root.append(motionText)




                # output_root.append(process_CDATA(dayItem.findtext('BusinessItemDetail/ItemText', default='')))

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
                # end of amendments section

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


    # get the path to input file
    pwd = path.dirname(path.abspath(input_xml))
    # write out the file
    filename = path.basename(input_xml).replace('as-downloaded-', '').split('.')[0]
    filepath = path.join(pwd, filename)
    et = etree.ElementTree(output_root)
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
    for sponsor in dayItem.find('BusinessItemDetail/Sponsors'):
        sponsor_notes = dayItem.findtext('BusinessItemDetail/SponsorNotes')
        if sponsor_notes is not None and sponsor_notes.strip() != '':
            sponosr_note_xml = ',<SponsorNotes>{}</SponsorNotes>'.format(sponsor_notes)
        else:
            sponosr_note_xml = ''

        append_fromstring(append_to,
                          '<MotionSponsor>{}{}&#8233;</MotionSponsor>'
                          .format(sponsor.findtext('Name', default=''), sponosr_note_xml)
                          )


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


# format date
def format_date(datetime_string):
    if isinstance(datetime_string, str) and len(datetime_string.split('-')) == 3:
        remove_time = datetime_string.split('T')[0]
        try:
            date_list = remove_time.split('-')
            # output_date = date.fromtimestamp(datetime_string)
            # print(output_date)
            output_date = date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
            output_date = output_date.strftime('%A %d %B')
            output_date = output_date.replace(' 0', ' ')
        except:
            return None
        return output_date
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
